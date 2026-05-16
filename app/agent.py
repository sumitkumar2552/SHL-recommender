
import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

from app.retriever import get_retriever
from app.prompts import build_system_prompt, build_messages

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"   # Groq ka best free model


def extract_query_for_retrieval(messages: list[dict]) -> str:
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    return " ".join(user_msgs[-3:]) if user_msgs else ""


def parse_agent_response(raw_text: str) -> dict:
    # JSON block dhundo
    json_match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        json_str = brace_match.group(0) if brace_match else None

    if json_str:
        try:
            data = json.loads(json_str)
            reply = data.get("reply", "")
            recommendations = data.get("recommendations", [])
            end_of_conversation = data.get("end_of_conversation", False)

            valid_recs = []
            retriever = get_retriever()
            valid_urls = retriever.get_valid_urls()

            for rec in recommendations:
                if not isinstance(rec, dict):
                    continue
                name = rec.get("name", "").strip()
                url = rec.get("url", "").strip()
                test_type = rec.get("test_type", "").strip()

                if url and url not in valid_urls:
                    catalog_item = retriever.get_by_name(name)
                    if catalog_item:
                        url = catalog_item["url"]
                        test_type = catalog_item.get("test_type", test_type)
                    else:
                        continue

                if name and url:
                    valid_recs.append({"name": name, "url": url, "test_type": test_type})

            return {
                "reply": reply,
                "recommendations": valid_recs[:10],
                "end_of_conversation": bool(end_of_conversation)
            }
        except json.JSONDecodeError:
            pass

    return {"reply": raw_text.strip(), "recommendations": [], "end_of_conversation": False}


def chat(messages: list[dict]) -> dict:
    retriever = get_retriever()
    query = extract_query_for_retrieval(messages)
    relevant_items = retriever.search(query, top_k=15) if query else retriever.get_all()[:20]
    system_prompt = build_system_prompt(relevant_items)
    formatted_messages = build_messages(messages)

    if not formatted_messages:
        return {
            "reply": "Hello! I'm the SHL Assessment Recommender. Tell me about the role you're hiring for!",
            "recommendations": [],
            "end_of_conversation": False
        }

    try:
        # Groq API call
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *formatted_messages
            ],
            max_tokens=1500,
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content or ""
        result = parse_agent_response(raw_text)
        return {
            "reply": result.get("reply", ""),
            "recommendations": result.get("recommendations", []),
            "end_of_conversation": result.get("end_of_conversation", False)
        }

    except Exception as e:
        print(f"[Agent] Error: {e}")
        return {
            "reply": f"Error: {str(e)}. Check GROQ_API_KEY in .env file.",
            "recommendations": [],
            "end_of_conversation": False
        }