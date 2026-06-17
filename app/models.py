from typing import Optional, Union

from pydantic import BaseModel

class UserQuery(BaseModel):
    query: str
    session_id: Optional[Union[str, int]] = None
