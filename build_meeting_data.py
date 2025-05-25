import os
import json
import re
from datetime import datetime

INPUT_DIR = "./meeting_data"
OUTPUT_JSON = os.path.join(INPUT_DIR, "meeting_data.json")

def extract_date_from_filename(filename):
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return match.group(1) if match else None

def build_documents():
    documents = []
    files = os.listdir(INPUT_DIR)

    for file in files:
        if file.endswith("_회의요약.txt"):
            path = os.path.join(INPUT_DIR, file)
            date_str = extract_date_from_filename(file)
            with open(path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line or "-" not in line:
                        continue
                    parts = line.split("-", 1)
                    doc = parts[1].strip()
                    documents.append({
                        "id": f"{date_str.replace('-', '')}_m{idx+1}",
                        "date": date_str,
                        "document": doc
                    })

    return documents

def save_json(documents):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    print(f"✅ meeting_data.json 생성 완료 ({len(documents)}개 문서)")

if __name__ == "__main__":
    docs = build_documents()
    save_json(docs)