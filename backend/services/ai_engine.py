import os
from typing import Dict, List, Any

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai  # type: ignore[import]
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
except ImportError:
    genai = None  # type: ignore[assignment]
    GEMINI_AVAILABLE = False


def generate_ai_summary(
    metrics,
    risk_data,
    investor_data,
    esg_data,
    warnings,
    fraud_flags,
    language: str = "en",
) -> Dict[str, Any]:
    """
    AI CFO Narrative & Recommendation Engine.

    Phase 2+3 upgrade:
        Returns structured JSON with:
        {
          strategic_actions: [],
          cost_optimization: [],
          liquidity_improvements: [],
          funding_recommendations: []
        }
    """

    # Normalize language; default to English, support Hindi.
    lang = (language or "en").lower()
    if lang not in ("en", "hi"):
        lang = "en"

    lang_instruction = (
        "Write recommendations in clear, simple English."
        if lang == "en"
        else "Write recommendations in clear, simple Hindi (use Devanagari script)."
    )

    prompt = f"""
You are an AI CFO for SMEs.

Given the following data:
- Financial Metrics: {metrics}
- Risk Analysis: {risk_data}
- Investor Readiness: {investor_data}
- ESG Score: {esg_data}
- Warnings: {warnings}
- Fraud Flags: {fraud_flags}

Provide a structured JSON object with four arrays. {lang_instruction}
{{
  "strategic_actions": [
    "High-level strategic recommendation 1",
    "High-level strategic recommendation 2"
  ],
  "cost_optimization": [
    "Concrete, finance-aware cost optimization idea"
  ],
  "liquidity_improvements": [
    "Action to improve short-term liquidity"
  ],
  "funding_recommendations": [
    "Recommendation on equity / debt / alternative funding"
  ]
}}

Respond with ONLY valid JSON, no additional commentary.
"""

    try:
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Gemini API not configured or library not installed.")

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        content = response.text or "{}"

        # Best-effort JSON parsing with safe fallback.
        import json

        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {
                "strategic_actions": [content],
                "cost_optimization": [],
                "liquidity_improvements": [],
                "funding_recommendations": [],
            }

        # Ensure all expected keys are present.
        def _ensure_list(value) -> List[str]:
            if isinstance(value, list):
                return [str(v) for v in value]
            if value is None:
                return []
            return [str(value)]

        return {
            "strategic_actions": _ensure_list(parsed.get("strategic_actions")),
            "cost_optimization": _ensure_list(parsed.get("cost_optimization")),
            "liquidity_improvements": _ensure_list(parsed.get("liquidity_improvements")),
            "funding_recommendations": _ensure_list(parsed.get("funding_recommendations")),
        }

    except Exception as e:
        # Handle Gemini API errors (or missing config) gracefully
        error_str = str(e)
        
        # Check for quota/billing errors
        if "429" in error_str or "insufficient_quota" in error_str or "quota" in error_str.lower():
            fallback_msg = (
                "AI recommendations are temporarily unavailable due to API quota limits. "
                "Please check your OpenAI account billing or contact support. "
                "Financial analysis and other features remain fully functional."
            )
        elif "401" in error_str or "invalid" in error_str.lower() or "authentication" in error_str.lower():
            fallback_msg = (
                "AI recommendations are unavailable due to API authentication issues. "
                "Please verify your OpenAI API key configuration."
            )
        else:
            fallback_msg = (
                "AI recommendations are temporarily unavailable. "
                "Financial analysis and other features remain fully functional."
            )
        
        # Return structured fallback with rule-based recommendations
        net_margin = metrics.get("net_margin", 0) if isinstance(metrics, dict) else 0
        current_ratio = metrics.get("current_ratio", 0) if isinstance(metrics, dict) else 0
        debt_to_equity = metrics.get("debt_to_equity", 0) if isinstance(metrics, dict) else 0
        
        rule_based_recommendations = []
        
        if net_margin < 5:
            rule_based_recommendations.append("Focus on improving profitability margins through cost optimization or revenue growth.")
        if current_ratio < 1:
            rule_based_recommendations.append("Address liquidity concerns by improving working capital management.")
        if debt_to_equity > 2:
            rule_based_recommendations.append("Consider reducing leverage to improve financial stability.")
        
        if not rule_based_recommendations:
            rule_based_recommendations.append("Continue monitoring key financial metrics and maintain current operational efficiency.")
        
        return {
            "strategic_actions": rule_based_recommendations,
            "cost_optimization": ["Review expense categories for optimization opportunities."] if net_margin < 10 else [],
            "liquidity_improvements": ["Improve cash flow management and working capital efficiency."] if current_ratio < 1.5 else [],
            "funding_recommendations": ["Evaluate funding options based on current risk profile and growth needs."],
            "_ai_unavailable": True,
            "_fallback_message": fallback_msg,
        }
