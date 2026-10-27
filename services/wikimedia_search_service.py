import os
import re
import urllib.parse
import requests
from configs.settings import DEFAULT_TIMEOUT
from interfaces.image_search_provider import ImageSearchProvider


class WikimediaSearchService(ImageSearchProvider):

    API_URL = "https://commons.wikimedia.org/w/api.php"
    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
    BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    def __init__(self, download_dir: str = None, timeout: int = DEFAULT_TIMEOUT):
        self.download_dir = download_dir or os.path.abspath("assets/downloads")
        os.makedirs(self.download_dir, exist_ok=True)
        self.timeout = timeout
        self.headers = {
            "User-Agent": self.BROWSER_UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    def search(self, query: str) -> dict:
        """
        Searches Wikimedia Commons for public domain or Creative Commons imagery,
        downloads a web-sized raster thumbnail locally, and preserves licensing metadata.
        """
        clean_query = query.strip()
        fallback_data = self._get_fallback_asset(clean_query)

        try:
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": clean_query,
                "gsrnamespace": 6,  # File namespace
                "gsrlimit": 8,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 1280,
                "format": "json"
            }

            response = requests.get(
                self.API_URL,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code != 200:
                print(f"[WikimediaSearchService] Warning: Status {response.status_code} for '{clean_query}'. Using fallback.")
                return fallback_data

            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            if not pages:
                # Try broader search (first 3 words)
                broader_query = " ".join(clean_query.split()[:3])
                if broader_query != clean_query:
                    params["gsrsearch"] = broader_query
                    resp2 = requests.get(self.API_URL, params=params, headers=self.headers, timeout=self.timeout)
                    if resp2.status_code == 200:
                        pages = resp2.json().get("query", {}).get("pages", {})

            chosen_url = None
            chosen_title = "Wikimedia Image"
            chosen_license = "CC / Public Domain"
            chosen_attribution = "Wikimedia Commons"

            for page_id, page_info in pages.items():
                image_info_list = page_info.get("imageinfo", [])
                if not image_info_list:
                    continue
                info = image_info_list[0]
                # Prefer thumbnail URL (web-optimized) over giant 20MB raw file
                remote_url = info.get("thumburl") or info.get("url", "")

                url_path = urllib.parse.urlparse(remote_url).path.lower()
                if any(url_path.endswith(ext) for ext in self.VALID_EXTENSIONS):
                    chosen_url = remote_url
                    chosen_title = page_info.get("title", "Wikimedia Image")
                    meta = info.get("extmetadata", {})
                    chosen_license = meta.get("LicenseShortName", {}).get("value", "CC / Public Domain")
                    artist = meta.get("Artist", {}).get("value", "")
                    clean_artist = re.sub(r"<[^>]+>", "", artist).strip()
                    credit = meta.get("Credit", {}).get("value", "")
                    clean_credit = re.sub(r"<[^>]+>", "", credit).strip()
                    chosen_attribution = clean_artist or clean_credit or "Wikimedia Commons"
                    break

            if not chosen_url:
                print(f"[WikimediaSearchService] No raster image found for '{clean_query}'. Using fallback.")
                return fallback_data

            # Download the thumbnail image locally
            local_path = self._download_image(chosen_url, clean_query)
            if not local_path or not os.path.exists(local_path):
                return fallback_data

            return {
                "query": clean_query,
                "asset_url": chosen_url,
                "local_path": local_path,
                "asset_type": "image",
                "source": "wikimedia",
                "title": chosen_title,
                "license": chosen_license,
                "attribution": chosen_attribution
            }

        except Exception as e:
            print(f"[WikimediaSearchService] Search error for '{clean_query}': {e}. Using fallback.")
            return fallback_data

    def _download_image(self, url: str, query_slug: str) -> str:
        try:
            safe_slug = re.sub(r"[^\w\-]", "_", query_slug)[:40]
            parsed_path = urllib.parse.urlparse(url).path
            ext = os.path.splitext(parsed_path)[1]
            if not ext or ext.lower() not in self.VALID_EXTENSIONS:
                ext = ".jpg"
            filename = f"wiki_{safe_slug}_{abs(hash(url)) % 10000}{ext}"
            target_path = os.path.join(self.download_dir, filename)

            if os.path.exists(target_path) and os.path.getsize(target_path) > 1024:
                return target_path

            resp = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True)
            if resp.status_code == 200:
                with open(target_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                if os.path.exists(target_path) and os.path.getsize(target_path) > 500:
                    return target_path
            else:
                print(f"[WikimediaSearchService] Download returned status {resp.status_code} for {url}")
        except Exception as e:
            print(f"[WikimediaSearchService] Failed to download {url}: {e}")
        return ""

    def _get_fallback_asset(self, query: str) -> dict:
        candidates = [
            os.path.abspath("assets/image1.jpg"),
            os.path.abspath("assets/image2.jpg"),
            os.path.abspath("assets/image3.jpg"),
            os.path.abspath("assets/aad.jpg"),
        ]
        chosen = next((c for c in candidates if os.path.exists(c)), "")

        return {
            "query": query,
            "asset_url": chosen or "local_fixture",
            "local_path": chosen,
            "asset_type": "image",
            "source": "local_fallback",
            "title": f"Local Asset: {query}",
            "license": "Local Work / Public Domain",
            "attribution": "Project Archive"
        }
