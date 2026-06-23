from pydantic import BaseModel


class MatchEvent(BaseModel):

    home_team: str
    away_team: str

    home_score: int
    away_score: int

    competition: str

    narrative: str