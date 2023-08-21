from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=100, null=False, unique=True)
    email = fields.CharField(max_length=200, null=False, unique=True)
    password = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)
    joining_date = fields.DatetimeField(default=datetime.utcnow)


class Business(Model):
    id = fields.IntField(pk=True, index=True)
    business_name = fields.CharField(max_length=100, null=False, unique=True)
    city = fields.CharField(max_length=100, null=False, default='unspecified')
    region = fields.CharField(max_length=100, null=False, default='unspecified')
    description = fields.CharField(max_length=500, null=True)
    logo = fields.CharField(max_length=200, default='businessDefault.jpg')
    owner = fields.ForeignKeyField("models.User", related_name='business')

class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, null=False, index=True)
    category = fields.CharField(max_length=30, index=True)
    original_price = fields.DecimalField(max_digits=10, decimal_places=2)
    new_price = fields.DecimalField(max_digits=10, decimal_places=2)
    percentage_discount = fields.IntField()
    offer_expiries_on = fields.DatetimeField(default=datetime.utcnow)
    product_image = fields.CharField(max_length=200, default="productDefault.jpg")
    business = fields.ForeignKeyField("models.Business", related_name='product')

user_pyd = pydantic_model_creator(User, name="User", exclude=("is_verified", ))
userIn_pyd = pydantic_model_creator(User, name="UserIn", exclude_readonly=True, exclude=("is_verified", "joining_date"))
userOut_pyd = pydantic_model_creator(User, name="UserOut", exclude=("password", ))

business_pyd = pydantic_model_creator(Business, name="Business")
businessIn_pyd = pydantic_model_creator(Business, name="BusinessIn", exclude_readonly=True)

product_pyd = pydantic_model_creator(Product, name="Product")
productIn_pyd = pydantic_model_creator(Product, name="ProductIn", exclude=("percentage_discount", "id"))
