# 🧭 Agentic AI Scheme Finder

**An AI-powered agent for discovering government welfare schemes through natural-language interaction, multi-step tool calling, and rule-based eligibility assessment.**

Developed for the **Open Innovation: Build an Agent for a Problem You Choose** challenge.

## 📌 Project Overview

Finding relevant government welfare schemes can be difficult. Individuals and families often struggle to understand eligibility criteria, income limits, documentation requirements, and available benefits.

The Agentic AI Scheme Finder aims to simplify this process through an interactive AI-powered system.

Users describe their circumstances in natural language. The agent gathers missing information through contextual follow-up questions, coordinates multiple tool calls, evaluates eligibility using predefined Python rules, and presents understandable recommendations.

Rather than functioning as a conventional chatbot, the application combines LLM-based reasoning and tool orchestration with deterministic eligibility assessment.

## 🎯 Problem Statement

Many individuals and families are unaware of government welfare schemes that may be relevant to their circumstances.

Traditional information-search workflows often require users to navigate multiple government portals, manually interpret eligibility conditions, identify required documents, and compare schemes against their personal circumstances.

This creates an accessibility and information-discovery challenge.

### Proposed Solution

An Agentic AI system that acts as an interactive scheme discovery assistant, helping users understand potentially relevant schemes through a conversational, multi-step workflow.

## ✨ Key Features

- **Natural Language Interaction:** Users describe their circumstances in plain language.
- **Dynamic Information Gathering:** Identifies missing information and asks contextual follow-up questions.
- **Multi-Step Agentic Workflow:** Coordinates multiple operations using tool-calling capabilities.
- **Multi-Provider LLM Support:** Gemini-only implementation (`app.py`) and enhanced Gemini + Groq implementation (`app2.py`).
- **Rule-Based Eligibility Assessment:** Evaluates scheme requirements using predefined Python rules.
- **Explainable Recommendations:** Explains why users may or may not qualify for individual schemes.
- **Document Guidance:** Identifies documents required for potentially eligible schemes.
- **Ineligibility Analysis:** Explains why certain schemes do not match the user's circumstances.
- **Report Generation:** Generates downloadable assessment reports.
- **Privacy-Conscious Interaction:** Avoids requesting government ID numbers, phone numbers, or bank details.

## ⚙️ Agent Architecture & Workflow

The application combines an LLM-powered conversational interface with Python-based tools and eligibility logic.

### Workflow

1. **User Input:** The user describes their personal, financial, and occupational circumstances.
2. **Information Analysis:** The agent interprets the request and identifies missing details.
3. **Contextual Follow-up:** The agent asks additional questions when necessary.
4. **Tool Orchestration:** The agent invokes relevant tools to perform required operations.
5. **Eligibility Assessment:** Predefined Python rules evaluate scheme requirements.
6. **Result Generation:** The agent presents potentially eligible and ineligible schemes with explanations.
7. **Report Generation:** Users can download an assessment report.

### Architectural Approach

- **LLM Layer:** Natural-language understanding, contextual questioning, and tool orchestration.
- **Tool Layer:** Dedicated Python functions for agent operations.
- **Eligibility Layer:** Deterministic Python logic for predefined eligibility conditions.
- **Presentation Layer:** Streamlit interface for user interaction and results.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| Google Gemini API | LLM integration |
| Groq API | Alternative LLM provider |
| Python Tool Functions | Agent operations |
| Rule-Based Logic | Eligibility assessment |
| Markdown | Report generation and documentation |

## 📂 Project Structure

```text
Only_Mar-Agentic_Chase/
│
├── app.py
├── app2.py
├── requirements.txt
├── docs/
│   └── screenshot.png
└── README.md
```

## 🚀 Installation & Usage

### Prerequisites

- Python
- Google Gemini API key or Groq API key
- Internet connectivity

### 1. Clone the Repository

```bash
git clone https://github.com/PEACEMAKER390/Only_Mar-Agentic_Chase.git
```

### 2. Navigate to the Project

```bash
cd Only_Mar-Agentic_Chase
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run Gemini-Only Version

```bash
python -m streamlit run app.py
```

### 5. Run Multi-Provider Version

```bash
python -m streamlit run app2.py
```

Enter the appropriate API key through the application's settings.

**Security:** Never upload API keys or private credentials to the public repository.

## 🎬 Project Demonstration

**Video Demonstration:** [Add your video link here]

The demonstration showcases the conversational workflow, contextual questioning, agent tool execution, eligibility assessment, and report generation.

## 🛡️ Responsible AI & Limitations

- Eligibility assessments are based on predefined demonstration rules.
- Demonstration scheme information should not be interpreted as verified or current government policy.
- AI-generated responses may contain inaccuracies.
- Users should verify scheme details through official government portals before applying.
- The application does not make official government eligibility decisions.
- API credentials should never be committed to the repository.
- Users should avoid submitting unnecessary sensitive personal information.

### Current Limitations

- Assessment accuracy depends on the completeness and correctness of predefined rules.
- Demonstration scheme data is not a substitute for an updated official government database.
- LLM responses may vary depending on the selected provider and model.
- Internet connectivity and valid API credentials are required.

## 🔮 Future Improvements

- Integration with verified and regularly updated government scheme databases.
- Expanded coverage of central and state-level schemes.
- More comprehensive eligibility rules.
- Improved document guidance.
- Multilingual interaction.
- More extensive evaluation of recommendation accuracy and reliability.
- Improved agent monitoring and error handling.

## 👨‍💻 Author

**Pradipta Kumar Modak**

B.Tech – Computer Science and Engineering

Developed for the Open Innovation challenge.

---

*Making government welfare scheme discovery more accessible, understandable, and user-friendly.*
