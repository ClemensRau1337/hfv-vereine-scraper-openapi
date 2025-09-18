from pydantic import AnyUrl, BaseModel


class Address(BaseModel):
    full: str
    street: str | None = None
    postcode: str | None = None
    city: str | None = None


class Verein(BaseModel):
    id: str
    name: str
    url: AnyUrl | None = None
    address: Address | None = None
    phone: str | None = None
    email: str | None = None
    website: AnyUrl | None = None


class VereinListItem(BaseModel):
    id: str
    name: str
    url: AnyUrl | None = None
