from fastapi import HTTPException
import httpx


# ----- LLM 설정 -----
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
OLLAMA_MODEL = "gemma4:e2b"

SYSTEM_PROMPT = (
    "너는 한국어 텍스트 요약 전문가야. "
    "주어진 글의 핵심 내용을 2~3문장 이내로 간결하게 요약해.\n\n"
    "규칙:\n"
    "- 원문에 없는 내용은 절대 추가하지 마.\n"
    "- 글쓴이의 주장이나 결론을 빠뜨리지 마.\n"
    "- 요약문만 출력하고, '요약:' 같은 접두사나 부가 설명은 붙이지 마.\n"
    "- 한국어로 답해."
)

async def request_summarize(content: str):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [            
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {e}")

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
