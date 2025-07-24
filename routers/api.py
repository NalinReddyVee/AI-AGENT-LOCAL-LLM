from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from services.extractor import extract_text
from services.chroma_service import get_collection
from fastapi.responses import JSONResponse
from utils.text_processing import chunk_text

router = APIRouter()

@router.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            text = extract_text(file)
            if not text.strip():
                raise ValueError("No text extracted")
            collection = get_collection("nabh_faqs")
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                collection.add(
                    documents=[chunk],
                    ids=[f"{file.filename}_{i}"],
                    metadatas=[{"source": file.filename, "type": "faq", "uploaded_by": "admin", "chunk_index": i}]
                )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {e}")
    return {"message": "Files uploaded and indexed successfully."}


@router.post("/query/")
async def query_vector_db(query: str = Form(...)):
    try:
        collection = get_collection("nabh_faqs")
        results = collection.query(query_texts=[query], n_results=1)
        if results["documents"]:
            return {
                "query": query,
                "matched_doc": results["documents"][0][0],
                "doc_id": results["ids"][0][0]
            }
        else:
            return JSONResponse(status_code=404, content={"message": "No match found."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {e}")
    

    
