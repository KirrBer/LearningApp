from pydantic import BaseModel, Field

class TextRequest(BaseModel):
    text: str