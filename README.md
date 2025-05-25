# 🤖 RAG 기반 회의 요약 응답 시스템 (FastAPI + ChromaDB + Gemini)

회의 요약 텍스트 파일을 자동 감지하여 ChromaDB에 벡터 등록하고, Gemini API를 통해 자연어 질문에 대한 회의 기반 응답을 제공하는 시스템입니다.

---

## 🚀 주요 기능

- `meeting_data/` 폴더 내 `_회의요약.txt` 자동 감지
- `.txt` → 벡터화하여 ChromaDB에 자동 저장
- 질문을 `/rag_answer`로 보내면 Gemini가 문맥 응답

---

## 📁 폴더 구조

```
rag_meeting_assistant/
├── main.py                # FastAPI 앱 (자동 감지 포함)
├── prompt_builder.py      # Gemini 프롬프트 생성
├── .env                   # Gemini API 키
├── requirements.txt
├── meeting_data/          # 회의 텍스트 저장소
│   ├── 2025-05-25_14-00_회의요약.txt
│   └── meeting_data.json  # 자동 생성됨
├── dev_tools/             # 수동 테스트용 도구
│   └── chroma_setup.py
└── vector_store/          # ChromaDB 내부 저장소
```

---

## ⚙️ 설치 및 실행

```bash
pip install -r requirements.txt

# .env 파일에 API 키 설정
echo "GOOGLE_API_KEY=your_gemini_api_key" > .env

# FastAPI 서버 실행
uvicorn main:app --reload --port 8000
```

---

## 🧪 테스트 방법

1. `meeting_data/2025-06-01_10-00_회의요약.txt` 파일 생성
2. 내용 예시:

```
황효동 - 회의 자동화 백엔드 구축
김지민 - 프론트엔드 연동 디버깅
```

3. 콘솔 출력:

```
📁 새 파일 감지됨: ./meeting_data/2025-06-01_10-00_회의요약.txt
✅ 2개 문서가 벡터로 추가됨.
```

---

## 🧠 질문 예시 (curl)

```bash
curl -X POST http://localhost:8000/rag_answer \
 -H "Content-Type: application/json" \
 -d '{"question": "오늘 회의에서 내가 맡은 일은 뭐였지?"}'
```

---

## 📦 참고

- Gemini API: [https://makersuite.google.com/app](https://makersuite.google.com/app)
- ChromaDB: [https://docs.trychroma.com](https://docs.trychroma.com)
- sentence-transformers: MiniLM 기반 임베딩 사용

---

## 📌 기타

- `dev_tools/` 폴더는 테스트용입니다. 운영 환경에서는 제거 예정입니다.

```

```
