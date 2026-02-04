from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import get_database
from models import User
from routers.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    if current_user["role"] not in ["admin", "official"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    total_citizens = await db["users"].count_documents({"role": "citizen"})
    total_schemes = await db["schemes"].count_documents({})
    # Assuming 'applications' collection exists or will exist.
    total_pending = await db["applications"].count_documents({"status": "pending"}) if "applications" in await db.list_collection_names() else 0
    
    return {
        "total_citizens": total_citizens,
        "total_schemes": total_schemes,
        "total_pending": total_pending
    }

@router.get("/users", response_model=List[User])
async def get_all_users(current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    if current_user["role"] not in ["admin", "official"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    users = await db["users"].find({"role": "citizen"}).to_list(length=100)
    return users

@router.get("/applications/pending")
async def get_pending_applications(current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    if current_user["role"] not in ["admin", "official"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    # Fetch Pending Apps
    applications = await db["applications"].find({"status": "Pending"}).sort("submission_date", -1).to_list(length=50)

    # Manual Join to prevent aggregation errors
    for app in applications:
        app["_id"] = str(app["_id"])
        
        user_id = app.get("user_id")
        applicant_details = {"full_name": "Unknown", "phone_number": "", "age": ""}
        
        if user_id:
            # Try to fetch from Info collection first
            info = await db["info"].find_one({"user_id": user_id})
            if info:
                applicant_details = {
                    "full_name": info.get("full_name", "Unknown"),
                    "age": info.get("age", ""),
                    "phone_number": info.get("phone_number", ""),
                    "aadhaar_no": info.get("aadhaar_no", ""),
                    "bank_account_no": info.get("bank_account_no", ""),
                    "annual_income": info.get("annual_income", "")
                }
            else:
                 # Fallback to User collection
                 try: 
                     from bson import ObjectId
                     user = await db["users"].find_one({"_id": ObjectId(user_id)})
                     if user:
                         applicant_details["full_name"] = user.get("full_name", "Unknown")
                         applicant_details["phone_number"] = user.get("phone_number", "")
                 except: 
                     pass

        # Populate
        app["applicant_details"] = applicant_details

    return applications

@router.post("/verify-application/{app_id}", response_model=dict)
async def verify_application(app_id: str, current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    if current_user["role"] not in ["admin", "official"]:
         raise HTTPException(status_code=403, detail="Unauthorized")

    from bson import ObjectId
    
    # 1. Update Status
    result = await db["applications"].find_one_and_update(
        {"_id": ObjectId(app_id)},
        {"$set": {"status": "Verified", "verified_by": current_user["sub"]}}
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "message": "Application Verified Successfully",
        "status": "Verified"
    } 

@router.post("/reject-application/{app_id}", response_model=dict)
async def reject_application(app_id: str, current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    if current_user["role"] not in ["admin", "official"]:
         raise HTTPException(status_code=403, detail="Unauthorized")

    from bson import ObjectId
    
    # Update Status to Rejected
    result = await db["applications"].find_one_and_update(
        {"_id": ObjectId(app_id)},
        {"$set": {"status": "Rejected", "rejected_by": current_user["sub"]}}
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "message": "Application Rejected",
        "status": "Rejected"
    } 

@router.delete("/applications/pending", response_model=dict)
async def delete_all_applications(current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    if current_user["role"] not in ["admin", "official"]:
         raise HTTPException(status_code=403, detail="Unauthorized")

    # Delete ALL applications (Pending, Verified, Rejected) to clean up state
    result = await db["applications"].delete_many({})
    
    return {
        "message": f"Deleted {result.deleted_count} applications (All Statuses).",
        "count": result.deleted_count
    } 
