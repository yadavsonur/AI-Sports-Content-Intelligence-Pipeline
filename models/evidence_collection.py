from pydantic import BaseModel

from models.evidence import Evidence


class EvidenceCollection(BaseModel):

    evidence: list[Evidence]