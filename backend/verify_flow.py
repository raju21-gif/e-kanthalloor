
import asyncio
import aiohttp
import sys

BASE_URL = "http://127.0.0.1:8000"

async def test_flow():
    async with aiohttp.ClientSession() as session:
        print(f"1. Authenticating as Admin to get token...")
        # Login Admin
        data = {"username": "admin@kanthalloor.gov.in", "password": "admin123"}
        async with session.post(f"{BASE_URL}/auth/token", data=data) as resp:
            if resp.status != 200:
                print(f"Admin Login Failed: {await resp.text()}")
                return
            token_data = await resp.json()
            admin_token = token_data["access_token"]
            print(f"   [OK] Admin Token Recieved")

        # Login/Register dummy User
        print(f"\n2. Registering/Logging in Dummy User...")
        user_data = {
            "email": "test_citizen@example.com", 
            "password": "password123", 
            "full_name": "Test Citizen",
            "role": "citizen"
        }
        # Try register
        await session.post(f"{BASE_URL}/auth/register", json=user_data)
        # Login
        login_data = {"username": "test_citizen@example.com", "password": "password123"}
        async with session.post(f"{BASE_URL}/auth/token", data=login_data) as resp:
            if resp.status != 200:
                print(f"User Login Failed: {await resp.text()}")
                return
            user_token_data = await resp.json()
            user_token = user_token_data["access_token"]
            print(f"   [OK] User Token Received")

        # 3. Submit Info for User (needed for name/phone)
        print(f"\n3. Submitting User Personal Info...")
        info_data = {
            "full_name": "Test Citizen",
            "age": 30,
            "bank_account_no": "1234567890",
            "aadhaar_no": "123456789012",
            "phone_number": "9998887776",
            "annual_income": 50000
        }
        headers = {"Authorization": f"Bearer {user_token}"}
        async with session.post(f"{BASE_URL}/info/submit", json=info_data, headers=headers) as resp:
             if resp.status != 200:
                print(f"Info Submit Failed: {await resp.text()}")
             else:
                print(f"   [OK] Info Submitted")

        # 4. Get a Scheme ID
        print(f"\n4. Fetching Scheme ID...")
        async with session.get(f"{BASE_URL}/schemes/") as resp:
            schemes = await resp.json()
            if not schemes:
                print("No schemes found! Cannot apply.")
                return
            scheme = schemes[0]
            scheme_id = scheme["_id"]
            scheme_name = scheme["name"]
            print(f"   [OK] Using Scheme: {scheme_name} ({scheme_id})")

        # 5. Submit Application (User Side)
        print(f"\n5. Submitting Application (User Side)...")
        app_payload = {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "applicant_name": "Test Citizen",
            "user_id": "auto",
            "status": "Pending",
            "details": {}
        }
        async with session.post(f"{BASE_URL}/applications/apply", json=app_payload, headers=headers) as resp:
            if resp.status == 200:
                print(f"   [OK] Application Submitted Successfully")
            else:
                print(f"   [FAIL] Application Submission Failed: {await resp.text()}")
                return

        # 6. Admin Polling Check (Admin Side)
        print(f"\n6. Checking Admin Pending Applications Endpoint...")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        async with session.get(f"{BASE_URL}/admin/applications/pending", headers=admin_headers) as resp:
            if resp.status == 200:
                apps = await resp.json()
                print(f"   [OK] Admin fetched {len(apps)} pending applications.")
                
                # Check if our new app is there
                found = False
                for app in apps:
                    if app["scheme_name"] == scheme_name and app["status"] == "Pending":
                        found = True
                        print(f"   [SUCCESS] Found pending application for {scheme_name}!")
                        if "applicant_details" in app:
                            print(f"   [SUCCESS] Applicant Details detected: {app['applicant_details'].get('full_name')}")
                        else:
                            print(f"   [WARNING] Applicant details field missing in aggregation.")
                        break
                
                if not found:
                    print(f"   [FAIL] Could not find the just-submitted application or it is not Pending.")
            else:
                print(f"   [FAIL] Admin Polling Endpoint Failed: {await resp.text()}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_flow())
