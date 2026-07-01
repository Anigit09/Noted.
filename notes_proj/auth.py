from passlib.context import CryptContext
from Notes.notes_proj.database import user_table,note_table,database
from typing import Annotated
from jose import JWTError,jwt,ExpiredSignatureError
from fastapi import HTTPException,status
from Notes.notes_proj.config import config
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
import datetime
from fastapi_mail import ConnectionConfig,MessageSchema
from fastapi_mail.fastmail import FastMail
from typing import Literal
pwdcontext=CryptContext(schemes=['argon2'],deprecated="auto")
oauth=OAuth2PasswordBearer(tokenUrl="token")
ALGORITHM="HS256"
def password_hash(password:str):
    return pwdcontext.hash(password)
def verify(hashpassword:str,confpassword:str):
    return pwdcontext.verify(confpassword,hashpassword)
async def get_user(email:str):
    query=user_table.select().where(user_table.c.email==email)
    response=await database.fetch_one(query)
    if response:
        return response         

async def create_token(email:str,type:str):
    expiry=datetime.datetime.now(datetime.UTC)+datetime.timedelta(minutes=30)
    jwt_date={"sub":email,"exp":expiry,"type":type}
    encoded_jwt=jwt.encode(jwt_date,config.SECRET_KEY,ALGORITHM)
    return encoded_jwt
async def create_shared_token(edit:bool):
    exp_time=datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=24)
    jwt_data={"edit":edit,"exp":exp_time,"type":"shared"}
    encoded_jwt=jwt.encode(jwt_data,config.SECRET_KEY,ALGORITHM)
    return encoded_jwt

async def authenticate_user(email:str,password:str): #to be used when user is logging in and re-types his details post registering
    response=await get_user(email=email)
    if response is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not registered") #try to be as vauge as possible in writing error messages during auth flow due to security risks
    if not verify(response.password,password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="pls try again")
    if not response.isConfirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="email not confirmed pls confirm and try again")

    return response
async def get_subject(token:str,type=Literal["acess","shared","Confirmation"]):
    try:
        payload=jwt.decode(token,config.SECRET_KEY,ALGORITHM) 
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect token")
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="expired token")
    Type=payload.get("type")
    if Type is None or Type!=type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="wrong token type")
    subject=payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="token missing the sub field")
    return subject
async def get_shared_edit(token:str,type=Literal["acess","shared","Confirmation"]):
    try:
        payload=jwt.decode(token,config.SECRET_KEY,ALGORITHM)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect token")
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="expired token")
    Type=payload.get("type")
    if Type is None or Type!=type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="wrong token type")
    edit=payload.get("edit")
    if edit is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="missing edit feild")
    return edit
async def get_current_user(token:Annotated[str,Depends(oauth)]): #this is for subsequent requests after sucessful login when endpoint returns the acess token and it is sent back to the server
    email=await get_subject(token,"acess")
    response=await get_user(email)
    if response is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not found")
    return response
conf = ConnectionConfig(

    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.APP_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,

    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,

    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
)
async def send_confirmation_email(email:str,conf_url:str):
    message=MessageSchema(
        subject="verification of email",
        recipients=[email],
        body=f""" Hello there! Click the link to verify your account {conf_url}""",
        subtype="plain"
    )
    fm=FastMail(conf)
    await fm.send_message(message)