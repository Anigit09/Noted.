from pydantic import BaseModel

class User(BaseModel):
    id:int|None = None
    email:str
class RegIn(User):
    password:str