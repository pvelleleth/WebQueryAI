import faiss
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import requests
import cohere
import os

app = FastAPI()

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Cohere client
co = cohere.Client("lZpVs6UyeDTGIjKqtud9Fi778WX4BMuyDzyBPbZ0")


# Function to fetch and clean webpage content
def fetch_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        raise Exception(f"Error fetching the webpage: {str(e)}")


# Function to preprocess and embed webpage content
def preprocess_and_embed(content):
    try:
        # Split the text into chunks
        chunks = content.split("\n\n")  # Split by double newline
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]  # Remove empty lines
        
        # Generate embeddings for each chunk
        embeddings = embedding_model.encode(chunks)
        return chunks, embeddings
    except Exception as e:
        raise Exception(f"Error preprocessing content: {str(e)}")


# Function to create a FAISS index
def create_faiss_index(embeddings):
    try:
        dim = embeddings.shape[1]  # Dimension of embeddings
        index = faiss.IndexFlatL2(dim)  # Create an L2 distance index
        index.add(embeddings)  # Add embeddings to the index
        return index
    except Exception as e:
        raise Exception(f"Error creating FAISS index: {str(e)}")


# Function to retrieve relevant chunks
def retrieve_relevant_chunks(index, query, chunks, top_k=3):
    try:
        # Generate embedding for the query
        query_embedding = embedding_model.encode([query])
        
        # Search the index for the top_k relevant chunks
        distances, indices = index.search(query_embedding, top_k)
        relevant_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
        return relevant_chunks
    except Exception as e:
        raise Exception(f"Error retrieving relevant chunks: {str(e)}")


# Function to query the LLM
def query_llm(context, query):
    try:
        prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        response = co.generate(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        return response.generations[0].text.strip()
    except Exception as e:
        raise Exception(f"Error querying Cohere LLM: {str(e)}")


# Pydantic model for API request validation
class QueryRequest(BaseModel):
    url: str
    query: str


# API endpoint for querying a webpage with RAG
@app.post("/query_webpage_rag/")
async def query_webpage_rag(request: QueryRequest):
    try:
        # Step 1: Fetch webpage content
        content = fetch_webpage(request.url)
        
        # Step 2: Preprocess and embed content
        chunks, embeddings = preprocess_and_embed(content)
        
        # Step 3: Create FAISS index
        index = create_faiss_index(embeddings)
        
        # Step 4: Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(index, request.query, chunks)
        
        # Step 5: Query the LLM
        context = "\n".join(relevant_chunks)
        result = query_llm(context, request.query)
        
        # Return the result
        return {"url": request.url, "query": request.query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))