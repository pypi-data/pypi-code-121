#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : datamodel
# @Time         : 2020/12/2 10:21 上午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None


# Don't do this in production!
@app.post("/user/", response_model=UserIn)
async def create_user(user: UserIn):
    return user


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=9000, debug=True, auto_reload=True)