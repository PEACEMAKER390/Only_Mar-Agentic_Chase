"""
Scheme Finder Agent - two-provider version (Gemini OR Groq)
Run:  python -m streamlit run app2.py
Needs: pip install streamlit google-genai openai

(The 'openai' package is only used to talk to Groq, which has an OpenAI-style API.)

IMPORTANT: the SCHEMES data below is SAMPLE / ILLUSTRATIVE ONLY.
Replace it with real, verified scheme details from official government sites
before presenting it as real information.
"""

import json
import os
import time

import streamlit as st
from google import genai
from google.genai import types

# ------------------------------------------------------------------
# 1. DATA (sample - replace with verified real schemes)
# ------------------------------------------------------------------
SCHEMES = [
    {
        "id": "EDU1",
        "name": "Demo Scholarship for Low-Income Students",
        "category": "education",
        "summary": "Yearly scholarship for students from low-income families.",
        "min_age": 16, "max_age": 30, "max_income": 250000,
        "states": ["all"], "occupations": ["student"],
        "documents": ["Income certificate", "Previous marksheet", "College admission proof", "Bank passbook copy"],
    },
    {
        "id": "EDU2",
        "name": "Demo Skill Training Programme for Youth",
        "category": "skill",
        "summary": "Free short-term job skill courses with a training stipend.",
        "min_age": 18, "max_age": 35, "max_income": 600000,
        "states": ["all"], "occupations": ["any"],
        "documents": ["Age proof", "Education certificate", "Passport-size photo"],
    },
    {
        "id": "AGR1",
        "name": "Demo Farmer Income Support Scheme",
        "category": "agriculture",
        "summary": "Direct income support for small farmers.",
        "min_age": 18, "max_age": 100, "max_income": 500000,
        "states": ["all"], "occupations": ["farmer"],
        "documents": ["Land ownership record", "Bank passbook copy", "ID proof"],
    },
    {
        "id": "HLT1",
        "name": "Demo Health Cover for Low-Income Families",
        "category": "health",
        "summary": "Hospitalisation cover for eligible low-income families.",
        "min_age": 0, "max_age": 100, "max_income": 200000,
        "states": ["all"], "occupations": ["any"],
        "documents": ["Family income proof", "ID proof of all members", "Residence proof"],
    },
    {
        "id": "HSG1",
        "name": "Demo State Housing Assistance",
        "category": "housing",
        "summary": "Financial help to build or repair a basic home.",
        "min_age": 21, "max_age": 100, "max_income": 300000,
        "states": ["west bengal"], "occupations": ["any"],
        "documents": ["Income certificate", "Land or tenancy proof", "ID proof", "Bank passbook copy"],
    },
]

CATEGORIES = sorted({s["category"] for s in SCHEMES})


def _find(scheme_id):
    for s in SCHEMES:
        if s["id"].lower() == str(scheme_id).strip().lower():
            return s
    return None


def _log(tool, args, result):
    """Record every tool call so we can show the agent's steps to the user."""
    st.session_state.setdefault("trace", []).append(
        {"tool": tool, "args": args, "result": result}
    )


# ------------------------------------------------------------------
# 2. TOOLS (plain Python functions the agent can call)
# ------------------------------------------------------------------
def search_schemes(category: str) -> str:
    """List schemes in a category. Valid categories: education, skill,
    agriculture, health, housing. Returns scheme ids, names and summaries."""
    found = [
        {"id": s["id"], "name": s["name"], "summary": s["summary"]}
        for s in SCHEMES
        if s["category"] == str(category).strip().lower()
    ]
    result = json.dumps(found) if found else f"No schemes found. Valid categories: {CATEGORIES}"
    _log("search_schemes", {"category": category}, result)
    return result


def check_eligibility(scheme_id: str, age: int, annual_income: int, state: str, occupation: str) -> str:
    """Check whether a person may be eligible for a scheme, using fixed rules.
    Use this tool for every eligibility decision, never guess.
    annual_income is the yearly family income in rupees. occupation examples:
    student, farmer, unemployed, worker."""
    s = _find(scheme_id)
    if not s:
        result = json.dumps({"error": f"Unknown scheme id {scheme_id}"})
        _log("check_eligibility", {"scheme_id": scheme_id}, result)
        return result

    # Some models send numbers as text, so convert safely.
    age = int(float(age))
    annual_income = int(float(annual_income))
    state = str(state)
    occupation = str(occupation)

    passed, failed = [], []

    if s["min_age"] <= age <= s["max_age"]:
        passed.append(f"age {age} is within {s['min_age']}-{s['max_age']}")
    else:
        failed.append(f"age {age} is outside {s['min_age']}-{s['max_age']}")

    if annual_income <= s["max_income"]:
        passed.append(f"income {annual_income} is within the limit {s['max_income']}")
    else:
        failed.append(f"income {annual_income} is above the limit {s['max_income']}")

    if "all" in s["states"] or state.strip().lower() in s["states"]:
        passed.append(f"state '{state}' is covered")
    else:
        failed.append(f"state '{state}' is not covered (covers: {', '.join(s['states'])})")

    if "any" in s["occupations"] or occupation.strip().lower() in s["occupations"]:
        passed.append(f"occupation '{occupation}' is accepted")
    else:
        failed.append(f"occupation '{occupation}' is not accepted (needs: {', '.join(s['occupations'])})")

    result = json.dumps({
        "scheme_id": s["id"],
        "scheme_name": s["name"],
        "result": "likely_eligible" if not failed else "not_eligible",
        "passed": passed,
        "failed": failed,
    })
    _log("check_eligibility", {"scheme_id": scheme_id, "age": age, "annual_income": annual_income,
                               "state": state, "occupation": occupation}, result)
    return result


