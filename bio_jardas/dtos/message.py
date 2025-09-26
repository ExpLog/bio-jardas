from pydantic import BaseModel, Field


class UpsertMessageGroupChoice(BaseModel):
    snowflake_id: int
    group_name: str
    weight: float = Field(ge=0.0)
    independent_roll_probability: float = Field(ge=0.0, le=0.1)
    is_channel: bool
    is_user: bool
    updated_by: int
