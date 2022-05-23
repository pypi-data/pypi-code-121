# contactform app

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/contact/send")
async def post_contact_send(request: Request):
    print(f"{request=}")
    return {"status": "ok"}
