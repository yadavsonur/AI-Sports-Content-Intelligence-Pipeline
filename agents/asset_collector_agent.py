import re
from models.scene_asset import SceneAsset
from models.asset_collection import AssetCollection
from services.wikimedia_search_service import WikimediaSearchService


class AssetCollectorAgent:

    def __init__(self, image_search_service=None):
        self.image_search = image_search_service or WikimediaSearchService()

    def execute(self, video_plan) -> AssetCollection:
        assets = []

        for index, scene in enumerate(video_plan.scenes):
            search_query = self._normalize_query(scene.visual_description)
            result = self.image_search.search(search_query)

            asset = SceneAsset(
                scene_index=index,
                original_visual_description=scene.visual_description,
                search_query=search_query,
                asset_url=result.get("asset_url", ""),
                local_path=result.get("local_path", ""),
                asset_type=result.get("asset_type", "image"),
                source=result.get("source", "wikimedia"),
                title=result.get("title", ""),
                license=result.get("license", "CC/PD"),
                attribution=result.get("attribution", "")
            )
            assets.append(asset)

        return AssetCollection(assets=assets)

    def _normalize_query(self, visual_description: str) -> str:
        query = visual_description.lower().strip()

        # Remove cinematic instruction prefixes that confuse search engines
        prefixes = [
            "aerial view of",
            "close-up of",
            "close up of",
            "montage of",
            "rapid succession of",
            "focus on",
            "photo of",
            "picture of",
            "wide shot of",
            "dramatic shot of",
            "slow motion of",
        ]

        for p in prefixes:
            if query.startswith(p):
                query = query[len(p):].strip()

        # Remove quotes, parentheses, special characters
        query = re.sub(r"[\"\'\(\)\[\]\{\}]", "", query)
        query = " ".join(query.split())

        # If too long, take the first 6 key words
        words = query.split()
        if len(words) > 6:
            query = " ".join(words[:6])

        return query or "football soccer match"
