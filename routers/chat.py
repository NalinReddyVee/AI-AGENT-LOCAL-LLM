import httpx
from fastapi import Form, HTTPException
from pydantic import BaseModel
from typing import List
from services.chroma_service import get_collection  # adjust import
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import time


router = APIRouter()

# Global persistent HTTP client
client = httpx.AsyncClient(timeout=httpx.Timeout(99.0))

class AnswerResponse(BaseModel):
    query: str
    answer: str
    context_docs: List[str]

@router.post("/query/", response_model=AnswerResponse)
async def query_vector_db(
    collection_name: str = Form(...),
    query: str = Form(...)
):
    try:
        print("Querying the request")
        collection = get_collection(collection_name)
        results = collection.query(query_texts=[query], n_results=3)

        docs = results["documents"][0]
        context = "\n\n".join(docs)
        prompt = f"""Use the following information to answer the question.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"""
        # print(prompt)
        # Send prompt to Ollama
        try:
            # Ollama streaming response
            answer = ""
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                async with client.stream("POST", "http://localhost:11434/api/generate", json={
                    "model": "phi",
                    "prompt": prompt,
                    "stream": True
                }) as response:
                    if response.status_code != 200:
                        raise HTTPException(status_code=500, detail="Failed to get response from Ollama.")
                    
                    async for line in response.aiter_lines():
                        if line.strip() == "":
                            continue
                        try:
                            chunk = httpx.Response(200, content=line).json()
                            answer += chunk.get("response", "")
                        except Exception as e:
                            print("Streaming chunk parse error:", e)

            return AnswerResponse(query=query, answer=answer.strip(), context_docs=docs)

        except Exception as e:
            import traceback
            print("Exception occurred:", repr(e))
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e) or "Unknown error")


    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-stream/")
async def stream_answer(
    collection_name: str = Form(...),
    query: str = Form(...)
):
    try:
        start_time = time.time()
        print(f"[DEBUG] Received query: '{query}' for collection '{collection_name}'")

        collection = get_collection(collection_name)
        print(f"[DEBUG] Collection '{collection_name}' retrieved. Time: {time.time() - start_time:.2f}s")

        results = collection.query(query_texts=[query], n_results=3)
        docs = results.get("documents", [[]])[0]

        if not docs:
            print("[DEBUG] No documents found. Returning fallback response.")
            return StreamingResponse(
                iter(["The information is not available."]),
                media_type="text/plain"
            )

        context = "\n\n".join(docs)
        print(f"[DEBUG] Built context with {len(docs)} documents. Context length: {len(context)} chars.")

        prompt = f"""You are an assistant who answers user questions using only the information provided below.

Strictly follow these rules:
- Use only the given context to form your answer.
- Do NOT guess or make up any information.
- If the answer cannot be found in the context, say: "The information is not available."

Context:
{context}

User Question:
{query}

Answer:"""

        print(f"[DEBUG] Prompt prepared. Length: {len(prompt)} chars.")

        async def event_generator():
            try:
                print("[DEBUG] Sending streaming request to Ollama...")
                async with client.stream("POST", "http://127.0.0.1:11434/api/generate", json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": True
                }) as response:
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                text = chunk.get("response", "")
                                if text:
                                    yield text
                            except json.JSONDecodeError:
                                print(f"[WARN] Could not parse line: {line}")
                                continue
            except Exception as stream_err:
                print(f"[ERROR] Streaming error: {stream_err}")
                yield "[Error: Streaming failed.]"

        print(f"[DEBUG] Total pre-stream setup time: {time.time() - start_time:.2f}s")
        return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        print(f"[ERROR] Exception in stream_answer: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")