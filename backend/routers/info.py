from fastapi import APIRouter, Depends, HTTPException, status
from models import PersonalInfo, User
from database import get_database
from .auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/submit", response_model=dict)
async def submit_personal_info(
    info: PersonalInfo, 
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Submit personal information (Name, Age, Bank, Aadhaar, Phone, Income).
    Stores in 'info' collection.
    """
    try:
        email = current_user.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch actual user to get ID
        user_doc = await db["users"].find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user_doc["_id"])
        
        print(f"Submitting info for user: {user_id}")

        # Link to current user
        info.user_id = user_id
        info.created_at = datetime.utcnow()
        
        # Convert to dict
        info_dict = info.model_dump(by_alias=True)
        # Remove _id if it's None so Mongo generates it
        if info_dict.get("_id") is None:
            info_dict.pop("_id", None)
        
        # Insert into MongoDB
        new_info = await db["info"].insert_one(info_dict)
        
        return {
            "message": "Personal information submitted successfully",
            "id": str(new_info.inserted_id)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error submitting info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=dict)
async def get_my_info(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Fetch the personal information for the logged-in user.
    """
    try:
        email = current_user.get("sub")
        user_doc = await db["users"].find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user_doc["_id"])
        
        # Find latest info
        info_doc = await db["info"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
        
        if not info_doc:
            # Return empty if not found, distinct from 404 error
            return {}
            
        return info_doc
    except Exception as e:
        print(f"Error fetching info: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
