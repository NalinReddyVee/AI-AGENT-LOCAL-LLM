
# Chatbot with FastAPI, LLM & Function Calling

This project is a **FastAPI-based chatbot** that uses a **Local LLM (Ollama with LLaMA3)** for streaming responses, integrated with **vector-based retrieval (RAG)** and **function calling capabilities**.  
The frontend is built with **vanilla HTML, CSS, and JavaScript**, providing a simple yet interactive UI to ask questions and receive real-time responses.

---

## Features
- ⚡ **Real-time streaming responses** from the LLM.
- 📚 **Context-aware answers** using a vector database.
- 🧠 **Function calling support** for executing custom Python functions.
- 🔄 **Dynamic collection selection** (fetched from backend API).
- 🎨 **Lightweight frontend** with no heavy frameworks.
- 🚀 **FastAPI backend** for handling queries and streaming responses.
- 🐳 **Docker support** for running Ollama and API.

---

## Architecture
```
Frontend (HTML/JS) --> FastAPI Backend --> Vector DB (e.g., Chroma) --> LLM (Ollama)
```

---

## Tech Stack
- **Backend:** FastAPI, httpx, StreamingResponse
- **Frontend:** HTML, CSS, Vanilla JS
- **LLM:** Ollama (LLaMA3)
- **Vector DB:** Chroma or other retrievers
- **Containerization:** Docker

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Install Dependencies
Create a virtual environment and install the requirements:
```bash
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows

pip install -r requirements.txt
```

---

### 3. Run Ollama in Docker
If Ollama is running in Docker, check the container resources (optional):
```bash
docker stats
```
To run Ollama with **custom CPU and memory:**
```bash
docker run -d --name ollama \
  --cpus="4" --memory="8g" \
  -p 11434:11434 ollama/ollama
```

---

### 4. Start the FastAPI Server
```bash
uvicorn app.main:app --reload
```
Backend runs at: **http://127.0.0.1:8000**

---

### 5. Open the Frontend
Simply open `index.html` in your browser or serve it with a simple HTTP server:
```bash
python -m http.server 8080
```
Then navigate to **http://localhost:8080**

---

## API Endpoints
### POST /chat/query-stream/
- Streams LLM responses.
- Request: `collection_name`, `query`
- Response: Real-time text chunks.

### GET /collections/
- Returns a list of all available collections.

---

## Function Calling
The backend supports **function calling** by detecting JSON responses from the LLM:
```json
{
  "function_call": {
    "name": "book_appointment",
    "arguments": {
      "date": "2025-07-25",
      "patient_id": "123"
    }
  }
}
```
You can extend the `call_function()` method in the backend to add your custom functions.

---

## Project Structure
```
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── routes/              # API routes
│   ├── services/            # LLM & VectorDB logic
├── static/
│   ├── index.html           # Frontend UI
├── requirements.txt
└── README.md
```

---

## Screenshots
_Add screenshots of your chatbot UI here._

---

## Future Improvements
- Add authentication for API endpoints.
- Integrate a modern frontend (React/Vue).
- Improve vector search with embeddings.
- Add logging and monitoring for LLM responses.

---

## License
This project is licensed under the MIT License.
