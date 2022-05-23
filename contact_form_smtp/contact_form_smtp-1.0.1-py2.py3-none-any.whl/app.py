# contactform app

import datetime
from smtplib import SMTP

from fastapi import FastAPI, Request

from .settings import SMTP_SERVER

app = FastAPI()


@app.post("/contact/send")
async def post_contact_send(request: Request, status_code=201):
    message = await request.json()
    from_addr = message["From"]
    to_addr = message["To"]
    subject = message["Subject"]
    body = message["HtmlBody"]

    body = body.replace("<div>", "")
    body = body.replace("</div>", "\n\n")
    message_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    with SMTP(SMTP_SERVER) as smtp:
        smtp.set_debuglevel(1)
        msg = (
            f"From: {from_addr}\n"
            f"To: {to_addr}\n"
            f"Subject: {subject}\n"
            f"Date: {message_date}\n"
            "\n"
            f"{body}"
        )
        smtp.sendmail(from_addr, to_addr, msg)
