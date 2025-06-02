from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import re
import glob
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb
import google.generativeai as genai
from prompt_builder import build_prompt

# ✅ 환경변수 로드 및 Gemini 키 설정
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

# ✅ CORS 허용 (Live Server 대응)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 디렉토리 설정
WATCH_DIR = "./meeting_data"

# ✅ ChromaDB 설정
client = chromadb.PersistentClient(path="./vector_store")
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="meetings", embedding_function=embedding_func)

# ✅ 파일명에서 날짜 추출
def extract_datetime_from_filename(filename):
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})", filename)
    return match.group(1) if match else None

# ✅ 회의요약 텍스트 파일을 벡터화하는 함수
def build_meeting_data_and_add(file_path):
    print(f"📁 벡터화 처리 중: {file_path}")
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

    if docs:
        collection.add(
            documents=[d["document"] for d in docs],
            metadatas=[{"date": d["date"]} for d in docs],
            ids=[d["id"] for d in docs]
        )
        print(f"✅ {len(docs)}개 문서 벡터화 완료")
    else:
        print("⚠️ 유효한 문장이 없어 벡터화하지 않음")

# ✅ 질문 → 벡터화 + 검색 + Gemini 호출
@app.post("/rag_answer")
def rag_answer(req: dict):
    question = req.get("question", "")
    print("📥 질문 수신:", question)

    # ✅ 모든 회의 요약 파일 벡터화
    files = glob.glob(os.path.join(WATCH_DIR, "*_회의요약.txt"))
    print(f"📂 벡터화 대상 파일: {len(files)}개")

    for path in files:
        build_meeting_data_and_add(path)

    try:
        results = collection.query(query_texts=[question], n_results=4)
        print("🔍 쿼리 결과:", results)
        documents = results.get("documents", [[]])[0]
        prompt = build_prompt(documents, question)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Gemini 호출 실패:", e)
        return {
            "answer": "⚠️ 현재 AI 응답량이 초과되었거나 오류가 발생했습니다."
        }

# ✅ 벡터 확인용 API
@app.get("/vector_check")
def vector_check():
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

# ✅ 정적 HTML 제공
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_html():
    return FileResponse("static/index.html")