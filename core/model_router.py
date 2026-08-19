import logging
import os
from pathlib import Path

logger = logging.getLogger("core.model_router")

class ModelRouter:
    """
    Routes requests dynamically to the right Ollama model tier based on intent or mode.
    Tiers:
      - fast: qwen3:8b (thinking: false) - Default conversational response
      - reasoning: qwen3:8b (thinking: true) - Deep step-by-step logic & planning
      - coding: qwen2.5-coder:7b (thinking: false) - Code generation & refactoring
      - vision: qwen3-vl:8b (thinking: false) - Image & UI analysis
    """

    def __init__(self, config_path="config/models.yaml"):
        self.tiers = {
            "fast": {
                "model": "qwen3:8b",
                "thinking": False,
                "temperature": 0.7,
                "max_tokens": 400
            },
            "reasoning": {
                "model": "qwen3:8b",
                "thinking": True,
                "temperature": 0.2,
                "max_tokens": 2048
            },
            "coding": {
                "model": "qwen2.5-coder:7b",
                "thinking": False,
                "temperature": 0.1,
                "max_tokens": 2048
            },
            "vision": {
                "model": "qwen3-vl:8b",
                "thinking": False,
                "temperature": 0.5,
                "max_tokens": 1024
            }
        }
        self.default_tier = "fast"
        self._load_config(config_path)

    def _load_config(self, config_path):
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "tiers" in data:
                        self.tiers.update(data["tiers"])
                    if data and "default_tier" in data:
                        self.default_tier = data["default_tier"]
                logger.info(f"Loaded model router configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Could not parse {config_path}: {e}. Using built-in tier defaults.")

    def route(self, prompt: str, mode: str = "friend", requested_tier: str = None) -> dict:
        if requested_tier and requested_tier in self.tiers:
            selected_tier = requested_tier
        elif mode == "plan" or "reason" in prompt.lower() or "architecture" in prompt.lower():
            selected_tier = "reasoning"
        elif mode == "build" or "code" in prompt.lower() or "function" in prompt.lower() or "class" in prompt.lower():
            selected_tier = "coding"
        elif "image" in prompt.lower() or "photo" in prompt.lower() or "screenshot" in prompt.lower():
            selected_tier = "vision"
        else:
            selected_tier = self.default_tier

        tier_config = self.tiers.get(selected_tier, self.tiers[self.default_tier])
        logger.info(f"Routed request (mode='{mode}', tier='{selected_tier}') -> model='{tier_config['model']}'")
        return {
            "tier": selected_tier,
            "model": tier_config["model"],
            "thinking": tier_config.get("thinking", False),
            "temperature": tier_config.get("temperature", 0.7),
            "max_tokens": tier_config.get("max_tokens", 400)
        }
