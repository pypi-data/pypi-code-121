# contactform app

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/contact/send")
async def post_contact_send(request: Request):
    print(f"{request=}")
    print(f"{request.query_params=}")
    print(f"{request.path_params=}")
    return {"status": "ok"}
