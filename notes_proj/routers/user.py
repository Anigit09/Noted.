from notes_proj.auth import get_current_user,authenticate_user,password_hash,create_token,get_user,send_confirmation_email,get_subject
from notes_proj.database import database,user_table
from fastapi import HTTPException,status
from typing import Annotated
from fastapi import APIRouter,BackgroundTasks,Request
from notes_proj.models.user import RegIn
router=APIRouter()
@router.post("/register")
async def register(user:RegIn,request:Request,background_tasks:BackgroundTasks):
    data=user.model_dump()
    if await get_user(data['email']) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user aldready exists")
    hash=password_hash(data['password'])
    query=user_table.insert().values(email=data['email'],password=hash)
    await database.execute(query)
    conf_token=await create_token(data['email'],"Confirmation")
    conf_url=f"{str(request.base_url).rstrip('/')}#/confirm/{conf_token}"
    background_tasks.add_task(send_confirmation_email,email=data['email'],conf_url=conf_url)
    return {"message":"registered sucessfully , pls check your mail for confirmation url"}
@router.post("/login")
async def login(user:RegIn):
    data=user.model_dump()
    record=await authenticate_user(data['email'],data['password'])
    token=await create_token(record.email,"acess")
    return {"acess_token":token,"token_type":"bearer"}
@router.get("/confirm/{conf_token}")
async def confirm(conf_token:str):
    email=await get_subject(conf_token,"Confirmation")
    query=user_table.update().where(user_table.c.email==email).values(isConfirmed=True)
    await database.execute(query)
    return {"message":"user confirmed sucessfully you can go back to log-in page"}
