"""
Insight Service - Generate AI insights using Claude API
"""

import os
from typing import Optional
from anthropic import Anthropic
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class InsightService:
    """Service for generating market insights using Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Insight Service.

        Args:
            api_key: Claude API key (defaults to CLAUDE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            logger.warning("Claude API key not set. Insights will be disabled.")
            self.client = None
        else:
            self.client = Anthropic(api_key=self.api_key)

    def generate_insight(
        self,
        market_title: str,
        old_prob: float,
        new_prob: float,
        delta_pct: float,
        window_minutes: int,
        volume_delta: Optional[float] = None,
        time_to_resolution: Optional[str] = None,
        user_name: str = "Yash",
        signal_summary: Optional[str] = None,
        long_term_trend: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an insight for a market movement using Claude.

        Args:
            market_title: The market question/title
            old_prob: Previous implied probability (0-100)
            new_prob: New implied probability (0-100)
            delta_pct: Percentage change
            window_minutes: Time window in minutes
            volume_delta: Change in volume (optional)
            time_to_resolution: Time remaining until market resolves (optional)
            user_name: User name for personalization (default: "Yash")
            signal_summary: External signal summary (optional, for future integration)
            long_term_trend: Historical trend analysis (optional)

        Returns:
            Generated insight text or None if disabled/error
        """
        if not self.client:
            logger.warning("Claude client not initialized. Skipping insight generation.")
            return None

        try:
            # Build the enhanced prompt template
            volume_text = f"\nVolume change: {volume_delta:+.2f}" if volume_delta else ""
            ttr_text = f"\nTime to resolution: {time_to_resolution}" if time_to_resolution else ""
            signal_text = f"\nExternal signal (optional): {signal_summary}" if signal_summary else ""
            trend_text = f"\n\nLong-term trend from history: {long_term_trend}" if long_term_trend else ""

            user_prompt = f"""User: {user_name}
Market: "{market_title}"
Time window: last {window_minutes} minutes
Implied probability: {old_prob:.1f}% → {new_prob:.1f}% (Δ {delta_pct:+.1f}%){volume_text}{ttr_text}{signal_text}{trend_text}

Consider external factors and market context when analyzing this move. In 3–5 sentences: explain plausible drivers of the move, 2 risks to watch, and a neutral note (not financial advice)."""

            # Call Claude API with enhanced prompt
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                system="You are an analyst for prediction markets. Be concise and neutral.",
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Extract the text response
            if message.content and len(message.content) > 0:
                insight_text = message.content[0].text
                logger.info(f"Generated insight for {user_name} on market: {market_title[:50]}...")
                return insight_text
            else:
                logger.warning("Claude API returned empty response")
                return None

        except Exception as e:
            logger.error(f"Error generating insight with Claude: {e}")
            return None

    def generate_insight_from_history(
        self,
        market_title: str,
        old_snapshot: dict,
        new_snapshot: dict,
        window_minutes: int,
        time_to_resolution: Optional[str] = None,
        user_name: str = "Yash",
        signal_summary: Optional[str] = None,
        long_term_trend: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate insight from two market snapshots (simplified API).

        Args:
            market_title: The market question/title
            old_snapshot: Previous snapshot with 'implied_prob' and 'volume'
            new_snapshot: New snapshot with 'implied_prob' and 'volume'
            window_minutes: Time window between snapshots
            time_to_resolution: Time until resolution (optional)
            user_name: User name for personalization (default: "Yash")
            signal_summary: External signal summary (optional)
            long_term_trend: Historical trend analysis (optional)

        Returns:
            Generated insight text or None
        """
        old_prob = old_snapshot.get("implied_prob", 0)
        new_prob = new_snapshot.get("implied_prob", 0)
        delta_pct = new_prob - old_prob

        old_vol = old_snapshot.get("volume", 0)
        new_vol = new_snapshot.get("volume", 0)
        volume_delta = new_vol - old_vol if old_vol > 0 else None

        return self.generate_insight(
            market_title=market_title,
            old_prob=old_prob,
            new_prob=new_prob,
            delta_pct=delta_pct,
            window_minutes=window_minutes,
            volume_delta=volume_delta,
            time_to_resolution=time_to_resolution,
            user_name=user_name,
            signal_summary=signal_summary,
            long_term_trend=long_term_trend,
        )


# Singleton instance
_insight_service: Optional[InsightService] = None


def get_insight_service() -> InsightService:
    """Get or create the Insight service instance"""
    global _insight_service
    if _insight_service is None:
        _insight_service = InsightService()
    return _insight_service
