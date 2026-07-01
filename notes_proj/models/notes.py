from pydantic import BaseModel,Field
from fastapi import Query
from typing import Optional
from datetime import date
#these both models will be commonly used for get and delete as both require the same input id in the body of the request
class getIN(BaseModel):
    id:int
class getOUT(getIN):
    title:str
    body:str
    doc:date
class postIN(BaseModel):
    title:str=Field(max_length=50)
    body:str=Field(max_length=300)
class postOUT(getIN):
    title:str
    body:str
class patchIN(BaseModel):
    id:int 
    title:Optional[str]=Field(default=None,max_length=50)
    body:Optional[str]=Field(default=None,max_length=300)
class queryparams(BaseModel):
    page:int=Query(1,ge=1)
    limit:int=Query(3,ge=1,le=5)
class linkIn(BaseModel):
    edit:bool=False
    

