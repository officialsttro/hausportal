from pydantic import BaseModel


class UserUnitAssignRequest(BaseModel):
    user_id: int
    unit_id: int
    relation_type: str = "TENANT"
