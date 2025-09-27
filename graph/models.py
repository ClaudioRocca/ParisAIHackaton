from pydantic import BaseModel
from typing import Optional, Any, List

class ToolInfo(BaseModel):
    name: str
    arguments: dict
    output: Optional[Any]
    error: bool