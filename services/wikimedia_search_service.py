import requests

from interfaces.image_search_provider import (
    ImageSearchProvider
)


class WikimediaSearchService(
    ImageSearchProvider
):

    def search(
        self,
        query
    ):

        url = (
            "https://commons.wikimedia.org/w/api.php"
        )

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        pages = (
            data.get("query", {})
            .get("pages", {})
        )

        if not pages:

            return {
                "query": query,
                "asset_url": "",
                "asset_type": "image",
                "source": "wikimedia",
                "title": "not_found"
            }

        first_page = next(
            iter(pages.values())
        )

        image_url = (
            first_page
            .get("imageinfo", [{}])[0]
            .get("url", "")
        )

        return {
            "query": query,
            "asset_url": image_url,
            "asset_type": "image",
            "source": "wikimedia",
            "title": first_page.get(
                "title",
                ""
            )
        }