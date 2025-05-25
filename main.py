### 📄 main.py
from fastapi import FastAPI, Request
import threading
import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb
import re
from prompt_builder import build_prompt
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()
WATCH_DIR = "./meeting_data"

# ✅ 영구 저장소를 사용하는 PersistentClient
client = chromadb.PersistentClient(path="./vector_store")
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="meetings", embedding_function=embedding_func)

def extract_datetime_from_filename(filename):
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})", filename)
    return match.group(1) if match else None

def build_meeting_data_and_add(file_path):
    print(f"📁 새 파일 감지됨: {file_path}")
    dt_str = extract_datetime_from_filename(file_path)
    date_only = dt_str.split("_")[0] if dt_str else "unknown"

    docs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "-" not in line:
                continue
            parts = line.split("-", 1)
            doc = parts[1].strip()
            docs.append({
                "id": f"{dt_str}_m{idx+1}",
                "date": date_only,
                "document": doc
            })

    # ChromaDB에 추가
    collection.add(
        documents=[d["document"] for d in docs],
        metadatas=[{"date": d["date"]} for d in docs],
        ids=[d["id"] for d in docs]
    )
    print(f"✅ {len(docs)}개 문서가 벡터로 추가됨.")

class TxtHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith("_회의요약.txt"):
            time.sleep(1)
            build_meeting_data_and_add(event.src_path)

def start_watchdog():
    observer = Observer()
    observer.schedule(TxtHandler(), path=WATCH_DIR, recursive=False)
    observer.start()
    print(f"👀 회의요약.txt 감시 중: {WATCH_DIR}")

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_watchdog, daemon=True).start()

@app.post("/rag_answer")
def rag_answer(req: dict):
    question = req["question"]
    results = collection.query(query_texts=[question], n_results=4)
    print("🔍 쿼리 결과:", results)
    documents = results["documents"][0] if results["documents"] else []
    prompt = build_prompt(documents, question)
    model = genai.GenerativeModel("gemini-1.5-pro")
    try:
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        print("❌ Gemini 호출 실패:", e)
        return {
            "answer": "⚠️ 현재 AI 응답량이 초과되었습니다. 잠시 후 다시 시도해주세요."
        }

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_html():
    return FileResponse("static/index.html")
@app.get("/vector_check")
def vector_check():
    # meetings 컬렉션 전체 데이터 조회
    results = collection.get()
    ids = results.get("ids", [])
    docs = results.get("documents", [])
    metas = results.get("metadatas", [])

    combined = [
        {
            "id": i,
            "document": d,
            "date": m.get("date", "unknown")
        }
        for i, d, m in zip(ids, docs, metas)
    ]
    return {"count": len(combined), "documents": combined}