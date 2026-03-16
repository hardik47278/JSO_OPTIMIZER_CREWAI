from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import os

load_dotenv()

# =========================================================
# LLM
# =========================================================
llm = LLM(model="gpt-4o-mini")


# =========================================================
# AGENTS
# =========================================================
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
    verbose=True,
    llm=llm,
    allow_delegation=False,
    max_iter=2,
    memory=False,
    cache=True,
)

notification_agent = Agent(
    role="Notification Agent",
    goal=(
        "Send feedback request notifications and reminders to candidates using the approved "
        "communication channel."
    ),
    backstory=(
        "You are responsible for candidate communication in the Candidate Experience System. "
        "You send short, polite, and professional WhatsApp messages asking candidates to "
        "share ratings and written feedback after consultation."
    ),
    verbose=True,
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
        "You read raw candidate feedback carefully and convert it into a structured format "
        "that downstream agents can analyze consistently."
    ),
    verbose=True,
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
        "You specialize in understanding the emotional tone of written feedback and classifying "
        "whether it is positive, neutral, or negative."
    ),
    verbose=True,
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
        "You assess the candidate's overall experience after consultation by combining explicit "
        "rating, sentiment analysis, and feedback context into a final score."
    ),
    verbose=True,
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
        "You detect operational, communication, and experience-related issues mentioned by "
        "the candidate, and classify their severity."
    ),
    verbose=True,
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
        "You combine all upstream outputs into a concise, actionable candidate experience report "
        "that HR teams can review and use for decision-making."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
    max_iter=2,
    memory=False,
    cache=True,
)

