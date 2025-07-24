from fastapi import FastAPI
from routers import chroma_router
from routers import chat
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount the 'public' folder to serve static files
app.mount("/static", StaticFiles(directory="public"), name="static")

app.include_router(chroma_router.router)
app.include_router(chat.router, prefix="/chat")



@app.get("/")
async def initGet():
    return {"message": "API is running!"}

@app.get("/chat")
async def serve_chat():
    return FileResponse("public/chatbot.html")
