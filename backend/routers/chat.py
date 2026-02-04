from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key configuration error")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
        "X-Title": "e-Kanthalloor Portal" # Optional
    }

    # OpenRouter Endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    payload = {
        "model": "deepseek/deepseek-chat", # Standard DeepSeek model
        "max_tokens": 1000,
        "messages": [
            {
                "role": "system",
                "content": "You are Governance Sahayi, a helpful AI assistant for the e-Kanthalloor digital governance portal. Your goal is to assist citizens with finding welfare schemes, understanding application processes, and navigating local government services. Be polite, concise, and helpful. If asked about specific scheme details you don't know, suggest they check the 'Welfare Schemes' section."
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return {"reply": data["choices"][0]["message"]["content"]}
        else:
            return {"reply": "I'm sorry, I couldn't generate a response at this time."}

    except requests.exceptions.RequestException as e:
        print(f"Chat API Error: {e}")
        if response is not None:
             print(f"Response Body: {response.text}")
        raise HTTPException(status_code=503, detail="AI Service currently unavailable")