guardrail_agent = Agent(
    role="Guardrail Agent",
    goal=(
        "Validate the final report for logical consistency, completeness, fairness, and score accuracy."
    ),
    backstory=(
        "You are responsible for responsible-AI validation. You verify that the score is in range, "
        "sentiment aligns with the score, detected issues are reflected properly, and the output "
        "is safe and complete."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
    max_iter=2,
    memory=False,
    cache=True,
)

scheduling_agent = Agent(
    role="Scheduling Agent",
    goal="Optionally schedule follow-ups or future consultations if required.",
    backstory=(
        "You support future workflow extensions where follow-up actions, reminders, or interview "
        "scheduling may be needed."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
    max_iter=2,
    memory=False,
    cache=True,
)


# =========================================================
# TASKS
# =========================================================
orchestrator_task = Task(
    description=(
        "A consultation has been completed.\n"
        "Start and coordinate the candidate experience workflow in the correct order:\n"
        "1. Notification\n"
        "2. Feedback collection\n"
        "3. Analysis\n"
        "4. Report generation\n"
        "5. Guardrail validation\n"
        "6. Human review\n"
        "7. HR Dashboard publishing\n"
        "8. User Dashboard publishing"
    ),
    expected_output="Workflow initiated successfully.",
    agent=orchestrator_agent,
    markdown=True,
)

notification_task = Task(
    description=(
        "Create a short, polite, and professional WhatsApp feedback request message for the candidate.\n"
        "Candidate phone number: {phone}\n\n"
        "The message should encourage the candidate to share:\n"
        "- rating\n"
        "- written feedback\n\n"
        "Note: WhatsApp sending is disabled in this prototype. "
        "In production this message will be delivered via WhatsApp Business API."
    ),
    expected_output=(
        "Notification result including:\n"
        "- Sent message text\n"
        "- Delivery status"
    ),
    agent=notification_agent,
    markdown=True,
    context=[orchestrator_task],
)

feedback_collection_task = Task(
    description=(
        "Candidate rating: {rating}\n"
        "Candidate feedback: {feedback}\n\n"
        "Note: In production, this data arrives via WhatsApp webhook after the candidate replies. "
        "In this prototype, it is passed directly as crew inputs to simulate that async response.\n\n"
        "Read the candidate's submitted rating and written feedback after the consultation.\n"
        "Prepare a clean structured feedback summary for downstream analysis."
    ),
    expected_output=(
        "Structured Feedback:\n"
        "- Rating: <value>\n"
        "- Feedback Summary: <short summary>\n"
        "- Key Points: <bullet list>"
    ),
    agent=feedback_collector_agent,
    markdown=True,
    context=[notification_task],
)

sentiment_analysis_task = Task(
    description=(
        "Analyze the structured feedback and determine the candidate's sentiment, tone, and emotion."
    ),
    expected_output=(
        "Sentiment Analysis Result:\n"
        "- Sentiment: <Positive / Neutral / Negative>\n"
        "- Tone: <Friendly / Neutral / Frustrated / Hostile>\n"
        "- Emotion: <Happy / Neutral / Confused / Angry / Sad>"
    ),
    agent=sentiment_analysis_agent,
    markdown=True,
    context=[feedback_collection_task],
)

satisfaction_scoring_task = Task(
    description=(
        "Using the candidate's rating, structured feedback, and sentiment analysis result, "
        "generate an overall satisfaction score from 1 to 5 with a short justification."
    ),
    expected_output=(
        "Satisfaction Scoring Result:\n"
        "- Satisfaction Score: <1 to 5>\n"
        "- Justification: <short explanation>"
    ),
    agent=satisfaction_agent,
    markdown=True,
    context=[feedback_collection_task, sentiment_analysis_task],
)

issue_detection_task = Task(
    description=(
        "Identify specific issues or concerns raised in the candidate's feedback.\n"
        "Examples may include unclear guidance, poor communication, delayed response, "
        "lack of support, or negative consultation behavior."
    ),
    expected_output=(
        "Issue Detection Result:\n"
        "- Issues Detected: <bullet list or None>\n"
        "- Severity Level: <Low / Medium / High>"
    ),
    agent=issue_detection_agent,
    markdown=True,
    context=[feedback_collection_task],
)

report_generation_task = Task(
    description=(
        "Generate a final candidate experience report by combining sentiment analysis, "
        "satisfaction scoring, and issue detection outputs.\n"
        "Make it concise, actionable, and dashboard-friendly."
    ),
    expected_output=(
        "Candidate Experience Report:\n"
        "- Satisfaction Score: <value>\n"
        "- Sentiment: <Positive / Neutral / Negative>\n"
        "- Issues Detected: <bullet list or None>\n"
        "- Summary: <short paragraph>\n"
        "- Recommendation: <improvement suggestion>"
    ),
    agent=report_agent,
    markdown=True,
    context=[
        sentiment_analysis_task,
        satisfaction_scoring_task,
        issue_detection_task,
    ],
)

guardrail_validation_task = Task(
    description=(
        "Validate the final candidate experience report.\n"
        "Check the following:\n"
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
    markdown=True,
    context=[report_generation_task],
)

human_review_task = Task(
    description=(
        "Human-in-the-Loop Review:\n"
        "Review the validated candidate experience report.\n"
        "Approve it if correct, or provide corrections / override comments if needed.\n"
        "This is a real human approval checkpoint before dashboard publishing."
    ),
    expected_output=(
        "Human Review Result:\n"
        "- Decision: Approved / Corrected / Rejected\n"
        "- Reviewer Notes: <notes or corrections>"
    ),
    agent=orchestrator_agent,
    markdown=True,
    context=[guardrail_validation_task],
    human_input=True,
)

hr_dashboard_task = Task(
    description=(
        "Prepare the full candidate experience report for the HR Consultant Dashboard.\n"
        "This is an internal view — include everything:\n"
        "- Final satisfaction score (1 to 5)\n"
        "- Sentiment and tone\n"
        "- All detected issues with severity level\n"
        "- Full summary paragraph\n"
        "- Actionable recommendation for the HR consultant\n"
        "Only publish if human review decision was Approved or Corrected."
    ),
    expected_output=(
        "HR Dashboard Output:\n"
        "- Satisfaction Score: <1 to 5>\n"
        "- Sentiment: <Positive / Neutral / Negative>\n"
        "- Tone: <value>\n"
        "- Issues Detected: <bullet list or None>\n"
        "- Severity: <Low / Medium / High>\n"
        "- Summary: <paragraph>\n"
        "- Recommendation: <improvement suggestion for HR consultant>\n"
        "- Publish Status: Published to HR Dashboard"
    ),
    agent=orchestrator_agent,
    markdown=True,
    context=[human_review_task],
)

user_dashboard_task = Task(
    description=(
        "Prepare a friendly, candidate-facing summary for the User Dashboard.\n"
        "This is what the candidate sees — keep it positive and supportive.\n"
        "DO NOT include:\n"
        "- Raw numerical scores\n"
        "- Issue detection details\n"
        "- Severity labels\n"
        "- Any information that could feel punitive\n"
        "DO include:\n"
        "- A warm thank-you message for submitting feedback\n"
        "- A brief positive summary of their consultation\n"
        "- One forward-looking tip or encouragement\n"
        "- Confirmation that their feedback has been received"
    ),
    expected_output=(
        "User Dashboard Output:\n"
        "- Thank You Message: <warm message>\n"
        "- Consultation Summary: <1-2 sentences, positive framing>\n"
        "- Encouragement / Tip: <one forward-looking suggestion>\n"
        "- Feedback Status: Received and noted\n"
        "- Publish Status: Published to User Dashboard"
    ),
    agent=orchestrator_agent,
    markdown=True,
    context=[human_review_task],
)


# =========================================================
# CREW
# =========================================================
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
        scheduling_agent,
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
        human_review_task,
        hr_dashboard_task,
        user_dashboard_task,
    ],
    process=Process.sequential,
    verbose=True,
)


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    result = crew.kickoff(
        inputs={
            "phone": "+919999999999",
            "rating": 4,
            "feedback": "The consultant was helpful but the guidance was slightly unclear.",
        }
    )

    print("\nFINAL OUTPUT:\n")
    print(result)