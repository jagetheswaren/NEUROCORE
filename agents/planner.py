import logging

logger = logging.getLogger("agents.planner")

class PlannerAgent:
    """
    Planning Agent that generates structured architectural blueprints without executing code directly.
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def create_plan(self, task_description: str) -> str:
        logger.info(f"Generating plan for task: {task_description}")
        prompt = (
            f"Please create a detailed step-by-step technical plan for the following request.\n"
            f"Request: {task_description}\n\n"
            f"Structure your answer with:\n"
            f"1. Objectives\n"
            f"2. Architecture & Components\n"
            f"3. Step-by-Step Implementation Strategy\n"
            f"4. Security & Safety Checklist\n"
        )
        return self.orchestrator.run(prompt, mode="plan")
