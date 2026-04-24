import os
import logging
import numpy as np
from groq import Groq

from app.services.surya_service import analyze_multichannel
from app.services.llava_service import analyze_with_llava

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is not set.")
        self.client = Groq(api_key=api_key)
        self.model  = "llama-3.3-70b-versatile"

    def chat(
        self,
        message:     str,
        image_stack: np.ndarray | None = None,
        image_bytes: bytes | None      = None,
    ) -> dict:

        # ── Step 1: Surya embedding (always runs) ──────────────────
        surya_data = None
        if image_stack is not None:
            try:
                surya_data = analyze_multichannel(image_stack)
            except Exception:
                logger.exception("Surya inference failed")

        # ── Step 2: LLaVA visual analysis (only if image uploaded) ─
        if image_bytes is not None:
            try:
                llava_text = analyze_with_llava(image_bytes, message)
                # Combine LLaVA visual output with Surya metrics
                final_text = self._combine_outputs(llava_text, surya_data)
                return {
                    "text":       final_text,
                    "surya_data": surya_data,
                    "source":     "llava+surya",
                }
            except Exception:
                logger.exception("LLaVA failed — falling back to Groq+Surya")
                # Fall through to Groq text path below

        # ── Step 3: Groq text path (no image / LLaVA failed) ───────
        prompt = self._build_prompt(message, surya_data)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert in solar physics, "
                            "space weather, and heliophysics."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            return {
                "text":       resp.choices[0].message.content,
                "surya_data": surya_data,
                "source":     "groq+surya",
            }
        except Exception:
            logger.exception("Groq call failed")
            return {
                "text":       "Both LLaVA and Groq are unavailable. Please retry.",
                "surya_data": surya_data,
                "source":     "error",
            }

    # ── Helpers ────────────────────────────────────────────────────

    def _combine_outputs(self, llava_text: str, surya_data: dict | None) -> str:
        """Append Surya metrics below the LLaVA visual analysis."""
        if not surya_data:
            return llava_text

        surya_block = f"""
---
## Surya ViT Embedding Metrics
| Metric | Value |
|---|---|
| Intensity | {surya_data['intensity']} |
| Magnetic complexity | {surya_data['magnetic_complexity']} |
| Flare risk (embedding) | {surya_data['flare_risk']} |
| Embedding dim | {surya_data['embedding_dim']} |

> Note: Surya metrics are derived from replicated single-channel input.
> True multi-channel SDO inference requires 13 aligned AIA+HMI channels.
"""
        return llava_text + surya_block

    def _build_prompt(self, message: str, surya_data: dict | None) -> str:
        if not surya_data:
            return message
        return f"""You are analysing solar observations from NASA SDO.

User question: {message}

Surya ViT embedding output:
- Intensity            : {surya_data['intensity']}
- Magnetic complexity  : {surya_data['magnetic_complexity']}
- Flare risk           : {surya_data['flare_risk']}
- Embedding dim        : {surya_data['embedding_dim']}

Provide a structured scientific explanation covering:
1. Magnetic field structure indicated by these values
2. Expected flare class (A/B/C/M/X) with reasoning
3. Active region morphology (α, β, βγ, βγδ)
4. Geomagnetic impact: Kp index, satellite/GPS/HF radio risk
5. Recommended monitoring cadence"""