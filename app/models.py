from typing import Optional
from pydantic import BaseModel, AnyUrl

class Address(BaseModel):
    full: str
    street: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None

class Verein(BaseModel):
    id: str
    name: str
    url: Optional[AnyUrl] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[AnyUrl] = None

class VereinListItem(BaseModel):
    id: str
    name: str
    url: Optional[AnyUrl] = None
