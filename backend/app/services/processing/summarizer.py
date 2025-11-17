import logging
import json
from typing import Dict, Any, Optional
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class SummarizerService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        logger.info(f"Summarizer service initialized with model {self.model}")

    def generate_summary(
        self, transcript: str, session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Generating summary for transcript ({len(transcript)} chars)")

            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(transcript, session_context)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            summary_text = response.choices[0].message.content
            tokens_used = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens,
            }

            try:
                summary = json.loads(summary_text)
            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse GPT response as JSON: {summary_text[:200]}"
                )
                raise ValueError("GPT returned invalid JSON")

            summary["tokens_used"] = tokens_used
            self._validate_summary(summary)
            cost = self._calculate_cost(tokens_used)
            logger.info(
                f"Summary generated successfully. "
                f"Tokens: {tokens_used['total']}, Cost: ${cost:.4f}"
            )

            return summary

        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            raise

    def _build_system_prompt(self) -> str:
        return """You are an expert AI assistant helping therapists create structured session summaries.

Your task is to analyze therapy session transcripts and generate a comprehensive, professional summary.

CRITICAL PRIVACY REQUIREMENTS:
1. NEVER include real names, full names, or identifiable information
2. Replace any names with "Paciente" (patient) or "Terapeuta" (therapist)
3. Remove or generalize any addresses, phone numbers, CPF, specific locations
4. Remove specific workplace names, school names, or other identifying details
5. Keep the clinical content but anonymize all personal identifiers

OUTPUT FORMAT:
You must return a valid JSON object with this exact structure:

{
  "main_points": [
    "List of 3-7 key points discussed in the session"
  ],
  "emotions_observed": [
    {
      "emotion": "name of emotion",
      "intensity": "baixa|moderada|alta",
      "context": "when/why this emotion appeared"
    }
  ],
  "behavioral_patterns": [
    "Observable patterns in patient's behavior, thinking, or reactions"
  ],
  "action_items": [
    {
      "task": "Specific task for patient",
      "frequency": "How often",
      "deadline": "When to complete"
    }
  ],
  "risk_assessment": {
    "level": "baixo|moderado|alto|crítico",
    "notes": "Brief explanation of risk level"
  },
  "next_session_focus": [
    "Topics or areas to explore in next session"
  ],
  "therapist_notes": "General observations, progress notes, or clinical impressions",
  "ai_confidence_score": 0.85
}

LANGUAGE: All content must be in Brazilian Portuguese (pt-BR).

CLINICAL ACCURACY: Focus on therapeutic content, emotional dynamics, and actionable insights.
Be professional, objective, and clinically relevant."""

    def _build_user_prompt(
        self, transcript: str, context: Optional[Dict[str, Any]]
    ) -> str:
        prompt = f"""Please analyze this therapy session transcript and generate a structured summary.

TRANSCRIPT:
{transcript}
"""

        if context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"

        prompt += "\n\nGenerate the summary as a JSON object following the specified structure."

        return prompt

    def _validate_summary(self, summary: Dict[str, Any]):
        required_fields = [
            "main_points",
            "emotions_observed",
            "behavioral_patterns",
            "action_items",
            "risk_assessment",
            "next_session_focus",
            "therapist_notes",
        ]

        for field in required_fields:
            if field not in summary:
                raise ValueError(f"Summary missing required field: {field}")

        risk = summary.get("risk_assessment", {})
        if not isinstance(risk, dict) or "level" not in risk:
            raise ValueError("risk_assessment must be an object with 'level' field")

        valid_risk_levels = ["baixo", "moderado", "alto", "crítico"]
        if risk["level"] not in valid_risk_levels:
            raise ValueError(f"Invalid risk level: {risk['level']}")

        logger.info("Summary validation passed")

    def _calculate_cost(self, tokens_used: Dict[str, int]) -> float:
        input_cost = (tokens_used["input"] / 1_000_000) * 0.150
        output_cost = (tokens_used["output"] / 1_000_000) * 0.600
        return input_cost + output_cost

    def estimate_summary_cost(self, transcript_length: int) -> float:
        estimated_input_tokens = transcript_length / 4
        estimated_output_tokens = 1000

        input_cost = (estimated_input_tokens / 1_000_000) * 0.150
        output_cost = (estimated_output_tokens / 1_000_000) * 0.600

        return input_cost + output_cost
