from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from database import get_database
from models import Scheme, SchemeCreate, User
from routers.auth import get_current_user
from ai_engine import ai_engine

router = APIRouter()

@router.post("/", response_model=Scheme)
async def create_scheme(scheme: SchemeCreate, current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    # Check if admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    scheme_dict = scheme.dict()
    # Optional: Pre-generate translations or simplified text here using ai_engine
    
    new_scheme = await db["schemes"].insert_one(scheme_dict)
    created_scheme = await db["schemes"].find_one({"_id": new_scheme.inserted_id})
    return Scheme(**created_scheme)

@router.get("/", response_model=List[Scheme])
async def list_schemes(language: Optional[str] = "en", db = Depends(get_database)):
    schemes = await db["schemes"].find().to_list(1000)
    
    # Apply translation if requested
    if language != "en":
        # in a real scenario, we'd use ai_engine.translate_content here or fetch pre-translated fields
        # schemes = [await ai_engine.translate_content(s, language) for s in schemes]
        pass
        
    return [Scheme(**s) for s in schemes]

@router.get("/{scheme_id}", response_model=Scheme)
async def get_scheme(scheme_id: str, db = Depends(get_database)):
    print(f"DEBUG: Fetching scheme with ID: {scheme_id}")
    
    # 1. Try exact string match
    scheme = await db["schemes"].find_one({"_id": scheme_id})
    if scheme:
        print("DEBUG: Found by string ID")
        return Scheme(**scheme)

    # 2. Try ObjectId match
    from bson import ObjectId
    if ObjectId.is_valid(scheme_id):
        try:
            obj_id = ObjectId(scheme_id)
            scheme = await db["schemes"].find_one({"_id": obj_id})
            if scheme:
                print("DEBUG: Found by ObjectId")
                return Scheme(**scheme)
        except Exception as e:
            print(f"DEBUG: ObjectId conversion error: {e}")

    print("DEBUG: Scheme not found")
    raise HTTPException(status_code=404, detail="Scheme not found")
