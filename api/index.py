import os
from datetime import datetime, timezone

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


class FeedbackInput(BaseModel):
    phone: str
    rating: int
    feedback: str


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


def save_feedback_to_supabase(
    phone: str,
    rating: int,
    feedback: str,
    hr_dashboard: str,
    user_dashboard: str,
):
    supabase = get_supabase()

    row = {
        "phone": phone,
        "rating": rating,
        "feedback": feedback,
        "hr_output": hr_dashboard,
        "user_output": user_dashboard,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    response = supabase.table("candidate_feedback").insert(row).execute()
    return response


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
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        memory=False,
        cache=True,
    )

    notification_agent = Agent(
        role="Notification Agent",
        goal="Send feedback request notifications to candidates.",
        backstory=(
            "You are responsible for candidate communication. "
            "You draft short, polite WhatsApp messages asking candidates for feedback."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    feedback_collector_agent = Agent(
        role="Feedback Collection Agent",
        goal="Collect and structure candidate rating and written feedback clearly.",
        backstory=(
            "You read raw candidate feedback and convert it into a structured format "
            "that downstream agents can analyze consistently."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    sentiment_analysis_agent = Agent(
        role="Sentiment Analysis Agent",
        goal="Analyze candidate feedback for sentiment, tone, and emotional expression.",
        backstory="You specialize in understanding emotional tone of written feedback.",
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    satisfaction_agent = Agent(
        role="Satisfaction Scoring Agent",
        goal="Generate an overall candidate satisfaction score.",
        backstory="You assess overall experience using rating + sentiment.",
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    issue_detection_agent = Agent(
        role="Issue Detection Agent",
        goal="Identify issues in feedback.",
        backstory="You detect operational or communication issues.",
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    report_agent = Agent(
        role="Report Agent",
        goal="Generate final experience report.",
        backstory="You combine outputs into actionable report.",
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    guardrail_agent = Agent(
        role="Guardrail Agent",
        goal="Validate final report.",
        backstory="You ensure score validity and fairness.",
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
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
        description="Detect issues.",
        expected_output="Issue result.",
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
        description="Validate report.",
        expected_output="Validation result.",
        agent=guardrail_agent,
        context=[report_generation_task],
    )

    hr_dashboard_task = Task(
        description="Prepare HR dashboard output.",
        expected_output="HR output.",
        agent=orchestrator_agent,
        context=[guardrail_validation_task],
    )

    user_dashboard_task = Task(
        description="Prepare user dashboard output.",
        expected_output="User output.",
        agent=orchestrator_agent,
        context=[hr_dashboard_task],
    )

    crew = Crew(
        agents=[
            orchestrator_agent,
            notification_agent,
            feedback_collector_agent,
            sentiment_analysis_agent,
            satisfaction_agent,
            issue_detection_agent,
            report_agent,
            guardrail_agent,
        ],
        tasks=[
            orchestrator_task,
            notification_task,
            feedback_collection_task,
            sentiment_analysis_task,
            satisfaction_scoring_task,
            issue_detection_task,
            report_generation_task,
            guardrail_validation_task,
            hr_dashboard_task,
            user_dashboard_task,
        ],
        process=Process.sequential,
        verbose=False,
    )

    return crew


@app.post("/analyze")
async def run_agent(data: FeedbackInput):
    try:
        crew = build_crew()

        result = crew.kickoff(
            inputs={
                "phone": data.phone,
                "rating": data.rating,
                "feedback": data.feedback,
            }
        )

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

        return {
            "status": "success",
            "hr_dashboard": hr_output,
            "user_dashboard": user_output,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))