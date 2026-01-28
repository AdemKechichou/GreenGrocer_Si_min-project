from pydantic import BaseModel , Field

class login(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=100)
# public user model
class ClientRegistration(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(max_length=254)
    address: str = Field(max_length=254)
   
# private user model
class ClientCreation(ClientRegistration):
    type: str = Field(description='Options: administrator, farmer, client' , default='client')

class farmerRegistration(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(max_length=254)
    address: str = Field(max_length=254)
    type: str = Field(default='farmer')

class workerRegistration(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(max_length=254)
    type: str = Field(default='worker')
class ItemCreate(BaseModel):
    profile_id: int | None = None
    title: str = Field(max_length=254)
    qty: int
    price: float

class Item(BaseModel):
    item_id: int | None = None
    profile_id: int | None
    title: str = Field(max_length=254)
    qty: int
    price: float

class ItemEdit(BaseModel):
    id: int | None = None
    title: str | None = Field(default=None , max_length=254)
    qty: int| None = None
    price: float| None= None

class ItemOrder(BaseModel):
    item_id: int
    farmer_id: int |None = None
    qty: int


class FarmerProfile(BaseModel):
    user_id: int | None = None
    name: str | None = Field(default=None ,max_length=100) 
    address: str | None = Field(default=None ,max_length=254)

class Password(BaseModel):
    current: str = Field(min_length=8) 
    new: str = Field(min_length=8) 

class UserEdit(BaseModel):
    email: str = Field(max_length=254)
    name: str = Field(max_length=254)
    address: str = Field(max_length=254)