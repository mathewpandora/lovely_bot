from pydantic import BaseModel


class ValentineCreate(BaseModel):
    text: str
    track_link: str
    recipient_id: int


class ValentineRead(BaseModel):
    id: int
    text: str
    track_link: str
    recipient_id: int

    model_config = {"from_attributes": True}
