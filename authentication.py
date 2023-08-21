from fastapi.exceptions import HTTPException
import jwt
from passlib.context import CryptContext
from dotenv import dotenv_values
from models import User
from fastapi import status


config_creds = dotenv_values(".env")

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password):
    return password_context.hash(password)


async def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, config_creds['SECRET'], algorithms=['HS256'])
        user = await User.get(id=payload.get("id"))

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW.Authenticate": "Bearer"}
        )

    return user


async def verify_user(password: str, hashed_password: str):
    return password_context.verify(password, hashed_password)


async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)

    if user and verify_user(password, user.password):
        return user
    return False


async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username or password is invalid",
            headers={"WWW.authenticate": "Bearer"}
        )

    token_data = {
        "id": user.id,
        "username": user.username
    }

    token = jwt.encode(token_data, config_creds['SECRET'])

    return token
