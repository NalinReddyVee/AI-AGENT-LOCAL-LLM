from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from services.chroma_service import get_collection, delete_collection, list_collections
from services.extractor import extract_text
from utils.text_processing import chunk_text

router = APIRouter()

import json
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from typing import List

router = APIRouter()

@router.post("/upload/")
async def upload_files(
    collection_name: str = Form(...),
    doc_type: str = Form(...),
    files: List[UploadFile] = File(...)
):
    print(f"[DEBUG] Starting upload to collection: {collection_name}, doc_type: {doc_type}")
    try:
        collection = get_collection(collection_name)
        print("[DEBUG] Collection retrieved successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to get collection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection: {e}")

    for file in files:
        try:
            filename = file.filename
            print(f"[DEBUG] Processing file: {filename}")

            content = await file.read()
            print(f"[DEBUG] Read {len(content)} bytes from {filename}")
            file.file.seek(0)  # Reset pointer for reuse

            if filename.lower().endswith(".json") and doc_type.lower() == "faq":
                print(f"[DEBUG] Detected JSON FAQ file: {filename}")
                try:
                    data = json.loads(content.decode("utf-8"))
                    print(f"[DEBUG] JSON parsed successfully with {len(data)} top-level entries.")
                except Exception as e:
                    print(f"[ERROR] Failed to parse JSON from {filename}: {e}")
                    raise HTTPException(status_code=400, detail=f"Invalid JSON in {filename}: {e}")

                for category_obj in data:
                    for category_name, category_content in category_obj.items():
                        print(f"[DEBUG] Processing category: {category_name}")
                        items = category_content.get("Items", [])
                        print(f"[DEBUG] Found {len(items)} items under category '{category_name}'.")

                        for item in items:
                            question = item.get("Question", "").strip()
                            answer = item.get("Answer", "").strip()
                            tags = item.get("Tags", "")
                            item_number = item.get("ItemNumber")
                            print(f"[DEBUG] Adding FAQ Item #{item_number}: {question[:50]}...")

                            document_text = f"Q: {question}\nA: {answer}"
                            collection.add(
                                documents=[document_text],
                                ids=[f"{filename}_{category_name}_{item_number}"],
                                metadatas=[{
                                    "source": filename,
                                    "type": doc_type,
                                    "category": category_name,
                                    "item_number": item_number,
                                    "tags": tags,
                                    "uploaded_by": "admin"
                                }]
                            )
                print(f"[DEBUG] Finished processing JSON FAQ file: {filename}")
            else:
                print(f"[DEBUG] Non-JSON file detected: {filename}, extracting text...")
                text = extract_text(file)
                print(f"[DEBUG] Extracted {len(text)} characters from {filename}")
                chunks = chunk_text(text)
                print(f"[DEBUG] Split {filename} into {len(chunks)} chunks.")

                for i, chunk in enumerate(chunks):
                    print(f"[DEBUG] Adding chunk #{i} of {filename}")
                    collection.add(
                        documents=[chunk],
                        ids=[f"{filename}_{i}"],
                        metadatas=[{
                            "source": filename,
                            "type": doc_type,
                            "uploaded_by": "admin",
                            "chunk_index": i
                        }]
                    )
                print(f"[DEBUG] Finished processing non-JSON file: {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to process {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {e}")

    print("[DEBUG] All files uploaded and indexed successfully.")
    return {"message": "Files uploaded and indexed successfully."}


@router.post("/query/")
async def query_vector_db(collection_name: str = Form(...), query: str = Form(...)):
    try:
        collection = get_collection(collection_name)
        results = collection.query(query_texts=[query], n_results=5)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/")
def list_all_collections():
    try:
        return list_collections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}")
def get_collection_data(collection_name: str):
    try:
        collection = get_collection(collection_name)

        # Fetch all data (documents, metadata, and ids)
        data = collection.get(include=["documents", "metadatas", "ids"])

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch collection '{collection_name}': {e}")


@router.delete("/collections/{collection_name}")
def delete_a_collection(collection_name: str):
    try:
        delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
