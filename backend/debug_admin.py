
import asyncio
import aiohttp
import sys

BASE_URL = "http://127.0.0.1:8000"

async def debug_admin():
    async with aiohttp.ClientSession() as session:
        print(f"Authenticating as Admin...")
        # Login Admin
        data = {"username": "admin@kanthalloor.gov.in", "password": "admin123"}
        async with session.post(f"{BASE_URL}/auth/token", data=data) as resp:
            if resp.status != 200:
                print(f"Admin Login Failed: {await resp.text()}")
                return
            token_data = await resp.json()
            admin_token = token_data["access_token"]
            print(f"Got Admin Token")

        print(f"\nChecking /admin/applications/pending...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        async with session.get(f"{BASE_URL}/admin/applications/pending", headers=headers) as resp:
            print(f"Status Code: {resp.status}")
            text = await resp.text()
            print(f"Response: {text}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(debug_admin())
