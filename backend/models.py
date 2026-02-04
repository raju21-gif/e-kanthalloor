from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Optional, List, Any, Annotated
from datetime import datetime
from bson import ObjectId

# Pydantic V2 compatible ObjectId handling
PyObjectId = Annotated[str, BeforeValidator(str)]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "citizen" # citizen, official, admin
    panchayat: Optional[str] = None # Added for locality
    language_pref: str = "en" # en, ta, ml
    # Profile Fields
    ward: Optional[str] = None
    occupation: Optional[str] = None
    address: Optional[str] = None
    bank_account_no: Optional[str] = None
    ifsc_code: Optional[str] = None
    profile_image_url: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class User(UserBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class SchemeBase(BaseModel):
    name: str
    description: str # Purpose
    beneficiary_category: List[str] # e.g. ["Farmers", "Women"]
    eligibility_criteria: str # Simple text explanation
    documents_required: List[str] # List of docs
    benefits: str # What do they get?
    application_process: str # Offline guidance
    department: Optional[str] = None # Govt Dept

class SchemeCreate(SchemeBase):
    pass

class Scheme(SchemeBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class PersonalInfo(BaseModel):
    full_name: str
    age: int
    bank_account_no: str
    aadhaar_no: str
    phone_number: str
    annual_income: float
    user_id: Optional[str] = None # Link to the user who submitted it
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Application(BaseModel):
    scheme_id: str
    scheme_name: str
    applicant_name: str
    user_id: str
    status: str = "Pending" # Pending, Approved, Rejected
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    # Flexible details for different schemes
    details: dict = {} 
    
    id: Optional[PyObjectId] = Field(None, alias="_id")
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
