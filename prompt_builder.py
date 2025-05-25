# This module provides a function to build a prompt for a question-answering task based on relevant documents and a user question. 

def build_prompt(relevant_docs, user_question):
    context = "\n".join(relevant_docs)
    return f"""
당신은 회의 분석 전문가입니다. 다음은 회의 참석자별 요약 내용입니다.
각 줄은 형식: '이름 - 역할 요약' 으로 되어 있습니다.

🗂 회의 요약:
{context}

❓ 사용자 질문:
{user_question}

✅ 문맥에 맞는 정확한 정보를 추출하여 한국어로 자연스럽게 답변하세요.
"""