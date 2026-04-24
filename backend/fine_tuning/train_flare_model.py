"""
train_flare_model.py
--------------------
QLoRA fine-tuning for solar flare detection on LLaMA 3.1 8B.

Usage:
    python train_flare_model.py --config finetune_config.yaml

Requirements:
    pip install unsloth trl peft bitsandbytes datasets transformers accelerate
"""

import os
import json
import yaml
import argparse
import numpy as np
from pathlib import Path
from collections import Counter
from sklearn.metrics import confusion_matrix

# ── Try Unsloth first (2-5x faster), fall back to standard HF ──────
try:
    from unsloth import FastLanguageModel
    UNSLOTH_AVAILABLE = True
    print("✅ Using Unsloth for fast fine-tuning")
except ImportError:
    UNSLOTH_AVAILABLE = False
    print("⚠ Unsloth not available — using standard HuggingFace PEFT")

from datasets import Dataset
from transformers import TrainingArguments, AutoTokenizer, AutoModelForCausalLM
from trl import SFTTrainer


FLARE_CLASSES = ["no_flare", "A", "B", "C", "M", "X"]


# ── Config loader ──────────────────────────────────────────────────

def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


# ── Dataset ────────────────────────────────────────────────────────

def load_jsonl(path: str) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def format_prompt(record: dict, tokenizer) -> str:
    """
    Converts a JSONL record into a single chat-formatted string.
    Uses tokenizer's chat template if available.
    """
    messages = record["messages"]
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
    except Exception:
        # Fallback: manual formatting
        parts = []
        for m in messages:
            role    = m["role"].upper()
            content = m["content"]
            parts.append(f"<|{role}|>\n{content}")
        return "\n".join(parts) + "\n<|END|>"


def build_hf_dataset(records: list[dict], tokenizer, eval_split: float):
    texts = [format_prompt(r, tokenizer) for r in records]
    labels = [r["metadata"]["actual_class"] for r in records]

    full = Dataset.from_dict({"text": texts, "label": labels})
    split = full.train_test_split(test_size=eval_split, seed=42)
    return split["train"], split["test"]


# ── Model loading ──────────────────────────────────────────────────

