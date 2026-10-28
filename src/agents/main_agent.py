from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.agents.dev_agent import dev_agent

def delegate_to_dev_agent(query: str) -> str:
    try:
        session_service = InMemorySessionService()
        runner = Runner(agent=dev_agent, app_name="dev_subagent", session_service=session_service)
        events = runner.run(user_id="internal_user", session_id="internal_session", new_message=query)

        output = ""
        for event in events:
            if hasattr(event, 'is_final_response') and event.is_final_response():
                if event.content and event.content.parts:
                    output = event.content.parts[0].text
                    break

        return output if output else "Sub-agent executed without text output."

    except Exception as e:
        return f"Sub-agent execution error: {str(e)}"

        response = runner.run(new_message=query)
        return response.text

main_agent = Agent(
    name = "main_agent",
    model = "gemini-flash-latest",
    instruction = """You are the primary interface. Answer standard queries directly.
    If the user request OS-level code execution, software installation, or GitHub tool integration,
    delegate the task immediately to delegate_to_dev_agent.""",
    tools = [delegate_to_dev_agent]
)