def get_documents(scheme_id: str) -> str:
    """Return the list of documents needed to apply for a scheme."""
    s = _find(scheme_id)
    result = json.dumps(s["documents"]) if s else json.dumps({"error": f"Unknown scheme id {scheme_id}"})
    _log("get_documents", {"scheme_id": scheme_id}, result)
    return result


def save_report(content: str) -> str:
    """Save the final summary (markdown) the user can take with them.
    Call this once, at the end, after the user's matches are final."""
    with open("scheme_report.md", "w", encoding="utf-8") as f:
        f.write(str(content))
    st.session_state["report"] = str(content)
    _log("save_report", {"chars": len(str(content))}, "Saved to scheme_report.md")
    return "Saved to scheme_report.md"


TOOLS = [search_schemes, check_eligibility, get_documents, save_report]
TOOL_MAP = {f.__name__: f for f in TOOLS}

# Same four tools described in the OpenAI/Groq format (Gemini reads the Python functions directly).
OPENAI_TOOLS = [
    {"type": "function", "function": {
        "name": "search_schemes",
        "description": "List schemes in a category. Valid categories: education, skill, agriculture, health, housing.",
        "parameters": {"type": "object",
                       "properties": {"category": {"type": "string"}},
                       "required": ["category"]}}},
    {"type": "function", "function": {
        "name": "check_eligibility",
        "description": "Check whether a person may be eligible for a scheme using fixed rules. "
                       "Use for every eligibility decision. annual_income is yearly family income in rupees.",
        "parameters": {"type": "object",
                       "properties": {"scheme_id": {"type": "string"},
                                      "age": {"type": "integer"},
                                      "annual_income": {"type": "integer"},
                                      "state": {"type": "string"},
                                      "occupation": {"type": "string",
                                                     "description": "e.g. student, farmer, unemployed, worker"}},
                       "required": ["scheme_id", "age", "annual_income", "state", "occupation"]}}},
    {"type": "function", "function": {
        "name": "get_documents",
        "description": "Return the list of documents needed to apply for a scheme.",
        "parameters": {"type": "object",
                       "properties": {"scheme_id": {"type": "string"}},
                       "required": ["scheme_id"]}}},
    {"type": "function", "function": {
        "name": "save_report",
        "description": "Save the final markdown summary. Call once, at the end.",
        "parameters": {"type": "object",
                       "properties": {"content": {"type": "string"}},
                       "required": ["content"]}}},
]

# ------------------------------------------------------------------
# 3. AGENT SETUP
# ------------------------------------------------------------------
SYSTEM = """You are a Scheme Finder assistant that helps people in India discover
government schemes they MAY qualify for.

Rules:
1. You need four facts before checking eligibility: age, yearly family income
   (rupees), state, and occupation. If any is missing, ask ONE short question
   for the missing facts. Do not guess them.
2. NEVER ask for Aadhaar, phone number, bank details or any personal ID.
3. Use search_schemes to find candidates, check_eligibility for EVERY
   eligibility decision, and get_documents for the documents list.
   Never decide eligibility yourself.
4. Say 'you may be eligible', never 'you are eligible'. Always tell the user
   to verify on the official government portal before applying.
5. If a tool returns an error or nothing is found, say so plainly. Do not invent schemes.
6b. Before answering, call search_schemes once for EVERY category (education, skill, agriculture, health, housing). Then call check_eligibility for every scheme found, and list EVERY scheme marked likely_eligible with its reasons and documents. Never skip a category. name, verdict, the reasons from the tool, and the documents.
7. Your final message to the user must always contain the full results (for each scheme: name, verdict, reasons, documents), even after calling save_report. Never reply with only 'saved'. Call save_report once with a short markdown summary., call save_report once with a short markdown summary.
Keep answers short and in simple language."""

DEFAULT_MODELS = {"Gemini": "gemini-3.8-flash", "Groq": "llama-3.3-70b-versatile"}
TRANSIENT_ERRORS = ("503", "429", "UNAVAILABLE", "tool_use_failed", "tool call validation failed", "overloaded", "timeout")

def ask_gemini(user_text, api_key, model):
    if "chat" not in st.session_state:
        client = genai.Client(api_key=api_key)
        st.session_state.chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                tools=TOOLS,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=10),
            ),
        )
    response = st.session_state.chat.send_message(user_text)
    return response.text or "(No answer returned. Try rephrasing.)"


