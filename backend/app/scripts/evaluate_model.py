"""
evaluate_model.py
-----------------
Runs the test split of flare_dataset.jsonl through the inference service
and computes TSS, HSS, FAR, POD + confusion matrix.

Usage:
    python evaluate_model.py --dataset data/flare_dataset.jsonl --output data/eval_report.json
"""

import json
import argparse
import numpy as np
from collections import Counter
from pathlib import Path

# Add project root to path so we can import the service
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


FLARE_CLASSES = ["no_flare", "A", "B", "C", "M", "X"]
POSITIVE_CLASSES = {"M", "X"}


# ── Metrics ────────────────────────────────────────────────────────

def compute_binary_metrics(y_true: list[str], y_pred: list[str]) -> dict:
    """TSS, HSS, FAR, POD for M+X vs rest (binary)."""
    y_t = [1 if c in POSITIVE_CLASSES else 0 for c in y_true]
    y_p = [1 if c in POSITIVE_CLASSES else 0 for c in y_pred]

    tp = sum(1 for a, b in zip(y_t, y_p) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y_t, y_p) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y_t, y_p) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_t, y_p) if a == 1 and b == 0)
    n  = tp + tn + fp + fn

    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tss = round(tpr - fpr, 4)

    expected = (
        ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / n
    ) if n > 0 else 0
    hss = round((tp + tn - expected) / (n - expected), 4) if (n - expected) > 0 else 0.0

    far = round(fp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    pod = round(tpr, 4)
    acc = round((tp + tn) / n, 4) if n > 0 else 0.0

    return {
        "TSS": tss, "HSS": hss,
        "FAR": far, "POD": pod,
        "Accuracy": acc,
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
    }


def compute_confusion_matrix(y_true: list[str], y_pred: list[str]) -> dict:
    labels = [c for c in FLARE_CLASSES if c in set(y_true + y_pred)]
    matrix = {}
    for true_cls in labels:
        matrix[true_cls] = {}
        for pred_cls in labels:
            count = sum(
                1 for t, p in zip(y_true, y_pred)
                if t == true_cls and p == pred_cls
            )
            matrix[true_cls][pred_cls] = count
    return matrix


def per_class_accuracy(y_true: list[str], y_pred: list[str]) -> dict:
    result = {}
    for cls in FLARE_CLASSES:
        total = sum(1 for t in y_true if t == cls)
        if total == 0:
            continue
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        result[cls] = round(correct / total, 4)
    return result


# ── Dataset loader ─────────────────────────────────────────────────

def load_test_split(path: str, eval_fraction: float = 0.1) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    # Same split as training (seed=42, last eval_fraction%)
    n_eval = max(1, int(len(records) * eval_fraction))
    # Deterministic: take last n_eval records (matches sklearn train_test_split behavior)
    return records[-n_eval:]


# ── Inference ─────────────────────────────────────────────────────

def extract_predicted_class(text: str) -> str:
    """Parse 'Flare class: X | ...' from model output."""
    import re
    text = text.lower()
    m = re.search(r"flare class:\s*(\S+)", text)
    if m:
        cls = m.group(1).strip("|").strip().upper()
        if cls == "NO_FLARE" or cls.lower() == "no_flare":
            return "no_flare"
        if cls in {"X", "M", "C", "B", "A"}:
            return cls
    return "no_flare"


def run_inference(records: list[dict], use_service: bool = True) -> tuple[list, list]:
    """
    Runs predictions on test records.
    If use_service=True, imports the actual flare_llm_service (requires model).
    If use_service=False, uses Groq directly (useful for eval without local model).
    """
    y_true, y_pred = [], []

    if use_service:
        try:
            from app.services.flare_llm_service import predict_flare
        except ImportError:
            print("⚠ Could not import flare_llm_service — running Groq-only eval")
            use_service = False

    for i, record in enumerate(records):
        true_label = record["metadata"]["actual_class"]
        y_true.append(true_label)

        if use_service:
            try:
                # Extract flux values from the user message
                user_content = record["messages"][1]["content"]
                import re
                flux_match = re.search(r"\[([^\]]+)\]", user_content)
                if flux_match:
                    flux_window = [float(x.strip()) for x in flux_match.group(1).split(",")]
                else:
                    flux_window = [1e-7] * 12

                result = predict_flare(flux_window=flux_window)
                y_pred.append(result.predicted_class)
            except Exception as e:
                print(f"  Sample {i}: inference error — {e}")
                y_pred.append("no_flare")
        else:
            # Naive baseline: predict class from peak flux threshold
            import re
            user_content = record["messages"][1]["content"]
            peak_match = re.search(r"Peak flux: ([0-9.e+\-]+)", user_content)
            if peak_match:
                peak = float(peak_match.group(1))
                if peak >= 1e-4:   pred = "X"
                elif peak >= 1e-5: pred = "M"
                elif peak >= 1e-6: pred = "C"
                elif peak >= 1e-7: pred = "B"
                else:              pred = "no_flare"
            else:
                pred = "no_flare"
            y_pred.append(pred)

        if (i + 1) % 50 == 0:
            print(f"  Evaluated {i+1}/{len(records)} samples...")

    return y_true, y_pred


# ── Main ───────────────────────────────────────────────────────────

def evaluate(dataset_path: str, output_path: str, use_service: bool):
    print(f"\nLoading test split from {dataset_path}...")
    records = load_test_split(dataset_path)
    print(f"Test samples: {len(records)}")

    dist = Counter(r["metadata"]["actual_class"] for r in records)
    print(f"True class distribution: {dict(dist)}\n")

    print("Running inference...")
    y_true, y_pred = run_inference(records, use_service=use_service)

    pred_dist = Counter(y_pred)
    print(f"Predicted class distribution: {dict(pred_dist)}\n")

    # Compute metrics
    binary_scores = compute_binary_metrics(y_true, y_pred)
    per_class     = per_class_accuracy(y_true, y_pred)
    conf_matrix   = compute_confusion_matrix(y_true, y_pred)

    report = {
        "n_samples":        len(y_true),
        "binary_metrics":   binary_scores,
        "per_class_accuracy": per_class,
        "confusion_matrix": conf_matrix,
        "true_distribution":  dict(Counter(y_true)),
        "pred_distribution":  dict(Counter(y_pred)),
    }

    # Print summary
    print("=" * 50)
    print("EVALUATION RESULTS (M+X binary)")
    print("=" * 50)
    for k, v in binary_scores.items():
        print(f"  {k:12s}: {v}")

    print("\nPer-class accuracy:")
    for cls, acc in per_class.items():
        print(f"  {cls:10s}: {acc:.1%}")

    print("\nConfusion Matrix:")
    labels = list(conf_matrix.keys())
    header = f"{'':12s}" + "".join(f"{l:10s}" for l in labels)
    print(header)
    for true_cls, row in conf_matrix.items():
        row_str = f"{true_cls:12s}" + "".join(f"{row.get(l, 0):10d}" for l in labels)
        print(row_str)
    print("=" * 50)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/flare_dataset.jsonl")
    parser.add_argument("--output",  default="data/eval_report.json")
    parser.add_argument("--no-service", action="store_true",
                        help="Use threshold baseline instead of model (faster)")
    args = parser.parse_args()
    evaluate(args.dataset, args.output, use_service=not args.no_service)
