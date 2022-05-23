# contactform app

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/contact/send")
async def post_contact_send(request: Request):
    print(f"{request=}")
    form_data = await request.form()
    print(f"{form_data=}")
    json_data = await request.json()
    print(f"{json_data=}")
    return {"status": "ok"}
