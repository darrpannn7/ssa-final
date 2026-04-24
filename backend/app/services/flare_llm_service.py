"""
flare_llm_service.py
--------------------
Loads the fine-tuned LoRA adapter for solar flare prediction.
Falls back to Groq LLaMA 3.3 70B if local model is not found.

Drop this file into:
    backend/app/services/flare_llm_service.py
"""

import os
import re
import logging
import threading
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# ── Model path ─────────────────────────────────────────────────────
LORA_PATH   = os.getenv("FLARE_MODEL_PATH", "models/flare-llama-lora")
BASE_MODEL  = "meta-llama/Llama-3.1-8B-Instruct"
GROQ_MODEL  = "llama-3.3-70b-versatile"

# ── Singleton ──────────────────────────────────────────────────────
_model     = None
_tokenizer = None
_lock      = threading.Lock()
_use_local = False


# ── Response type ──────────────────────────────────────────────────

@dataclass
class FlarePredicton:
    predicted_class:       str    # no_flare | A | B | C | M | X
    confidence:            str    # low | medium | high
    onset_window_minutes:  int    # estimated onset in minutes
    reasoning:             str
    model_source:          str    # fine-tuned-llama | groq-fallback


# ── Loader ─────────────────────────────────────────────────────────

def _load_local_model():
    """
    Tries to load fine-tuned LoRA adapter.
    Returns (model, tokenizer) or (None, None).
    """
    if not os.path.exists(LORA_PATH):
        logger.info(f"LoRA path not found: {LORA_PATH} — will use Groq fallback")
        return None, None

    try:
        # Try Unsloth first (fastest)
        try:
            from unsloth import FastLanguageModel
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=LORA_PATH,
                max_seq_length=512,
                load_in_4bit=True,
                dtype=None,
            )
            FastLanguageModel.for_inference(model)
            logger.info("✅ Fine-tuned model loaded via Unsloth")
            return model, tokenizer
        except ImportError:
            pass

        # Fallback: standard HuggingFace PEFT
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel
        import torch

        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        tokenizer = AutoTokenizer.from_pretrained(LORA_PATH)
        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=bnb,
            device_map="auto",
        )
        model = PeftModel.from_pretrained(base, LORA_PATH)
        model.eval()
        logger.info("✅ Fine-tuned model loaded via PEFT")
        return model, tokenizer

    except Exception:
        logger.exception("Failed to load local fine-tuned model")
        return None, None


def _get_model():
    global _model, _tokenizer, _use_local
    if _model is None:
        with _lock:
            if _model is None:
                m, t = _load_local_model()
                if m is not None:
                    _model     = m
                    _tokenizer = t
                    _use_local = True
                else:
                    _model     = "groq"
                    _use_local = False
    return _model, _tokenizer, _use_local


# ── Prompt builder ─────────────────────────────────────────────────

def _build_prompt(
    flux_window:               list[float],
    peak_flux:                 float,
    sunspot_count:             int,
    wind_speed:                float,
    bz:                        float,
    surya_flare_risk:          str,
    surya_magnetic_complexity: float,
) -> str:
    flux_str = ", ".join(f"{v:.3e}" for v in flux_window)

    arr = np.array(flux_window)
    diff = arr[-1] - arr[0] if len(arr) > 1 else 0
    if diff > arr[0] * 0.3:
        trend = "rising"
    elif diff < -arr[0] * 0.3:
        trend = "falling"
    else:
        trend = "stable"

    return (
        f"GOES X-ray flux (last 60 min, W/m²): [{flux_str}]\n"
        f"Peak flux: {peak_flux:.3e}\n"
        f"Trend: {trend}\n"
        f"Sunspot count: {sunspot_count}\n"
        f"Solar wind speed: {wind_speed:.0f} km/s\n"
        f"Bz component: {bz:.1f} nT\n"
        f"Surya flare_risk: {surya_flare_risk}\n"
        f"Surya magnetic_complexity: {surya_magnetic_complexity:.4f}\n"
        f"Predict flare class and estimated onset window."
    )


SYSTEM_PROMPT = (
    "You are a solar flare prediction model. Analyze GOES X-ray flux "
    "time series and space weather indicators to predict solar flare "
    "class. Classes: no_flare, A, B, C, M, X."
)


