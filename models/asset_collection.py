from pydantic import BaseModel

from models.scene_asset import (
    SceneAsset
)


class AssetCollection(
    BaseModel
):

    assets: list[SceneAsset]