# ✅ meeting_data.json 파일을 수동으로 ChromaDB에 등록하는 도구 (테스트용)

import json
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

client = chromadb.Client()
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="meetings", embedding_function=embedding_func)

with open("./meeting_data/meeting_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

collection.add(
    documents=[d["document"] for d in data],
    metadatas=[{"date": d["date"]} for d in data],
    ids=[d["id"] for d in data]
)

print(f"✅ 총 {len(data)}개의 문서가 수동으로 추가되었습니다.")