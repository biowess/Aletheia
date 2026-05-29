import json
import logging
from typing import Dict, Any

from app.reasoning.providers.base import BaseAIProvider
from app.reasoning.parser import ReasoningResponseParser

logger = logging.getLogger(__name__)

ENHANCEMENT_SYSTEM_PROMPT = """You are a senior clinical education tutor. Your task is to refine the language and phrasing of a clinical reasoning report so the output sounds more academically cautious, more natural, and more pedagogically accurate.
Do NOT change any medical facts, clinical findings, evidence scores, or citation tokens (e.g. {{cite:c1}}).
Do NOT change the structure of the JSON. Do NOT remove or add any list items.

LANGUAGE RULES:
1. Replace overly definitive medical language with cautious educational phrasing.
   Use: "consistent with", "suggestive of", "raises concern for", "supports", "highly compatible with", "needs confirmation", "remains a consideration", "is less likely", "cannot yet be confirmed".
2. Avoid overclaiming.
   Do NOT use: "diagnostic for", "confirmed", "proves", "rules in", "definitive diagnosis", "pathognomonic" unless the existing evidence layer already explicitly supports that level of certainty.
3. Preserve uncertainty. When evidence is incomplete, the text must acknowledge that the conclusion is provisional. Do not smooth away uncertainty into a final-sounding statement.
4. Keep educational framing. The output should sound like it is teaching clinical reasoning, not giving clinical orders. Recommendations should be phrased as educational next steps or urgent specialist review where appropriate.
5. Make transitions natural. The report should read smoothly and professionally.
6. Reduce repetitive phrasing. Vary sentence structure so the report does not sound templated or robotic. Avoid repeating "strongly suggests" too often. Avoid overusing "classic" unless it is genuinely useful.
7. Make differential language balanced. Phrase certainty proportionally (e.g., "likely", "possible", "lower probability", "important to monitor", "not fully supported", "cannot be excluded yet").
8. Keep severity language measured. Use: "high concern", "urgent", "potentially serious", "high-risk scenario" rather than dramatic or alarmist wording.

Return a valid JSON object matching the input structure exactly, but with the text fields enhanced according to the rules above.
"""

class LanguageEnhancementService:
    def __init__(self, provider: BaseAIProvider, parser: ReasoningResponseParser):
        self.provider = provider
        self.parser = parser

    async def enhance_report_language(self, parsed_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies a language pass over the assembled reasoning output to make it 
        more academically cautious and pedagogically accurate.
        """
        # Save original citations to ensure they are untouched
        original_citations = parsed_response.get("citations", [])
        
        # Prepare payload without citations to reduce context size and prevent modification
        payload_to_enhance = {k: v for k, v in parsed_response.items() if k != "citations"}
        
        prompt = f"""Please enhance the text fields of the following clinical reasoning report JSON according to the system instructions.
Return ONLY valid JSON matching the exact same schema structure.

Original JSON:
{json.dumps(payload_to_enhance, indent=2)}
"""
        try:
            enhanced_text = await self.provider.complete(prompt, system=ENHANCEMENT_SYSTEM_PROMPT)
            enhanced_parsed = self.parser.parse_reasoning_response(enhanced_text)
            
            # Restore original citations exactly as they were
            enhanced_parsed["citations"] = original_citations
            
            return enhanced_parsed
        except Exception as e:
            logger.error(f"Language enhancement failed, falling back to original: {e}")
            return parsed_response
