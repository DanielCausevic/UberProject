from pydantic import BaseModel, Field

class CreateDriverRequest(BaseModel):
    name: str = Field(min_length=1)
