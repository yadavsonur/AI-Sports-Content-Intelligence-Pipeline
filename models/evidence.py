from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source: str
    content: str
    url: Optional[str] = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
