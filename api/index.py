import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Candidate Experience API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://crewai-jso.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────────────────────────────

class FeedbackInput(BaseModel):
    phone: str
    rating: int
    feedback: str


class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str


class ChatInput(BaseModel):
    message: str
    history: List[ChatMessage] = []
    # context from the /analyze run — passed from frontend
    feedback: Optional[str] = ""
    rating: Optional[int] = 0
    hr_result: Optional[str] = ""
    user_result: Optional[str] = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def mask_phone(phone: str) -> str:
    if len(phone) > 6:
        return phone[:3] + "****" + phone[-3:]
    return "***masked***"


def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")
    return LLM(model="gpt-4o-mini")


def get_supabase() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set")
    return create_client(supabase_url, supabase_key)


def save_feedback_to_supabase(phone, rating, feedback, hr_dashboard, user_dashboard):
    supabase = get_supabase()
    row = {
        "phone": mask_phone(phone),
        "rating": rating,
        "feedback": feedback,
        "hr_output": hr_dashboard,
        "user_output": user_dashboard,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_used": "gpt-4o-mini",
        "agent_version": "1.0.0",
        "compute_note": "Optimized: cache=True, max_iter=2-3, sequential pipeline, minimal token prompts",
    }
    return supabase.table("candidate_feedback").insert(row).execute()


# ── /analyze endpoint (unchanged) ────────────────────────────────────────────

def build_crew():
    llm = get_llm()

    orchestrator_agent = Agent(
        role="Candidate Experience Agent (Orchestrator)",
        goal=(
            "Coordinate the complete candidate experience workflow after consultation completion, "
            "from notification to dashboard-ready validated report."
        ),
        backstory=(
            "You oversee the full candidate experience pipeline. You make sure the right agents "
            "run in the correct order, outputs stay consistent, and final results are ready for "
            "human review and dashboard publishing."
        ),
        verbose=False, llm=llm, allow_delegation=False, max_iter=3, memory=False, cache=True,
    )
    notification_agent = Agent(
        role="Notification Agent",
        goal="Send feedback request notifications to candidates.",
        backstory=(
            "You are responsible for candidate communication. "
            "You draft short, polite WhatsApp messages asking candidates for feedback."
        ),
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )
    feedback_collector_agent = Agent(
        role="Feedback Collection Agent",
        goal="Collect and structure candidate rating and written feedback clearly.",
        backstory=(
            "You read raw candidate feedback and convert it into a structured format "
            "that downstream agents can analyze consistently."
        ),
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )
    sentiment_analysis_agent = Agent(
        role="Sentiment Analysis Agent",
        goal="Analyze candidate feedback for sentiment, tone, and emotional expression.",
        backstory="You specialize in understanding emotional tone of written feedback.",
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )
    satisfaction_agent = Agent(
        role="Satisfaction Scoring Agent",
        goal="Generate an overall candidate satisfaction score.",
        backstory="You assess overall experience using rating + sentiment.",
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )
    issue_detection_agent = Agent(
        role="Issue Detection Agent",
        goal="Identify issues in feedback.",
        backstory="You detect operational or communication issues.",
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )
    report_agent = Agent(
        role="Report Agent",
        goal="Generate final experience report.",
        backstory="You combine outputs into actionable report.",
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )
    guardrail_agent = Agent(
        role="Guardrail Agent",
        goal="Validate final report.",
        backstory="You ensure score validity and fairness.",
        verbose=False, llm=llm, allow_delegation=False, max_iter=2, memory=False, cache=True,
    )

    orchestrator_task = Task(
        description="Start workflow.",
        expected_output="Workflow initiated.",
        agent=orchestrator_agent,
    )
    notification_task = Task(
        description="Draft WhatsApp feedback request for {phone}",
        expected_output="Message drafted.",
        agent=notification_agent,
        context=[orchestrator_task],
    )
    feedback_collection_task = Task(
        description="Candidate rating {rating}, feedback {feedback}",
        expected_output="Structured feedback.",
        agent=feedback_collector_agent,
        context=[notification_task],
    )
    sentiment_analysis_task = Task(
        description="Analyze sentiment.",
        expected_output="Sentiment result.",
        agent=sentiment_analysis_agent,
        context=[feedback_collection_task],
    )
    satisfaction_scoring_task = Task(
        description="Generate satisfaction score.",
        expected_output="Score result.",
        agent=satisfaction_agent,
        context=[feedback_collection_task, sentiment_analysis_task],
    )
    issue_detection_task = Task(
        description=(
            "Detect issues in the feedback. "
            "Also flag any language that may indicate bias, discriminatory treatment, "
            "or exclusion based on gender, ethnicity, age, or background. "
            "If detected, include a 'DEI Review Required' flag in your output."
        ),
        expected_output="Issue result with optional DEI Review Required flag.",
        agent=issue_detection_agent,
        context=[feedback_collection_task],
    )
    report_generation_task = Task(
        description="Generate report.",
        expected_output="Report.",
        agent=report_agent,
        context=[sentiment_analysis_task, satisfaction_scoring_task, issue_detection_task],
    )
    guardrail_validation_task = Task(
        description=(
            "Validate the report for fairness and accuracy. "
            "Append this exact disclaimer to the validated output: "
            "'--- GOVERNANCE NOTICE --- "
            "This is an AI-generated insight only. "
            "Final decisions must be reviewed and approved by a human HR consultant. "
            "AI reasoning is logged for audit purposes.'"
        ),
        expected_output="Validated report with governance disclaimer appended.",
        agent=guardrail_agent,
        context=[report_generation_task],
    )
    hr_dashboard_task = Task(
        description=(
            "Prepare HR dashboard output. "
            "Include a section titled 'HR Consultant Action Required' "
            "listing specific items the consultant must personally review. "
            "Present all AI scores as 'suggested indicators' — never as final verdicts or "
            "performance judgments on the HR consultant."
        ),
        expected_output="HR dashboard output with action items and suggested indicators.",
        agent=orchestrator_agent,
        context=[guardrail_validation_task],
    )
    user_dashboard_task = Task(
        description=(
            "Prepare user dashboard output. "
            "Include a 'Career Growth Tip' section with one personalized, encouraging suggestion "
            "for the candidate's next steps. "
            "Ensure language is inclusive and accessible to candidates from all backgrounds, "
            "including first-time job seekers and candidates from underserved communities."
        ),
        expected_output="User dashboard output with inclusive career growth tip.",
        agent=orchestrator_agent,
        context=[hr_dashboard_task],
    )

    crew = Crew(
        agents=[
            orchestrator_agent, notification_agent, feedback_collector_agent,
            sentiment_analysis_agent, satisfaction_agent, issue_detection_agent,
            report_agent, guardrail_agent,
        ],
        tasks=[
            orchestrator_task, notification_task, feedback_collection_task,
            sentiment_analysis_task, satisfaction_scoring_task, issue_detection_task,
            report_generation_task, guardrail_validation_task,
            hr_dashboard_task, user_dashboard_task,
        ],
        process=Process.sequential,
        verbose=False,
    )
    return crew


