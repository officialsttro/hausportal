from pydantic import BaseModel


class PropertyCreateRequest(BaseModel):
    name: str
    street: str
    postal_code: str
    city: str


class PropertyResponse(BaseModel):
    id: int
    name: str
    street: str
    postal_code: str
    city: str

    class Config:
        from_attributes = True
