from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import os
load_dotenv()

app       = FastAPI()
templates = Jinja2Templates(directory="templates")

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI         = os.getenv("GOOGLE_REDIRECT_URI")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
def login():
    google_url = "https://accounts.google.com/o/oauth2/v2/auth"
    url = (
        f"{google_url}?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
    )
    return RedirectResponse(url)

# Google 回傳授權碼後的處理
@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("登入失敗：沒有取得授權碼", status_code=400)

    
    # 使用 code 換取 access_token
    token_url  = "https://oauth2.googleapis.com/token"
    token_data = {
        "code"         : code,
        "client_id"    : GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri" : REDIRECT_URI,
        "grant_type"   : "authorization_code"
    }
    token_res    = requests.post(token_url, data=token_data).json()
    access_token = token_res.get("access_token")

    # 使用 access_token 拿使用者資訊
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers      = {"Authorization": f"Bearer {access_token}"}
    userinfo     = requests.get(userinfo_url, headers=headers).json()

    return templates.TemplateResponse("success.html", {
        "request": request,
        "name"   : userinfo.get("name"),
        "email"  : userinfo.get("email"),
        "picture": userinfo.get("picture")
    })
