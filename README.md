# 🤖 RAG 기반 회의 요약 응답 시스템 (FastAPI + ChromaDB + Gemini)

이 프로젝트는 FastAPI, ChromaDB, Gemini API를 활용하여 회의 요약 텍스트 파일을 벡터화하고, 사용자의 자연어 질문에 대해 회의 내용을 바탕으로 응답하는 시스템입니다.

회의 요약 `.txt` 파일을 `meeting_data/` 폴더에 저장하면:

1. 자동 감지되어 문서가 ChromaDB에 벡터로 저장되고,
2. `/rag_answer` API로 질문을 보내면,
3. 관련 회의 내용을 검색해 Gemini가 응답합니다.

---

## ✅ 주요 기능

- `.txt` 파일 자동 감지 (watchdog 기반)
- 문서 → 벡터화 → ChromaDB 저장
- Gemini API로 회의 기반 질의응답
- PersistentClient 설정으로 서버 꺼져도 데이터 유지

---

## 📁 폴더 구조

```
rag_meeting_assistant/
├── main.py                  # FastAPI 서버 (자동 등록 & 질문 응답)
├── prompt_builder.py        # Gemini 프롬프트 구성 함수
├── utils.py                 # (선택) vector_check 등 유틸 함수 위치
├── build_meeting_data.py    # 수동 JSON 등록 도구 (테스트용)
├── .env                     # Gemini API 키
├── requirements.txt         # 필요한 패키지 목록
├── README.md                # 이 문서
├── vector_store/            # ✅ ChromaDB 영구 벡터 저장소
├── meeting_data/            # 회의 텍스트 입력 폴더
│   ├── 2025-06-01_10-00_회의요약.txt
│   └── meeting_data.json    # 자동 생성 JSON
```

---

## ⚙️ 설치 및 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 아래처럼 작성:

```
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### 3. FastAPI 서버 실행

```bash
uvicorn main:app --reload --port 8000
```

---

## 📄 회의 요약 텍스트 작성 예시

파일명 형식은 **`YYYY-MM-DD_HH-MM_회의요약.txt`** 입니다.

`meeting_data/2025-06-01_10-00_회의요약.txt`

```
황효동 - 자동 회의 등록 백엔드 구축
오다현 - 프론트엔드 연동 테스트
```

업로드 시:

```
📁 새 파일 감지됨: ./meeting_data/2025-06-01_10-00_회의요약.txt
✅ 2개 문서가 벡터로 추가됨.
```

---

## 💬 질문 API 예시

### ✅ 질문 전송 (curl)

```bash
curl -X POST http://localhost:8000/rag_answer \
 -H "Content-Type: application/json" \
 -d '{"question": "6월 1일 회의 내용은?"}'
```

### ✅ 응답 예시

```json
{
  "answer": "회의 내용은 프론트연동 테스트, 백엔드 구축있습니다."
}
```

---

## 🧠 에러 방어 로직

Gemini API의 사용량이 초과될 경우, 자동으로 fallback 메시지를 반환하도록 `try/except` 처리되어 있습니다.

---

## 📌 벡터 저장 유지

ChromaDB는 `vector_store/`에 `.parquet` 파일 형태로 저장되어
**서버 재시작 후에도 벡터가 유지**됩니다.

---

## 🔧 추가 API 제안 (선택 구현 가능)

| API                | 설명                              |
| ------------------ | --------------------------------- |
| `/vector_check`    | 현재 등록된 회의 문서 리스트 반환 |
| `/delete_doc`      | 특정 문서 ID로 삭제               |
| `/recent_meetings` | 최근 등록된 회의 목록             |

---

## 📚 참고 자료

- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [ChromaDB 공식 문서](https://docs.trychroma.com)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

---

## 🙌 기여 또는 문의

버그 제보, 개선 제안, 기능 추가 요청은 언제든지 환영합니다!
