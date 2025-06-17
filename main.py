from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import json

app = FastAPI()
OLLAMA_URL = "http://localhost:11434/api/chat"

@app.post("/generate")
async def generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")

    async def stream_response():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json={
                    "model": "tinyllama",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        yield json.loads(line)["message"]["content"] + "\n"

    return StreamingResponse(stream_response(), media_type="text/plain")
