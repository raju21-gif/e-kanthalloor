from fastapi import APIRouter, Depends, HTTPException, status
from models import Application, User
from database import get_database
from .auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/apply", response_model=dict)
async def apply_scheme(
    application: Application, 
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Submit a new scheme application.
    """
    try:
        email = current_user.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch actual user to get ID and assure existence
        user_doc = await db["users"].find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user_doc["_id"])
        
        # Link application to user
        application.user_id = user_id
        application.submission_date = datetime.utcnow()
        if not application.status:
            application.status = "Pending"

        if not application.status:
            application.status = "Pending"

        # AI Auto-fill: Fetch User Profile
        info_doc = await db["info"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
        
        applicant_details = {
             "full_name": user_doc.get("full_name", "Unknown"),
             "phone": "Not Provided"
        }
        
        if info_doc:
             applicant_details = {
                 "full_name": info_doc.get("full_name", ""),
                 "age": info_doc.get("age", ""),
                 "phone_number": info_doc.get("phone_number", ""),
                 "aadhaar_no": info_doc.get("aadhaar_no", ""),
                 "bank_account_no": info_doc.get("bank_account_no", ""),
                 "annual_income": info_doc.get("annual_income", "")
             }
        
        # Store in the flexible 'details' field or a dedicated one if we updated model
        # Using 'details' as 'applicant_details' nested object
        application.details["applicant_details"] = applicant_details

        print(f"Submitting Application for User: {user_id}, Scheme: {application.scheme_name}. Auto-filled details: {applicant_details.get('full_name')}")

        # Convert to dict
        app_dict = application.model_dump(by_alias=True)
        if app_dict.get("_id") is None:
            app_dict.pop("_id", None)
        
        # Insert into MongoDB
        new_app = await db["applications"].insert_one(app_dict)
        
        # Database saves application with status "Pending"
        
        return {
            "message": "Application Enquiry submitted to Panchayat Office.",
            "id": str(new_app.inserted_id),
            "status": "Pending"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error submitting application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-applications", response_model=list)
async def get_my_applications(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    fetch all applications for the logged-in user.
    """
    try:
        email = current_user.get("sub")
        user_doc = await db["users"].find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user_doc["_id"])
        
        cursor = db["applications"].find({"user_id": user_id}).sort("submission_date", -1)
        apps = await cursor.to_list(length=100)
        
        # Serialization fix
        for app in apps:
            app["_id"] = str(app["_id"])
            
        return apps
    except Exception as e:
        print(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch applications")

@router.post("/generate-message", response_model=dict)
async def generate_application_message(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generates a personalized application message for WhatsApp based on user data and scheme details.
    """
    try:
        scheme_id = body.get("scheme_id")
        if not scheme_id:
            raise HTTPException(status_code=400, detail="Scheme ID required")

        email = current_user.get("sub")
        # 1. Fetch User Info
        user_doc = await db["users"].find_one({"email": email})
        user_id = str(user_doc["_id"])
        
        info_doc = await db["info"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
        
        if not info_doc:
            # Fallback if no specific info doc
            info_doc = {
                "full_name": user_doc.get("full_name", "Citizen"),
                "phone_number": "Not provided",
                "aadhaar_no": "Not provided",
                "age": "Not provided",
                "bank_account_no": "Not provided"
            }

        # 2. Fetch Scheme Info
        from bson import ObjectId
        scheme = await db["schemes"].find_one({"_id": ObjectId(scheme_id)})
        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")

        # 3. Generate Message (Simulated AI)
        # In a real scenario, this would call an LLM with a prompt
        
        scheme_name = scheme.get("name", "Welfare Scheme")
        
        message = f"""*Application for {scheme_name}*
        
Respectful Sir/Madam,

I am {info_doc.get('full_name')}, a resident of Kanthalloor Panchayat. I would like to apply for the *{scheme_name}*.

*My Details:*
• Name: {info_doc.get('full_name')}
• Age: {info_doc.get('age')}
• Phone: {info_doc.get('phone_number')}
• Aadhaar: {info_doc.get('aadhaar_no')}
• Bank Acc: {info_doc.get('bank_account_no')}

I have attached necessary documents visually in this chat or will provide them physically. Please guide me on the next steps.

Thank you."""

        print(f"Generated message for user {email} on scheme {scheme_name}")
        
        return {"message": message, "phone": "919876543210"} # Returns mock official number

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
