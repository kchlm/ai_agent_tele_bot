from google.adk import Agent
from src.tools.system_tools import execute_bash_command

dev_agent = Agent(
    name = "development_agent",
    model = "gemini-flash-latest",
    instruction = """You are a specialized developer sub-agent.
    You have access to a server terminal.
    Use execute_bash_command to access GitHub, clone repositories, install packages, and execute code.
    Return the raw system output.""",
    tools = [execute_bash_command]
)