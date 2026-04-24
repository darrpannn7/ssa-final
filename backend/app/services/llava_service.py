import base64
import logging
import os
from groq import Groq

logger = logging.getLogger(__name__)


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def analyze_with_llava(image_bytes: bytes, user_prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set.")

    client = Groq(api_key=api_key)
    b64    = encode_image(image_bytes)

    system_prompt = """You are an expert solar physicist specialising in:
- HMI magnetogram interpretation
- Solar active region classification (α, β, βγ, βγδ)
- Solar flare prediction (GOES A / B / C / M / X class)
- Space weather forecasting

When shown an HMI magnetogram:
- Bright white patches = strong positive magnetic polarity
- Dark/black patches   = strong negative magnetic polarity
- Gray background      = quiet Sun

Always be structured, precise, and scientific."""

    vision_prompt = f"""Analyse this HMI (Helioseismic and Magnetic Imager)
magnetogram from NASA SDO.

User request: {user_prompt}

Structure your response exactly as:

## Active Regions Detected
For each visible active region:
- **Location**: approximate disk position (N/S, E/W)
- **Polarity class**: α / β / βγ / βγδ
- **Flare risk**: expected GOES class (A/B/C/M/X)
- **Confidence**: Low / Medium / High
- **Reasoning**: brief explanation

## Overall Assessment
- Activity level: Quiet / Active / Intense
- Most dangerous region and why
- 24h / 48h / 72h flare probability

## Space Weather Impact
- Estimated Kp index
- Risk to satellites / GPS / HF radio
- Earth-directed CME likelihood"""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}"
                            },
                        },
                        {
                            "type": "text",
                            "text": vision_prompt,
                        },
                    ],
                },
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    except Exception:
        logger.exception("LLaVA call failed")
        raise