# ── Response parser ────────────────────────────────────────────────

def _parse_response(text: str) -> dict:
    """
    Parses: 'Flare class: M | Confidence: high | Onset: 15-30 min | Reasoning: ...'
    """
    text = text.strip()

    # Extract class
    cls_match = re.search(r"flare class:\s*(\w+)", text, re.IGNORECASE)
    predicted_class = cls_match.group(1) if cls_match else "no_flare"
    if predicted_class.lower() not in {"no_flare", "a", "b", "c", "m", "x"}:
        predicted_class = "no_flare"
    else:
        predicted_class = predicted_class.upper() if predicted_class.lower() != "no_flare" else "no_flare"

    # Extract confidence
    conf_match = re.search(r"confidence:\s*(\w+)", text, re.IGNORECASE)
    confidence = conf_match.group(1).lower() if conf_match else "medium"

    # Extract onset minutes (take first number found)
    onset_match = re.search(r"onset:\s*(\d+)", text, re.IGNORECASE)
    onset_minutes = int(onset_match.group(1)) if onset_match else 30

    # Extract reasoning
    reason_match = re.search(r"reasoning:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    reasoning = reason_match.group(1).strip()[:300] if reason_match else text[:300]

    return {
        "predicted_class":      predicted_class,
        "confidence":           confidence,
        "onset_window_minutes": onset_minutes,
        "reasoning":            reasoning,
    }


# ── Local inference ────────────────────────────────────────────────

def _infer_local(model, tokenizer, prompt: str) -> str:
    import torch

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        text = f"<|SYSTEM|>\n{SYSTEM_PROMPT}\n<|USER|>\n{prompt}\n<|ASSISTANT|>\n"

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=450)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    decoded = tokenizer.decode(out[0], skip_special_tokens=True)
    # Return only the newly generated part
    if "<|ASSISTANT|>" in decoded:
        return decoded.split("<|ASSISTANT|>")[-1].strip()
    return decoded[len(text):].strip()


# ── Groq fallback ──────────────────────────────────────────────────

def _infer_groq(prompt: str) -> str:
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.2,
        max_tokens=200,
    )
    return resp.choices[0].message.content


# ── Public API ─────────────────────────────────────────────────────

def predict_flare(
    flux_window:               list[float],
    sunspot_count:             int   = 20,
    wind_speed:                float = 400.0,
    bz:                        float = 0.0,
    surya_flare_risk:          str   = "Low — C-class or below",
    surya_magnetic_complexity: float = 0.0,
) -> FlarePredicton:
    """
    Main entry point for flare prediction.
    
    Args:
        flux_window: List of 12 GOES X-ray flux values (W/m²), 5-min cadence
        sunspot_count: Current sunspot number
        wind_speed: Solar wind speed in km/s
        bz: IMF Bz component in nT
        surya_flare_risk: Surya ViT flare risk string
        surya_magnetic_complexity: Surya ViT magnetic complexity score

    Returns:
        FlarePredicton dataclass with class, confidence, onset, reasoning
    """
    if not flux_window:
        flux_window = [1e-7] * 12

    peak_flux = max(flux_window)
    prompt = _build_prompt(
        flux_window=flux_window,
        peak_flux=peak_flux,
        sunspot_count=sunspot_count,
        wind_speed=wind_speed,
        bz=bz,
        surya_flare_risk=surya_flare_risk,
        surya_magnetic_complexity=surya_magnetic_complexity,
    )

    model, tokenizer, use_local = _get_model()

    try:
        if use_local:
            raw = _infer_local(model, tokenizer, prompt)
            source = "fine-tuned-llama-3.1-8b-lora"
        else:
            raw = _infer_groq(prompt)
            source = "groq-llama-3.3-70b-fallback"
    except Exception:
        logger.exception("Inference failed")
        raw = "Flare class: no_flare | Confidence: low | Onset: N/A | Reasoning: Inference error."
        source = "error"

    parsed = _parse_response(raw)
    return FlarePredicton(
        predicted_class=parsed["predicted_class"],
        confidence=parsed["confidence"],
        onset_window_minutes=parsed["onset_window_minutes"],
        reasoning=parsed["reasoning"],
        model_source=source,
    )
