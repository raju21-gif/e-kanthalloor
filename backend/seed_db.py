import asyncio
from database import db
from models import Scheme, User, UserInDB
from security import get_password_hash
import os

schemes_data = [
    {
        "name": "Pradhan Mantri Awas Yojana (PMAY)",
        "description": "Housing scheme for rural families to provide pucca houses with basic amenities.",
        "beneficiary_category": ["Homeless families", "Families living in kuccha houses"],
        "eligibility_criteria": "Must not own a pucca house. Annual income below Rs 2 Lakhs.",
        "documents_required": ["Aadhaar Card", "Bank Passbook", "Ration Card", "Income Certificate"],
        "benefits": "Financial assistance of ₹1.2 Lakhs for house construction.",
        "application_process": "1. Collect PMAY form from Panchayat Office.\n2. Submit with documents to VEO.\n3. Inspection by officials -> Approval.",
        "department": "Rural Development"
    },
    {
        "name": "PM-KISAN Samman Nidhi",
        "description": "Income support scheme for landholding farmers.",
        "beneficiary_category": ["Farmers", "Landholders"],
        "eligibility_criteria": "Must be a landholding farmer family. No income tax payers.",
        "documents_required": ["Land Record", "Aadhaar Card", "Bank Passbook"],
        "benefits": "₹6,000 per year in three equal installments.",
        "application_process": "Apply via PM-KISAN Portal or visit Krishi Bhavan / Panchayat with land records.",
        "department": "Agriculture"
    },
    {
        "name": "Old Age Pension (Indira Gandhi National Old Age Pension Scheme)",
        "description": "Social security pension for senior citizens belonging to BPL households.",
        "beneficiary_category": ["Senior Citizens (60+)", "BPL"],
        "eligibility_criteria": "Age 60 years or above. Must belong to BPL household.",
        "documents_required": ["Aadhaar Card", "Age Proof", "BPL Ration Card", "Bank Details"],
        "benefits": "₹1,600 monthly pension.",
        "application_process": "Submit pension application form at the Grama Panchayat office with age proof and BPL card.",
        "department": "Social Justice"
    }
]

async def seed():
    await db.connect_to_database()
    
    # Schemes - Resetting to ensure schema compliance
    print("Resetting Schemes collection...")
    await db.db["schemes"].drop()
    
    print("Seeding Schemes...")
    for s in schemes_data:
        await db.db["schemes"].insert_one(s)
    print("Schemes seeded successfully.")

    # Admin User
    admin = await db.db["users"].find_one({"email": "admin@kanthalloor.gov.in"})
    if not admin:
        print("Seeding Admin User...")
        hashed = get_password_hash("admin123")
        user = UserInDB(
            email="admin@kanthalloor.gov.in",
            full_name="Panchayat Admin",
            role="admin",
            phone_number="7012402897",
            hashed_password=hashed
        )
        await db.db["users"].insert_one(user.dict())

    # Citizen User
    citizen = await db.db["users"].find_one({"email": "mahesh@gmail.com"})
    if not citizen:
        print("Seeding Citizen User...")
        hashed = get_password_hash("password123")
        user = UserInDB(
            email="mahesh@gmail.com",
            full_name="Mahesh Kumar",
            role="citizen",
            phone_number="9876543210",
            hashed_password=hashed
        )
        await db.db["users"].insert_one(user.dict())
    else:
        print("Resetting Citizen Password...")
        hashed = get_password_hash("password123")
        await db.db["users"].update_one(
            {"email": "mahesh@gmail.com"},
            {"$set": {"hashed_password": hashed}}
        )
    
    await db.close_database_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed())
