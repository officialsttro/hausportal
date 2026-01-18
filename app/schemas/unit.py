from pydantic import BaseModel


class UnitCreateRequest(BaseModel):
    label: str


class UnitResponse(BaseModel):
    id: int
    property_id: int
    label: str

    class Config:
        from_attributes = True