@app.post("/analyze")
async def run_agent(data: FeedbackInput):
    try:
        crew = build_crew()
        crew.kickoff(inputs={
            "phone": data.phone,
            "rating": data.rating,
            "feedback": data.feedback,
        })
        tasks = crew.tasks
        hr_output = str(tasks[-2].output.raw) if tasks[-2].output else ""
        user_output = str(tasks[-1].output.raw) if tasks[-1].output else ""

        save_feedback_to_supabase(
            phone=data.phone,
            rating=data.rating,
            feedback=data.feedback,
            hr_dashboard=hr_output,
            user_dashboard=user_output,
        )
        return {"status": "success", "hr_dashboard": hr_output, "user_dashboard": user_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── /chat endpoint (NEW) ──────────────────────────────────────────────────────

@app.post("/chat")
async def chat_agent(data: ChatInput):
    try:
        llm = get_llm()

        # last 10 messages only to save tokens
        history_text = ""
        for msg in data.history[-10:]:
            role_label = "Candidate" if msg.role == "user" else "Agent"
            history_text += f"{role_label}: {msg.content}\n"

        # build context from the /analyze session
        context_text = ""
        if data.feedback:
            context_text += f"Candidate's feedback: {data.feedback}\n"
        if data.rating:
            context_text += f"Candidate's rating: {data.rating}/5\n"
        if data.hr_result:
            context_text += f"HR Dashboard Result:\n{data.hr_result}\n"
        if data.user_result:
            context_text += f"User Dashboard Result:\n{data.user_result}\n"

        chat_support_agent = Agent(
            role="JSO Candidate Support Agent",
            goal=(
                "Help job-seeking candidates by answering their questions about the JSO platform "
                "and discussing their consultation feedback results in a friendly, supportive way."
            ),
            backstory=(
                "You are a helpful, empathetic support agent for JSO — a career intelligence platform. "
                "You assist job seekers with platform queries and help them understand their consultation "
                "experience results. You are inclusive, encouraging, and always honest. "
                "You never make final career decisions for the candidate — you guide and support them. "
                "You are aware of the candidate's recent feedback session context if provided."
            ),
            verbose=False,
            llm=llm,
            allow_delegation=False,
            max_iter=2,
            memory=False,
            cache=True,
        )

        chat_task = Task(
            description=(
                f"The candidate has asked: '{data.message}'\n\n"
                f"Session context (use if relevant):\n{context_text}\n"
                f"Conversation so far:\n{history_text}\n"
                "Respond in a friendly, concise, and helpful manner. "
                "If the question is about their feedback results, refer to the session context above. "
                "If it is a general JSO platform question, answer based on your knowledge of career platforms. "
                "Always end with an encouraging note for the candidate's career journey."
            ),
            expected_output="A friendly, helpful, concise reply to the candidate's message.",
            agent=chat_support_agent,
        )

        crew = Crew(
            agents=[chat_support_agent],
            tasks=[chat_task],
            process=Process.sequential,
            verbose=False,
        )

        crew.kickoff()
        reply = str(chat_task.output.raw) if chat_task.output else "I'm sorry, I could not process your query. Please try again."

        return {"status": "success", "reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))