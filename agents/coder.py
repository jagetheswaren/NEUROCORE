import logging

logger = logging.getLogger("agents.coder")

class CoderAgent:
    """
    Automated Coding Agent bound by Permission Manager policies.
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def generate_code(self, coding_request: str) -> str:
        logger.info(f"Generating code for request: {coding_request}")
        prompt = (
            f"Write clean, production-ready Python code for the following task.\n"
            f"Task: {coding_request}\n"
            f"Provide code with error handling and inline documentation."
        )
        return self.orchestrator.run(prompt, mode="build")

    def execute_command_safely(self, command: str):
        return self.orchestrator.execute_command(command)
