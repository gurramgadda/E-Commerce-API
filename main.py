from fastapi import FastAPI, Request, HTTPException, status, Depends
import jwt
from tortoise.contrib.fastapi import register_tortoise
from tortoise import models
from models import (User, Business, user_pyd, userIn_pyd,
                    business_pyd, businessIn_pyd)


from authentication import get_hashed_password, verify_token, token_generator
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm)
from dotenv import dotenv_values


# signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import send_email

# response classes
from fastapi.responses import HTMLResponse

# templates
from fastapi.templating import Jinja2Templates


app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
config_creds = dotenv_values(".env")


@app.post("/token")
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_toke": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
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

    return await user


@app.post("/user/me")
async def user_signin(user: userIn_pyd = Depends(get_current_user)):
    business = await Business.get(owner=user)

    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "verified": user.is_verified,
            "joined at": user.joining_date.strftime("%b %d %Y")
        }
    }


@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    updated_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(
            business_name=instance.username,
            owner=instance
        )

        await business_pyd.from_tortoise_orm(business_obj)

    # send email for verification
    await send_email([instance.email], instance)


@app.post("/login")
async def user_login(user: userIn_pyd):
    user_info = user.dict(exclude_unset=True)
    user_info["password"]: get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pyd.from_tortoise_orm(user_obj)
    return {
        "status": "ok",
        "data": f"Hello {new_user.username}"
    }


@app.get("/")
def index():
    return {"user": "started"}


templates = Jinja2Templates(directory="Templates")


@app.get("/verification", response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html",
                                          {"request": request, "username": user.username})

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or Expired Token",
        headers={"WWW.authenticate": "Bearer"}
    )


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
