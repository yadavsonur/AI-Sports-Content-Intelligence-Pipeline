from typing import Optional
from pydantic import BaseModel


class SceneAsset(BaseModel):
    scene_index: int
    original_visual_description: str
    search_query: str
    asset_url: str
    asset_type: str = "image"
    source: str = "wikimedia"
    title: str = ""
    local_path: Optional[str] = ""
    license: Optional[str] = ""
    attribution: Optional[str] = ""
