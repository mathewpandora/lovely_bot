from pydantic import BaseModel


class CredentialRead(BaseModel):
    id: int
    password: str

    model_config = {"from_attributes": True}


class CredentialCreate(BaseModel):
    id: int
    password: str
