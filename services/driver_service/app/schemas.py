from pydantic import BaseModel
class CreateDriverRequest(BaseModel):
    name: str