def ask_groq(user_text, api_key, model):
    from openai import OpenAI  # imported here so Gemini-only use does not need it

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    if "oai_messages" not in st.session_state:
        st.session_state.oai_messages = [{"role": "system", "content": SYSTEM}]
    msgs = st.session_state.oai_messages
    start = len(msgs)  # remember where this turn began, so a failed turn can be undone
    msgs.append({"role": "user", "content": user_text})
    try:
        for _ in range(10):  # stop condition: max 10 steps
            resp = client.chat.completions.create(
                model=model, messages=msgs, tools=OPENAI_TOOLS, tool_choice="auto"
            )
            msg = resp.choices[0].message
            entry = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                entry["tool_calls"] = [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ]
            msgs.append(entry)
            if not msg.tool_calls:
                return msg.content or "(No answer returned. Try rephrasing.)"
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                    result = TOOL_MAP[tc.function.name](**args)
                except Exception as e:  # let the model see the error and recover
                    result = f"Error: {e}"
                msgs.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
        return "Stopped: too many steps."
    except Exception:
        del msgs[start:]  # undo the half-finished turn so a retry starts clean
        raise


def ask_with_retry(user_text, provider, api_key, model):
    """Retry a few times on busy-server / rate-limit errors."""
    ask = ask_gemini if provider == "Gemini" else ask_groq
    for attempt in range(5):
        st.session_state.trace = []  # clear steps from any failed attempt
        try:
            return ask(user_text, api_key, model)
        except Exception as e:
            text = str(e)
            if any(t in text for t in TRANSIENT_ERRORS) and attempt < 4:
                time.sleep(5 * (attempt + 1))  # waits 5s, 10s, 15s, 20s
                continue
            return f"Something went wrong: {e}"
    return "Something went wrong: too many retries."


# ------------------------------------------------------------------
# 4. UI
# ------------------------------------------------------------------
def reset_conversation(keep_messages=False):
    keys = ["chat", "oai_messages", "trace", "report"]
    if not keep_messages:
        keys.append("messages")
    for k in keys:
        st.session_state.pop(k, None)


def main():
    st.set_page_config(page_title="Scheme Finder Agent", page_icon="🧭", layout="wide")
    st.title("🧭 Scheme Finder Agent")
    st.caption(
        "Describe your situation in plain words. The agent finds schemes you may qualify for, "
        "asks for missing details, and explains every decision. Demo data only - verify on official portals."
    )

    with st.sidebar:
        st.header("Settings")
        provider = st.selectbox("AI provider", ["Gemini", "Groq"])
        env_name = "GEMINI_API_KEY" if provider == "Gemini" else "GROQ_API_KEY"
        api_key = st.text_input(f"{provider} API key", type="password",
                                value=os.getenv(env_name, ""), key=f"key_{provider}")
        model_name = st.text_input("Model", value=DEFAULT_MODELS[provider], key=f"model_{provider}")
        if provider == "Groq":
            st.caption("Groq model names change. If you get a 'model not found' error, "
                       "copy a current name from console.groq.com.")
        if st.button("New conversation"):
            reset_conversation()
            st.rerun()
        st.markdown("**Privacy:** the agent never asks for ID numbers, phone or bank details.")
        st.markdown("**Safety:** eligibility is decided by fixed code rules, not by the AI model.")

    # Switching provider starts a fresh conversation (histories are not compatible)
    if st.session_state.get("active_provider") != provider:
        reset_conversation()
        st.session_state["active_provider"] = provider

    if "messages" not in st.session_state:
        st.session_state.messages = []

    cols = st.columns(3)
    examples = [
        "I'm 20, a student in West Bengal. My family earns about 2 lakh a year.",
        "My father is a farmer in West Bengal, age 45, income around 3 lakh. What can he get?",
        "I need help for my family. We earn 1.5 lakh a year.",
    ]
    clicked = None
    for col, text in zip(cols, examples):
        if col.button(text, use_container_width=True):
            clicked = text

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("trace"):
                with st.expander(f"Agent steps ({len(m['trace'])} tool calls)"):
                    for i, t in enumerate(m["trace"], 1):
                        st.markdown(f"**{i}. `{t['tool']}`**")
                        st.json({"input": t["args"], "output": t["result"]})

    user_text = st.chat_input("Describe your situation...") or clicked

    if user_text:
        if not api_key:
            st.error(f"Enter your {provider} API key in the sidebar first.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        st.session_state.trace = []
        with st.chat_message("assistant"):
            with st.spinner(f"Agent is working ({provider})..."):
                answer = ask_with_retry(user_text, provider, api_key, model_name)
            st.markdown(answer)
            trace = list(st.session_state.get("trace", []))
            if trace:
                with st.expander(f"Agent steps ({len(trace)} tool calls)", expanded=True):
                    for i, t in enumerate(trace, 1):
                        st.markdown(f"**{i}. `{t['tool']}`**")
                        st.json({"input": t["args"], "output": t["result"]})

        st.session_state.messages.append({"role": "assistant", "content": answer, "trace": trace})

    if st.session_state.get("report"):
        with st.sidebar:
            st.download_button("Download report", st.session_state["report"], file_name="scheme_report.md")


if __name__ == "__main__":
    main()