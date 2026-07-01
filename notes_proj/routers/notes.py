from fastapi import APIRouter,HTTPException,status,Depends
from fastapi.responses import PlainTextResponse
from notes_proj.models.notes import getIN,getOUT,postIN,postOUT,patchIN,queryparams,linkIn
from notes_proj.database import database,note_table
from notes_proj.models.user import User
from notes_proj.auth import get_current_user,create_shared_token,get_shared_edit
from typing import Annotated
from math import ceil
from sqlalchemy import select,func,and_
from datetime import date
router=APIRouter()
@router.post("/notes",response_model=postOUT)
async def publish(note:postIN,current_user:Annotated[User,Depends(get_current_user)]):
    data={**note.model_dump(),"user_id":current_user.id,"doc":date.today()}
    try:
        query=note_table.insert().values(title=data['title'],body=data['body'],user_id=data['user_id'],doc=data['doc'])
        id=await database.execute(query)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="note titles must be unique")
    data={**data,"id":id}
    return data
@router.get("/notes")
async def recieveall(params:queryparams=Depends(),current_user:User=Depends(get_current_user)):
    #lets try manual pagination here , we know pagination is the process of sending chunks of response data rather than the entire data in the form of pages where in each page will have a list of items/resources we would send for a get request
    #we are writing this generally on a get request that tries to acess all the resources and not sepcific ones 
    off=(params.page-1)*params.limit
    query=note_table.select().where(note_table.c.user_id==current_user.id).limit(params.limit).offset(off).order_by(note_table.c.doc)
    query2=select(func.count()).select_from(note_table).where(note_table.c.user_id==current_user.id)
    records=await database.fetch_val(query2)
    return {"data":await database.fetch_all(query),"page":params.page,"total":records,"total pages":ceil(records/params.limit)}
@router.get("/notes/{id}",response_model=getOUT)
async def recieve(id:int,current_user:Annotated[User,Depends(get_current_user)]):
    query=note_table.select().where(and_(note_table.c.id==id , note_table.c.user_id==current_user.id))
    response=await database.fetch_one(query)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="note not found")
    return response
@router.patch("/notes")
async def modify(note:patchIN,current_user:Annotated[User,Depends(get_current_user)]):
    data=note.model_dump(exclude_unset=True) #all the values in the pydantic model that are optional and not sent by the client or sent as null will be ignored and not unpacked as say title:Null
    note_id=data.pop('id') #as we arent explicitly setting the key value like body=data['body'] and we just pass in the dict to the values for automatic kwargs matching so it includes id hence it tries to set id we dont want that as id is aldready existing and need not be changed hence pop it out
    q=note_table.select().where(and_(note_table.c.id==note_id,note_table.c.user_id==current_user.id))
    n=await database.fetch_one(q)
    if n is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="note not found")
    query=note_table.update().where(note_table.c.id==note_id).values(**data)
    response=await database.execute(query)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="note not found")
    return {"message":"note updated"}
@router.delete("/notes")
async def remove(note:getIN,current_user:Annotated[User,Depends(get_current_user)]):
    data=note.model_dump()
    query=note_table.delete().where(and_(note_table.c.id==data['id'],note_table.c.user_id==current_user.id))
    await database.execute(query)
    return {"message":"note deleted"}
@router.post("/notes/{id}/share") #why post when i am technically trying to fetch a sharable link? as we are creating / posting a new resource in the from of the link
async def linkgen(perms:linkIn,id:int):
    data=perms.model_dump()
    token=await create_shared_token(data['edit'])
    print(token)
    url=f"https://noted-tfej.onrender.com/notes/{id}/shared/{token}"
    return PlainTextResponse(url)
@router.get("/notes/{id}/shared/{token}")
async def acess(id:int,token:str):
    print(token)
    await get_shared_edit(token,"shared") #i just want to make sure that the user dosent pass the acess token in the place of shared in the link
    query=note_table.select().where(note_table.c.id==id)
    note=await database.fetch_one(query)
    return note
@router.patch("/notes/{id}/shared/{token}")
async def editing(id:int,token:str,note:patchIN):
    edit=await get_shared_edit(token,"shared")
    if not edit:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="edit permissions not given")
    data=note.model_dump(exclude_unset=True) #all the values in the pydantic model that are optional and not sent by the client or sent as null will be ignored and not unpacked as say title:Null
    note_id=data.pop('id') #as we arent explicitly setting the key value like body=data['body'] and we just pass in the dict to the values for automatic kwargs matching so it includes id hence it tries to set id we dont want that as id is aldready existing and need not be changed hence pop it out
    q=note_table.select().where(note_table.c.id==id)
    n=await database.fetch_one(q)
    if n is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="note not found")
    query=note_table.update().where(note_table.c.id==note_id).values(**data)
    response=await database.execute(query)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="note not found")
    return {"message":"note updated"}

