from models.scene_asset import (
    SceneAsset
)

from models.asset_collection import (
    AssetCollection
)

from services.wikimedia_search_service import (
    WikimediaSearchService
)


class AssetCollectorAgent:

    def __init__(
        self,
        image_search_service=None
    ):

        self.image_search = (
            image_search_service
            or WikimediaSearchService()
        )

    def execute(
        self,
        video_plan
    ):

        assets = []

        for index, scene in enumerate(
            video_plan.scenes
        ):

            search_query = (
                self._normalize_query(
                    scene.visual_description
                )
            )

            result = (
                self.image_search.search(
                    search_query
                )
            )

            asset = SceneAsset(
                scene_index=index,

                original_visual_description=
                scene.visual_description,

                search_query=
                search_query,

                asset_url=
                result["asset_url"],

                asset_type=
                result["asset_type"]
            )

            assets.append(asset)

        return AssetCollection(
            assets=assets
        )

    def _normalize_query(
        self,
        visual_description
    ):

        query = (
            visual_description
            .lower()
            .strip()
        )

        replacements = {
            "aerial view of": "",
            "close-up of": "",
            "montage of": "",
            "rapid succession of": "",
            "focus on": "",
        }

        for old, new in (
            replacements.items()
        ):
            query = query.replace(
                old,
                new
            )

        return (
            " ".join(
                query.split()
            )
        )