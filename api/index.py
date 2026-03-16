import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM

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
        backstory=(
            "You specialize in understanding emotional tone of written feedback."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    satisfaction_agent = Agent(
        role="Satisfaction Scoring Agent",
        goal="Generate an overall candidate satisfaction score using the rating and sentiment analysis.",
        backstory=(
            "You assess the candidate's overall experience by combining rating, "
            "sentiment analysis, and feedback context into a final score."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    issue_detection_agent = Agent(
        role="Issue Detection Agent",
        goal="Identify specific issues or concerns raised in candidate feedback.",
        backstory=(
            "You detect operational, communication, and experience-related issues "
            "and classify their severity."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    report_agent = Agent(
        role="Report Agent",
        goal="Generate a final candidate experience report for HR and dashboard use.",
        backstory=(
            "You combine all upstream outputs into a concise, actionable report "
            "that HR teams can use for decision-making."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    guardrail_agent = Agent(
        role="Guardrail Agent",
        goal="Validate the final report for consistency, completeness, fairness, and score accuracy.",
        backstory=(
            "You are responsible for responsible-AI validation. You verify score range, "
            "sentiment alignment, issue reflection, and output safety."
        ),
        verbose=False,
        llm=llm,
        allow_delegation=False,
        max_iter=2,
        memory=False,
        cache=True,
    )

    orchestrator_task = Task(
        description=(
            "A consultation has been completed.\n"
            "Coordinate the candidate experience workflow:\n"
            "1. Notification\n"
            "2. Feedback collection\n"
            "3. Analysis\n"
            "4. Report generation\n"
            "5. Guardrail validation\n"
            "6. HR Dashboard publishing\n"
            "7. User Dashboard publishing"
        ),
        expected_output="Workflow initiated successfully.",
        agent=orchestrator_agent,
    )

    notification_task = Task(
        description=(
            "Draft a short, polite WhatsApp feedback request message for the candidate.\n"
            "Candidate phone number: {phone}\n"
            "Note: WhatsApp sending is disabled in this prototype."
        ),
        expected_output="Drafted message text and delivery status.",
        agent=notification_agent,
        context=[orchestrator_task],
    )

    feedback_collection_task = Task(
        description=(
            "Candidate rating: {rating}\n"
            "Candidate feedback: {feedback}\n\n"
            "Note: In production this arrives via WhatsApp webhook. "
            "In this prototype it is passed directly as crew inputs.\n\n"
            "Structure the feedback for downstream analysis."
        ),
        expected_output=(
            "Structured Feedback:\n"
            "- Rating: <value>\n"
            "- Feedback Summary: <short summary>\n"
            "- Key Points: <bullet list>"
        ),
        agent=feedback_collector_agent,
        context=[notification_task],
    )

    sentiment_analysis_task = Task(
        description="Analyze the structured feedback for sentiment, tone, and emotion.",
        expected_output=(
            "Sentiment Analysis Result:\n"
            "- Sentiment: <Positive / Neutral / Negative>\n"
            "- Tone: <Friendly / Neutral / Frustrated / Hostile>\n"
            "- Emotion: <Happy / Neutral / Confused / Angry / Sad>"
        ),
        agent=sentiment_analysis_agent,
        context=[feedback_collection_task],
    )

    satisfaction_scoring_task = Task(
        description=(
            "Using the candidate rating, structured feedback, and sentiment analysis, "
            "generate an overall satisfaction score from 1 to 5 with justification."
        ),
        expected_output=(
            "Satisfaction Scoring Result:\n"
            "- Satisfaction Score: <1 to 5>\n"
            "- Justification: <short explanation>"
        ),
        agent=satisfaction_agent,
        context=[feedback_collection_task, sentiment_analysis_task],
    )

    issue_detection_task = Task(
        description=(
            "Identify specific issues in the candidate feedback such as unclear guidance, "
            "poor communication, delayed response, or negative behavior."
        ),
        expected_output=(
            "Issue Detection Result:\n"
            "- Issues Detected: <bullet list or None>\n"
            "- Severity Level: <Low / Medium / High>"
        ),
        agent=issue_detection_agent,
        context=[feedback_collection_task],
    )

    report_generation_task = Task(
        description=(
            "Generate a final candidate experience report combining sentiment, "
            "satisfaction score, and issue detection. Make it concise and dashboard-friendly."
        ),
        expected_output=(
            "Candidate Experience Report:\n"
            "- Satisfaction Score: <value>\n"
            "- Sentiment: <value>\n"
            "- Issues Detected: <bullet list or None>\n"
            "- Summary: <short paragraph>\n"
            "- Recommendation: <improvement suggestion>"
        ),
        agent=report_agent,
        context=[sentiment_analysis_task, satisfaction_scoring_task, issue_detection_task],
    )

    guardrail_validation_task = Task(
        description=(
            "Validate the candidate experience report:\n"
            "- satisfaction score is between 1 and 5\n"
            "- sentiment logically aligns with score\n"
            "- detected issues are reflected in summary and recommendation\n"
            "- report is complete, fair, and safe for display"
        ),
        expected_output=(
            "Validation Result:\n"
            "- Status: Valid / Needs Review\n"
            "- Reason: <short explanation>\n"
            "- Final Checked Score: <1 to 5>"
        ),
        agent=guardrail_agent,
        context=[report_generation_task],
    )

    hr_dashboard_task = Task(
        description=(
            "Prepare the full report for the HR Consultant Dashboard.\n"
            "Include everything: score, sentiment, tone, issues, severity, summary, recommendation.\n"
            "Only publish if guardrail validation passed."
        ),
        expected_output=(
            "HR Dashboard Output:\n"
            "- Satisfaction Score: <1 to 5>\n"
            "- Sentiment: <value>\n"
            "- Tone: <value>\n"
            "- Issues Detected: <bullet list or None>\n"
            "- Severity: <Low / Medium / High>\n"
            "- Summary: <paragraph>\n"
            "- Recommendation: <improvement suggestion>\n"
            "- Publish Status: Published to HR Dashboard"
        ),
        agent=orchestrator_agent,
        context=[guardrail_validation_task],
    )

    user_dashboard_task = Task(
        description=(
            "Prepare a friendly candidate-facing summary for the User Dashboard.\n"
            "DO NOT include scores, issues, severity, or anything punitive.\n"
            "DO include a thank-you message, positive consultation summary, "
            "one encouragement tip, and feedback confirmation."
        ),
        expected_output=(
            "User Dashboard Output:\n"
            "- Thank You Message: <warm message>\n"
            "- Consultation Summary: <1-2 sentences positive framing>\n"
            "- Encouragement / Tip: <one forward-looking suggestion>\n"
            "- Feedback Status: Received and noted\n"
            "- Publish Status: Published to User Dashboard"
        ),
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


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def run_agent(data: FeedbackInput):
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

    return {
        "status": "success",
        "final_output": str(result),
        "hr_dashboard": hr_output,
        "user_dashboard": user_output,
    }