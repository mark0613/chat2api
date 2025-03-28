import random
from datetime import datetime, timedelta

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

import utils.globals as globals
from app import app, templates


def get_token():
    available_tokens = list(set(globals.token_list) - set(globals.error_token_list))
    if available_tokens:
        selected_token = random.choice(available_tokens)
        return selected_token
    return None


@app.get("/login", response_class=HTMLResponse)
async def login_html(request: Request):
    token = get_token()

    if token:
        tomorrow = datetime.now() + timedelta(days=1)
        expires = tomorrow.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("token", value=get_token(), expires=expires)
    else:
        response = templates.TemplateResponse("login.html", {"request": request})

    return response
