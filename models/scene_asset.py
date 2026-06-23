from pydantic import BaseModel


class SceneAsset(BaseModel):

    scene_index: int

    original_visual_description: str

    search_query: str

    asset_url: str

    asset_type: str

    source: str

    title: str