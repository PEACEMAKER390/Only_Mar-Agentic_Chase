"""
Scheme Finder Agent - prototype
Run:  streamlit run app.py
Needs: pip install streamlit google-genai

IMPORTANT: the SCHEMES data below is SAMPLE / ILLUSTRATIVE ONLY.
Replace it with real, verified scheme details from official government sites
before presenting it as real information.
"""

import json
import os

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


def _find(scheme_id: str):
    for s in SCHEMES:
        if s["id"].lower() == scheme_id.strip().lower():
            return s
    return None


def _log(tool: str, args: dict, result: str):
    """Record every tool call so we can show the agent's steps to the user."""
    st.session_state.setdefault("trace", []).append(
        {"tool": tool, "args": args, "result": result}
    )


# ------------------------------------------------------------------
# 2. TOOLS (plain Python functions the agent can call)
# The docstrings and type hints are what the model reads.
# ------------------------------------------------------------------
def search_schemes(category: str) -> str:
    """List schemes in a category. Valid categories: education, skill,
    agriculture, health, housing. Returns scheme ids, names and summaries."""
    found = [
        {"id": s["id"], "name": s["name"], "summary": s["summary"]}
        for s in SCHEMES
        if s["category"] == category.strip().lower()
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
        f.write(content)
    st.session_state["report"] = content
    _log("save_report", {"chars": len(content)}, "Saved to scheme_report.md")
    return "Saved to scheme_report.md"


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
6. For each scheme give: name, verdict, the reasons from the tool, and the documents.
7. When the user has a final list, call save_report once with a short markdown summary.
Keep answers short and in simple language."""

TOOLS = [search_schemes, check_eligibility, get_documents, save_report]

# ------------------------------------------------------------------
# 4. UI
# ------------------------------------------------------------------
st.set_page_config(page_title="Scheme Finder Agent", page_icon="🧭", layout="wide")
st.title("🧭 Scheme Finder Agent")
st.caption(
    "Describe your situation in plain words. The agent finds schemes you may qualify for, "
    "asks for missing details, and explains every decision. Demo data only - verify on official portals."
)

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    model_name = st.text_input("Model", value="gemini-3.8-flash")
    if st.button("New conversation"):
        for k in ("chat", "messages", "trace", "report"):
            st.session_state.pop(k, None)
        st.rerun()
    st.markdown("**Privacy:** the agent never asks for ID numbers, phone or bank details.")
    st.markdown("**Safety:** eligibility is decided by fixed code rules, not by the AI model.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sample inputs for easy demos
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

# Show past messages
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
        st.error("Enter your Gemini API key in the sidebar first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    if "chat" not in st.session_state:
        client = genai.Client(api_key=api_key)
        st.session_state.chat = client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                tools=TOOLS,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=10),
            ),
        )

    st.session_state.trace = []  # fresh trace for this turn
    with st.chat_message("assistant"):
        with st.spinner("Agent is working..."):
            import time
            answer = None
            for attempt in range(5):
                st.session_state.trace = []  # clear steps from any failed attempt
                try:
                    response = st.session_state.chat.send_message(user_text)
                    answer = response.text or "(No answer returned. Try rephrasing.)"
                    break
                except Exception as e:
                    if ("503" in str(e) or "429" in str(e)) and attempt < 4:
                        time.sleep(5 * (attempt + 1))  # waits 5s, 10s, 15s, 20s
                        continue
                    answer = f"Something went wrong: {e}"
                    break
        st.markdown(answer)
        trace = list(st.session_state.trace)
        if trace:
            with st.expander(f"Agent steps ({len(trace)} tool calls)", expanded=True):
                for i, t in enumerate(trace, 1):
                    st.markdown(f"**{i}. `{t['tool']}`**")
                    st.json({"input": t["args"], "output": t["result"]})

    st.session_state.messages.append({"role": "assistant", "content": answer, "trace": trace})

if st.session_state.get("report"):
    with st.sidebar:
        st.download_button("Download report", st.session_state["report"], file_name="scheme_report.md")