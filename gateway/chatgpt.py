import json
import urllib.parse
from urllib.parse import quote

from fastapi import Request, Depends
from fastapi.responses import HTMLResponse

from app import app, templates
from apps.user.views import login_page
from utils.kv_utils import set_value_for_key_list
from utils.database import get_db
from apps.token.operations import get_available_token

with open("templates/chatgpt_context_1.json", "r", encoding="utf-8") as f:
    chatgpt_context_1 = json.load(f)
with open("templates/chatgpt_context_2.json", "r", encoding="utf-8") as f:
    chatgpt_context_2 = json.load(f)


@app.get("/", response_class=HTMLResponse)
async def chatgpt_html(request: Request, db=Depends(get_db)):
    # 獲取一個可用的 token，優先選擇 access_token
    token = get_available_token(db, threshold=60*60, prefer_access_token=True)
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/token_error", status_code=302)
    if len(token) != 45 and not token.startswith("eyJhbGciOi"):
        token = quote(token)

    user_chatgpt_context_1 = chatgpt_context_1.copy()
    user_chatgpt_context_2 = chatgpt_context_2.copy()

    set_value_for_key_list(user_chatgpt_context_1, "accessToken", token)
    if request.cookies.get("oai-locale"):
        set_value_for_key_list(user_chatgpt_context_1, "locale", request.cookies.get("oai-locale"))
    else:
        accept_language = request.headers.get("accept-language")
        if accept_language:
            set_value_for_key_list(user_chatgpt_context_1, "locale", accept_language.split(",")[0])

    user_chatgpt_context_1 = json.dumps(user_chatgpt_context_1, separators=(',', ':'), ensure_ascii=False)
    user_chatgpt_context_2 = json.dumps(user_chatgpt_context_2, separators=(',', ':'), ensure_ascii=False)

    escaped_context_1 = user_chatgpt_context_1.replace("\\", "\\\\").replace('"', '\\"')
    escaped_context_2 = user_chatgpt_context_2.replace("\\", "\\\\").replace('"', '\\"')

    clear_localstorage_script = """
    <script>
        localStorage.clear();
    </script>
    """

    return templates.TemplateResponse("chatgpt.html", {
        "request": request,
        "react_chatgpt_context_1": escaped_context_1,
        "react_chatgpt_context_2": escaped_context_2,
        "clear_localstorage_script": clear_localstorage_script
    })
