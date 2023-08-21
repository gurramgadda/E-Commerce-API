from fastapi import (BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from models import User
import jwt

config_creds = dotenv_values(".env")

config = ConnectionConfig(
    MAIL_USERNAME=config_creds['EMAIL'],
    MAIL_PASSWORD=config_creds['PASSWORD'],
    MAIL_FROM=config_creds['EMAIL'],
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_email(email: List, instance: User):

    token_data = {
        "id": instance.id,
        "username": instance.username
    }

    token = jwt.encode(token_data, config_creds['SECRET'], algorithm='HS256')

    template = f"""
        <!DOCTYPE html>
        <html>
            <head>
            </head>
            <body>
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <h2> Email Verification</h2>
                    <p>
                        Welcome to Market Add. Please Click the below Verify Button to Verify your Email
                    </p>
                    <a style="margin: 1rem 0; padding: 1rem; background: #0275d8; border-radius:0.5rem; 
                    font-size: 1rem; text-decoration: none; color: white" href="http://localhost:8000/verification?token={token}">
                        Verify Your Email
                    </a>
                    <p> kindly ignore this email if not initiated. Thank You</p>
                </div>
            </body>
        </html>
    """

    message = MessageSchema(
        subject="Market ADD Account Verification Mail",
        recipients=email,
        body=template,
        subtype="html" 
    )

    fm = FastMail(config)
    await fm.send_message(message=message)

