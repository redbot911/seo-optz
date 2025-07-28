# backend/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext # type: ignore

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage for demo purposes (replace with DB in production)
users_db = {}

class User(BaseModel):
    email: EmailStr
    password: str

class UserInDB(User):
    hashed_password: str

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

@router.post("/signup")
def signup(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = hash_password(user.password)
    users_db[user.email] = {"email": user.email, "hashed_password": hashed}
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: User):
    db_user = users_db.get(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
