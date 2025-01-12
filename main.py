from bs4 import BeautifulSoup
import requests
import json

def fetch_webpage(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()

import cohere

co = cohere.ClientV2("lZpVs6UyeDTGIjKqtud9Fi778WX4BMuyDzyBPbZ0")

def query_llm(content, query):
    prompt = f"The following is text extracted from a webpage:\n\n{content}\n\nQuestion: {query}\nAnswer:"
    response = co.chat(
        model="command-r-plus-08-2024",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.5,
    )
    return response

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

class QueryRequest(BaseModel):
    url: str
    query: str

@app.post("/query_webpage/")
async def query_webpage(request: QueryRequest):
    try:
        # Fetch content
        content = fetch_webpage(request.url)
        
        # Query LLM
        result = query_llm(content, request.query)
        
        # Respond with JSON
        return {"url": request.url, "query": request.query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))