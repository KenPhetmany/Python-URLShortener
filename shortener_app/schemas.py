# states what the API expects as a request body and what the client can expect in the
# response body
from pydantic import BaseModel

# store the URL that the shortened URL forwards to


class URLBase(BaseModel):
    target_url: str

# inherits the target_url from URLBase
# is_active allows to deativate shortened URLs


class URL(URLBase):
    is_active: bool
    clicks: int

# provide configurations to pydantic.
# orm_mode (Object-Relational Mapping) to work with a database model
# provides the convenience of interating with your database
    class Config:
        orm_mode = True

# enhances URL by requiring two strings


class URLInfo(URL):
    url: str
    admin: str