def load_model_and_tokenizer(cfg: dict):
    model_name   = cfg["model_name"]
    load_in_4bit = cfg.get("load_in_4bit", True)
    max_seq_len  = cfg.get("max_seq_length", 512)

    if UNSLOTH_AVAILABLE:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_len,
            load_in_4bit=load_in_4bit,
            dtype=None,  # auto-detect
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=cfg["lora_r"],
            lora_alpha=cfg["lora_alpha"],
            lora_dropout=cfg["lora_dropout"],
            target_modules=cfg["target_modules"],
            bias=cfg.get("bias", "none"),
            use_gradient_checkpointing="unsloth",
            random_state=cfg.get("seed", 42),
        )
    else:
        from transformers import BitsAndBytesConfig
        import torch
        from peft import get_peft_model, LoraConfig, TaskType

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=load_in_4bit,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
        )

        lora_config = LoraConfig(
            r=cfg["lora_r"],
            lora_alpha=cfg["lora_alpha"],
            lora_dropout=cfg["lora_dropout"],
            target_modules=cfg["target_modules"],
            bias=cfg.get("bias", "none"),
            task_type=TaskType.CAUSAL_LM,
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return model, tokenizer


# ── Evaluation ─────────────────────────────────────────────────────

def extract_predicted_class(text: str) -> str:
    """Parse 'Flare class: X | ...' from model output."""
    text = text.lower()
    for cls in ["x", "m", "c", "b", "a"]:
        if f"flare class: {cls}" in text:
            return cls.upper()
    if "no_flare" in text:
        return "no_flare"
    return "no_flare"


def compute_skill_scores(y_true: list, y_pred: list) -> dict:
    """
    Compute TSS and HSS for binary M+X vs rest classification.
    These are the standard metrics in solar flare prediction research.
    """
    # Binary: positive = M or X class
    positive = {"M", "X"}
    y_true_bin = [1 if c in positive else 0 for c in y_true]
    y_pred_bin = [1 if c in positive else 0 for c in y_pred]

    tp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 1 and p == 0)

    # TSS = TPR - FPR
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tss = round(tpr - fpr, 4)

    # HSS
    n = tp + tn + fp + fn
    expected = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / n if n > 0 else 0
    hss = round((tp + tn - expected) / (n - expected), 4) if (n - expected) > 0 else 0.0

    # FAR and POD
    far = round(fp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    pod = round(tpr, 4)

    return {
        "TSS": tss,
        "HSS": hss,
        "FAR": far,
        "POD": pod,
        "TP":  tp, "TN": tn, "FP": fp, "FN": fn,
    }


# ── Main ───────────────────────────────────────────────────────────

def train(config_path: str):
    cfg = load_config(config_path)
    print(f"\n{'='*50}")
    print(f"Model : {cfg['model_name']}")
    print(f"Data  : {cfg['dataset_path']}")
    print(f"Output: {cfg['output_dir']}")
    print(f"{'='*50}\n")

    # Load model
    model, tokenizer = load_model_and_tokenizer(cfg)

    # Load dataset
    records = load_jsonl(cfg["dataset_path"])
    print(f"Loaded {len(records)} training records")

    dist = Counter(r["metadata"]["actual_class"] for r in records)
    print(f"Class distribution: {dict(dist)}\n")

    train_ds, eval_ds = build_hf_dataset(records, tokenizer, cfg["eval_split"])
    print(f"Train: {len(train_ds)} | Eval: {len(eval_ds)}")

    # Training args
    output_dir = cfg["output_dir"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=cfg["num_train_epochs"],
        per_device_train_batch_size=cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=cfg["gradient_accumulation_steps"],
        learning_rate=cfg["learning_rate"],
        warmup_ratio=cfg.get("warmup_ratio", 0.05),
        lr_scheduler_type=cfg.get("lr_scheduler_type", "cosine"),
        optim=cfg.get("optim", "adamw_8bit"),
        bf16=cfg.get("bf16", True),
        fp16=cfg.get("fp16", False),
        logging_steps=cfg.get("logging_steps", 10),
        save_steps=cfg.get("save_steps", 100),
        eval_strategy="steps",
        eval_steps=cfg.get("eval_steps", 50),
        seed=cfg.get("seed", 42),
        report_to=cfg.get("report_to", "none"),
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        dataset_text_field="text",
        max_seq_length=cfg["max_seq_length"],
        args=training_args,
    )

    print("\nStarting training...\n")
    trainer.train()

    # Save LoRA adapter
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"\n✅ LoRA adapter saved to {output_dir}")

    # Quick eval on held-out set
    print("\nRunning evaluation on held-out set...")
    if UNSLOTH_AVAILABLE:
        FastLanguageModel.for_inference(model)

    y_true, y_pred = [], []
    for sample in eval_ds.select(range(min(100, len(eval_ds)))):
        true_label = sample["label"]
        text = sample["text"]
        # Strip assistant turn to get prompt only
        prompt = text.split("<|ASSISTANT|>")[0] if "<|ASSISTANT|>" in text else text

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=400)
        import torch
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=60,
                temperature=0.1,
                do_sample=False,
            )
        decoded = tokenizer.decode(out[0], skip_special_tokens=True)
        pred_label = extract_predicted_class(decoded)
        y_true.append(true_label)
        y_pred.append(pred_label)

    scores = compute_skill_scores(y_true, y_pred)
    print(f"\n{'='*40}")
    print("Evaluation Results (M+X binary):")
    for k, v in scores.items():
        print(f"  {k}: {v}")
    print(f"{'='*40}\n")

    # Save scores
    scores_path = os.path.join(output_dir, "eval_scores.json")
    with open(scores_path, "w") as f:
        json.dump(scores, f, indent=2)
    print(f"Scores saved to {scores_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="finetune_config.yaml")
    args = parser.parse_args()
    train(args.config)
