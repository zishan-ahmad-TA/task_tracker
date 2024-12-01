from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import requests
import os
from jose import jwt, JWTError
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime, timedelta, timezone
from models import Employee as DBEmployee

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
SECRET_KEY = os.getenv("JWT_SECRET")  
ALGORITHM = "HS256"

auth_router = APIRouter()

@auth_router.get("/login")
async def login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid profile email"
    )
    return RedirectResponse(url=google_auth_url)

@auth_router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch token")

    token_info = token_response.json()
    access_token = token_info.get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    if user_info_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    user_info = user_info_response.json()
    email = user_info.get("email")
    name = user_info.get("name")
    profile_image_url = user_info.get("picture")
    print(profile_image_url)

    if not email or not name:
        raise HTTPException(status_code=400, detail="Incomplete user info from Google")

    user = db.query(DBEmployee).filter(DBEmployee.email_id == email).first()

    if not user:
        new_user = DBEmployee(
            name=name, 
            email_id=email, 
            role="member",
            profile_image_url=profile_image_url
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    jwt_payload = {
        "employee_id": user.employee_id,
        "exp": (datetime.now(timezone.utc) + timedelta(days=1)).timestamp(), 
    }
    jwt_token = jwt.encode(jwt_payload, SECRET_KEY, algorithm=ALGORITHM)

    redirect_response = RedirectResponse(url=f"{FRONTEND_URL}/home")
    redirect_response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        max_age=3600,
        #Enable in Prod
        # secure=True,
        # samesite="Strict"
    )
    return redirect_response

def verify_jwt(request: Request, db: Session = Depends(get_db)):
    # Extract JWT from the access_token cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        # Decode and verify the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token has expired")

        # Fetch user from the database
        user = db.query(DBEmployee).filter(DBEmployee.employee_id == payload.get("employee_id")).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user  
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")