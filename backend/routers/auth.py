from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from database import get_database
from models import UserCreate, User, UserInDB, Token
from security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from bson import ObjectId
import os
import shutil

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_database)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    """Fetch current user details"""
    email = current_user.get("sub")
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@router.post("/register", response_model=User)
async def register(user: UserCreate, db = Depends(get_database)):
    user_exists = await db["users"].find_one({"email": user.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    new_user = await db["users"].insert_one(user_in_db.dict(by_alias=True))
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    return User(**created_user)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    user = await db["users"].find_one({"email": form_data.username}) # OAuth2 form uses 'username' field for email
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user.get("role", "citizen")},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/profile", response_model=User)
async def update_profile(
    user_update: dict, 
    current_user: dict = Depends(get_current_user), 
    db = Depends(get_database)
):
    """
    Updates the current user's profile with provided fields.
    """
    email = current_user.get("sub")
    
    # Filter only allowed fields to prevent arbitrary updates (like role)
    allowed_fields = {"ward", "occupation", "address", "bank_account_no", "ifsc_code", "full_name", "panchayat"}
    update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
    
    if not update_data:
         raise HTTPException(status_code=400, detail="No valid fields to update")

    result = await db["users"].update_one(
        {"email": email},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
         # Check if user exists just in case
         found_user = await db["users"].find_one({"email": email})
         if not found_user:
             raise HTTPException(status_code=404, detail="User not found")
         # If user exists but nothing changed, we still return the user
    
    updated_user = await db["users"].find_one({"email": email})
    return User(**updated_user)
