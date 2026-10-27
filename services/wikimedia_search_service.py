import hashlib
import os
import re
import socket
import threading
import urllib.parse
from contextlib import contextmanager
from html import unescape

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from configs.settings import DEFAULT_TIMEOUT
from interfaces.image_search_provider import ImageSearchProvider


_IPV4_DNS_LOCK = threading.RLock()


@contextmanager
def _force_ipv4_dns():
    """
    Temporarily make Python's socket resolver return IPv4 addresses only.
    Diagnostics showed Commons HTTPS resets over IPv6 but succeeds over IPv4.
    The lock prevents this module's concurrent requests from racing the patch.
    """
    with _IPV4_DNS_LOCK:
        original_getaddrinfo = socket.getaddrinfo

        def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            if family in (0, socket.AF_UNSPEC, socket.AF_INET):
                return original_getaddrinfo(
                    host, port, socket.AF_INET, type, proto, flags
                )
            return original_getaddrinfo(host, port, family, type, proto, flags)

        socket.getaddrinfo = ipv4_getaddrinfo
        try:
            yield
        finally:
            socket.getaddrinfo = original_getaddrinfo


class WikimediaSearchService(ImageSearchProvider):
    """
    Search Wikimedia Commons and download a local, web-sized image.

    Network resilience:
    - retries connection resets/timeouts and transient HTTP errors
    - uses a descriptive User-Agent
    - validates downloaded files before accepting them
    - keeps local fallback behavior if Wikimedia is unreachable
    """

    API_URL = "https://commons.wikimedia.org/w/api.php"
    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

    def __init__(self, download_dir: str = None, timeout: int = DEFAULT_TIMEOUT):
        self.download_dir = os.path.abspath(
            download_dir or os.path.join("assets", "downloads")
        )
        os.makedirs(self.download_dir, exist_ok=True)
        self.timeout = max(5, int(timeout))

        # Wikimedia asks clients to identify their application and provide a
        # contact route. A repository URL is used here instead of a fake email.
        user_agent = os.getenv(
            "WIKIMEDIA_USER_AGENT",
            "WorldCupAgent/1.0 "
            "(https://github.com/yadavsonur/AI-Sports-Content-Intelligence-Pipeline)"
        )

        retry = Retry(
            total=4,
            connect=4,
            read=4,
            status=4,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
            respect_retry_after_header=True,
            raise_on_status=False,
        )

        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.api_headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }
        self.image_headers = {
            "User-Agent": user_agent,
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        }

    def search(self, query: str) -> dict:
        """Search Wikimedia Commons and return a downloaded image plus metadata."""
        clean_query = " ".join((query or "").split()).strip()
        fallback_data = self._get_fallback_asset(clean_query)

        if not clean_query:
            print("[WikimediaSearchService] Empty query; using local fallback.")
            return fallback_data

        queries_to_try = [clean_query]
        broad_query = " ".join(clean_query.split()[:3])
        if broad_query and broad_query.casefold() != clean_query.casefold():
            queries_to_try.append(broad_query)

        try:
            pages = {}
            for candidate_query in queries_to_try:
                params = {
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": candidate_query,
                    "gsrnamespace": 6,
                    "gsrlimit": 10,
                    "prop": "imageinfo",
                    "iiprop": "url|extmetadata",
                    "iiurlwidth": 1280,
                    "format": "json",
                    "formatversion": 2,
                }

                # The user's network resets Wikimedia HTTPS over IPv6, while
                # curl -4 succeeds. Force IPv4 for this request only.
                with _force_ipv4_dns():
                    response = self.session.get(
                        self.API_URL,
                        params=params,
                        headers=self.api_headers,
                        timeout=(5, self.timeout),
                    )
                    response.raise_for_status()
                    payload = response.json()
                pages = payload.get("query", {}).get("pages", [])
                if isinstance(pages, dict):
                    pages = list(pages.values())
                if pages:
                    break

            if not pages:
                print(
                    f"[WikimediaSearchService] No Commons results for "
                    f"'{clean_query}'. Using local fallback."
                )
                return fallback_data

            for page_info in pages:
                image_info_list = page_info.get("imageinfo", [])
                if not image_info_list:
                    continue

                info = image_info_list[0]
                remote_url = info.get("thumburl") or info.get("url") or ""
                if not self._looks_like_supported_image_url(remote_url):
                    continue

                local_path = self._download_image(remote_url, clean_query)
                if not local_path:
                    continue

                metadata = info.get("extmetadata", {})
                license_name = self._metadata_value(
                    metadata, "LicenseShortName", "CC BY-SA / Public Domain"
                )
                artist = self._strip_html(
                    self._metadata_value(metadata, "Artist", "")
                )
                credit = self._strip_html(
                    self._metadata_value(metadata, "Credit", "")
                )

                return {
                    "query": clean_query,
                    "asset_url": remote_url,
                    "local_path": local_path,
                    "asset_type": "image",
                    "source": "wikimedia",
                    "title": page_info.get("title", "Wikimedia Commons image"),
                    "license": license_name,
                    "attribution": artist or credit or "Wikimedia Commons",
                }

            print(
                f"[WikimediaSearchService] Search results had no usable downloadable "
                f"raster images for '{clean_query}'. Using local fallback."
            )
            return fallback_data

        except (requests.RequestException, ValueError) as exc:
            print(
                f"[WikimediaSearchService] Request failed for '{clean_query}' "
                f"after retries: {exc}. Using local fallback."
            )
            return fallback_data
        except Exception as exc:
            print(
                f"[WikimediaSearchService] Unexpected error for '{clean_query}': "
                f"{exc}. Using local fallback."
            )
            return fallback_data

    def _download_image(self, url: str, query_slug: str) -> str:
        """Download to a temporary file and only keep it if it is a real image."""
        try:
            parsed = urllib.parse.urlparse(url)
            ext = os.path.splitext(parsed.path)[1].lower()
            if ext not in self.VALID_EXTENSIONS:
                ext = ".jpg"

            safe_slug = re.sub(r"[^\w-]+", "_", query_slug, flags=re.UNICODE).strip("_")
            safe_slug = (safe_slug[:45] or "commons_image")
            digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
            filename = f"wiki_{safe_slug}_{digest}{ext}"
            target_path = os.path.join(self.download_dir, filename)
            if self._is_valid_image(target_path):
                return target_path

            temp_path = target_path + ".part"
            try:
                with _force_ipv4_dns():
                    with self.session.get(
                        url,
                        headers=self.image_headers,
                        timeout=(5, self.timeout),
                        stream=True,
                    ) as response:
                        response.raise_for_status()
                        content_type = response.headers.get("Content-Type", "").lower()
                        if content_type and not content_type.startswith("image/"):
                            print(
                                f"[WikimediaSearchService] Refusing non-image response "
                                f"({content_type}) for {url}"
                            )
                            return ""

                        with open(temp_path, "wb") as output:
                            for chunk in response.iter_content(chunk_size=64 * 1024):
                                if chunk:
                                    output.write(chunk)

                if self._is_valid_image(temp_path):
                    os.replace(temp_path, target_path)
                    return target_path

                print(f"[WikimediaSearchService] Downloaded file is not a valid image: {url}")
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

        except requests.RequestException as exc:
            print(f"[WikimediaSearchService] Image download failed after retries: {exc}")
        except OSError as exc:
            print(f"[WikimediaSearchService] Could not save image: {exc}")

        return ""

    @staticmethod
    def _is_valid_image(path: str) -> bool:
        if not path or not os.path.isfile(path) or os.path.getsize(path) < 1024:
            return False
        try:
            with Image.open(path) as image:
                image.verify()
            return True
        except Exception:
            return False

    @staticmethod
    def _looks_like_supported_image_url(url: str) -> bool:
        if not url:
            return False
        path = urllib.parse.urlparse(url).path.lower()
        return any(path.endswith(ext) for ext in WikimediaSearchService.VALID_EXTENSIONS)

    @staticmethod
    def _metadata_value(metadata: dict, key: str, default: str) -> str:
        value = metadata.get(key, {})
        if isinstance(value, dict):
            return unescape(str(value.get("value", default)))
        return default

    @staticmethod
    def _strip_html(value: str) -> str:
        return re.sub(r"<[^>]*>", "", unescape(value or "")).strip()

    def _get_fallback_asset(self, query: str) -> dict:
        candidates = [
            os.path.abspath(os.path.join("assets", "image1.jpg")),
            os.path.abspath(os.path.join("assets", "image2.jpg")),
            os.path.abspath(os.path.join("assets", "image3.jpg")),
            os.path.abspath(os.path.join("assets", "aad.jpg")),
        ]
        existing = [path for path in candidates if os.path.isfile(path)]
        chosen = existing[0] if existing else ""

        return {
            "query": query,
            "asset_url": chosen or "local_fixture",
            "local_path": chosen,
            "asset_type": "image",
            "source": "local_fallback",
            "title": f"Local fallback asset: {query}",
            "license": "Local Work / Public Domain",
            "attribution": "Project Archive",
        }
