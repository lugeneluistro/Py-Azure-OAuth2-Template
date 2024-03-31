from pydantic import BaseModel
from typing import Optional

class UserDTO(BaseModel):
    email: str | None 
    password: str | None 
    first_name: Optional[str] = None 
    last_name: Optional[str] = None
    domain_name: Optional[str] = None 
    business_name: Optional[str] = None 
