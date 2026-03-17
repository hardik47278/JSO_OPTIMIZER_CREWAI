# 🤖 Agentic JSO Platform — Candidate Experience Multi-Agent System

## 📌 Overview

The Agentic JSO Platform introduces an AI-driven multi-agent architecture to enhance candidate consultation experiences, automate feedback analysis, and provide intelligent insights for HR consultants and administrators.

Phase-1 relied on static dashboards and manual workflows.
Phase-2 introduces autonomous AI agents capable of reasoning, analyzing feedback, scheduling consultations, generating satisfaction scores, and ensuring responsible AI governance through guardrail validation and human-in-the-loop review.

---

## 🎯 Why Agentic AI in Phase-2

* Automatically analyze candidate feedback after HR consultation sessions
* Generate explainable satisfaction scores using sentiment analysis and rating fusion
* Automate consultation scheduling between candidates and HR consultants
* Send automated reminders and notifications via email or WhatsApp
* Enable personalized job recommendations based on candidate profiles
* Improve platform scalability and reduce manual operational workload
* Ensure responsible AI outputs through guardrail validation and human review

---

## ⚠️ Limitations in Phase-1

* Manual coordination required for consultation scheduling
* No intelligent feedback analysis mechanism
* Satisfaction scores were not automatically generated
* Limited data-driven HR performance monitoring
* Lack of real-time consultation quality analytics
* No structured explainability or auditability of AI insights
* No advanced AI job recommendation system

---

## 🚀 How AI Agents Improve User Experience

* Automated feedback analysis and structured insight generation
* Intelligent consultation scheduling
* Real-time AI chat support for career guidance
* Automated reminders and notification workflows
* Personalized job and CV recommendations
* Reduced administrative workload
* Guardrail-validated safe and unbiased outputs
* Human review mechanisms for accountability and trust

---

## 🧠 Candidate Experience Agent Design

### Agent Type

A **Candidate Experience Agent** built as a multi-agent sequential pipeline coordinated by an **Orchestrator Agent**.

### Key Capabilities

* Analyze consultation feedback using sentiment analysis
* Generate satisfaction scores
* Provide AI career chat assistance
* Recommend CV templates and job opportunities
* Validate outputs using governance guardrails
* Enable human review for responsible AI decision-making

---

## ⚙️ Automated Tasks

* Consultation scheduling
* Feedback collection
* Sentiment and satisfaction analysis
* Consultation insight generation
* Privacy validation checks
* Notification delivery
* Job and CV recommendations
* Trend-based HR consultant performance evaluation

---

## 📊 Dashboard Integration

### 👤 User Dashboard

* Book consultation sessions automatically
* Chat with AI agent for career guidance
* Submit ratings and feedback
* View satisfaction scores and consultation insights
* Download consultation reports
* Receive personalized job recommendations
* Access privacy-protected personal data

### 👨‍💼 HR Consultant Dashboard

* View candidate feedback and sentiment insights
* Monitor performance analytics and average ratings
* Identify recurring consultation issues
* Enable fair trend-based evaluation

### 🧑‍💻 Super Admin Dashboard

* Monitor platform-wide satisfaction analytics
* Track HR consultant performance trends
* Identify recurring complaints and improvement opportunities
* Oversee AI governance and system behaviour

### 📜 Licensing Dashboard

* Monitor consultation session limits per licensed consultants
* Trigger automated renewal notifications

---

## 🧩 Problem Solved

* Lack of automated consultation satisfaction measurement
* Manual scheduling inefficiencies
* Slow candidate query resolution
* Unstructured feedback analysis
* Limited fairness in HR performance evaluation

---

## 🌍 Real-World Scenario

1. Candidate books consultation via scheduling agent
2. System sends automated reminders
3. Candidate interacts with AI chat assistant for career guidance
4. Feedback is automatically collected post-session
5. AI analyzes feedback and generates an explainable satisfaction score
6. Guardrail validation ensures safe and consistent insights
7. HR consultant reviews results before dashboard publishing
8. Platform generates downloadable consultation reports
9. Candidate continues interaction through AI chat

---


## FLOW DIAGRAM

<img width="574" height="912" alt="image" src="https://github.com/user-attachments/assets/bc819c8b-ffe2-4354-9c8e-d1782137a43e" />


## 🏗️ Technical Architecture

* **Frontend:** NextJS + React
* **Backend APIs:** NodeJS
* **AI Prototype:** CrewAI + OpenAI (Render deployment)
* **Production Stack:** AWS Bedrock
* **Serverless Execution:** AWS Lambda
* **Storage:** AWS S3
* **Database:** Supabase
* **Deployment:** Vercel
* **Governance Layer:** Guardrail validation before storing or displaying outputs

---

## 🔗 Phase-1 Integration

* Event-driven AI workflow triggers on feedback submission
* Data Flow:
  `Dashboard → API → AI Agents → Database → Dashboards`
* MCP regulates structured agent tool access
* RBAC and encryption protect sensitive candidate data
* Seamless integration without full platform rewrite

---

## ⏱️ Implementation Timeline

| Phase                          | Duration    |
| ------------------------------ | ----------- |
| Architecture Design            | 1 Week      |
| AI Agent & Backend Development | 3 Weeks     |
| Testing & Validation           | 1 Week      |
| Deployment & Monitoring        | 1 Week      |
| **Total Timeline**             | **6 Weeks** |

---

## 🤖 Multi-Agent Pipeline

### 🧩 Orchestrator Agent

Coordinates workflow and manages execution of all sub-agents.

### 📩 Notification Agent

Drafts WhatsApp or email feedback request messages.

### 📝 Feedback Collector Agent

Structures candidate rating and feedback into machine-readable format.

### 😊 Sentiment Analysis Agent

Detects emotional tone, confidence score, and key phrases.

### 📊 Satisfaction Scoring Agent

Combines sentiment and rating to compute overall satisfaction score.

### 🚨 Issue Detection Agent

Identifies operational issues and flags bias or DEI concerns.

### 📄 Report Agent

Generates actionable consultation reports.

### 🛡️ Guardrail Agent

Validates fairness, logical consistency, and appends governance notice.

---

## 🔮 Future Enhancements

* Advanced job recommendation engine
* Resume scoring and improvement suggestions
* Consultant performance prediction models
* Reinforcement learning scheduling optimization
* Multilingual AI chat assistant

---

## 📌 Conclusion

The Agentic JSO Phase-2 system transforms a static consultation platform into an **intelligent, scalable, and responsible AI-driven ecosystem**.
By combining multi-agent reasoning, automation, and governance guardrails, the platform enhances candidate experience, improves HR performance insights, and enables data-driven decision-making.
