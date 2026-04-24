import cv2
import numpy as np
import base64
from PIL import Image
import io


def detect_and_annotate(image_bytes: bytes) -> dict:
    """
    Takes raw magnetogram image bytes.
    Detects active regions using contrast thresholding.
    Returns base64 annotated image + region metadata.
    """
    # ── Load image ──────────────────────────────────────────────
    pil   = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img   = np.array(pil)
    gray  = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # ── Detect bright regions (positive polarity) ────────────────
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # ── Detect dark regions (negative polarity) ──────────────────
    _, dark_mask = cv2.threshold(gray, 55, 255, cv2.THRESH_BINARY_INV)

    # ── Morphological cleanup ─────────────────────────────────────
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN,  kernel)
    dark_mask   = cv2.morphologyEx(dark_mask,   cv2.MORPH_CLOSE, kernel)
    dark_mask   = cv2.morphologyEx(dark_mask,   cv2.MORPH_OPEN,  kernel)

    # ── Find contours ─────────────────────────────────────────────
    bright_contours, _ = cv2.findContours(
        bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    dark_contours, _ = cv2.findContours(
        dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    MIN_AREA = 300   # ignore tiny noise blobs
    annotated = img.copy()
    regions   = []
    ar_index  = 1

    # ── Draw bright (positive) regions ───────────────────────────
    for cnt in bright_contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        complexity  = _estimate_complexity(area)
        flare_class = _estimate_flare_class(area, "positive")

        # Cyan box for positive polarity
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 255), 2)
        _draw_label(
            annotated,
            f"AR{ar_index} +{flare_class}",
            x, y,
            color=(0, 255, 255)
        )

        regions.append({
            "id":         f"AR{ar_index}",
            "polarity":   "positive",
            "bbox":       [x, y, w, h],
            "area":       int(area),
            "complexity": complexity,
            "flare_risk": flare_class,
        })
        ar_index += 1

    # ── Draw dark (negative) regions ─────────────────────────────
    for cnt in dark_contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        complexity  = _estimate_complexity(area)
        flare_class = _estimate_flare_class(area, "negative")

        # Orange box for negative polarity
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (255, 140, 0), 2)
        _draw_label(
            annotated,
            f"AR{ar_index} -{flare_class}",
            x, y,
            color=(255, 140, 0)
        )

        regions.append({
            "id":         f"AR{ar_index}",
            "polarity":   "negative",
            "bbox":       [x, y, w, h],
            "area":       int(area),
            "complexity": complexity,
            "flare_risk": flare_class,
        })
        ar_index += 1

    # ── Add legend ────────────────────────────────────────────────
    _draw_legend(annotated)

    # ── Encode to base64 ─────────────────────────────────────────
    _, buffer  = cv2.imencode(".png", cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
    b64_image  = base64.b64encode(buffer).decode("utf-8")

    return {
        "annotated_image": b64_image,   # base64 PNG
        "regions":         regions,
        "total_regions":   len(regions),
    }


# ── Helpers ───────────────────────────────────────────────────────

def _estimate_complexity(area: float) -> str:
    if area > 8000:
        return "βγδ"
    elif area > 4000:
        return "βγ"
    elif area > 1500:
        return "β"
    return "α"


def _estimate_flare_class(area: float, polarity: str) -> str:
    if area > 8000:
        return "X"
    elif area > 4000:
        return "M"
    elif area > 1500:
        return "C"
    return "B"


def _draw_label(img, text: str, x: int, y: int, color: tuple):
    font       = cv2.FONT_HERSHEY_SIMPLEX
    scale      = 0.5
    thickness  = 1
    padding    = 4

    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)

    # Label background
    label_y = max(y - th - padding * 2, 0)
    cv2.rectangle(
        img,
        (x, label_y),
        (x + tw + padding * 2, label_y + th + padding * 2),
        color,
        -1   # filled
    )
    # Label text in black
    cv2.putText(
        img, text,
        (x + padding, label_y + th + padding),
        font, scale,
        (0, 0, 0),
        thickness,
        cv2.LINE_AA
    )


def _draw_legend(img):
    h, w = img.shape[:2]
    legends = [
        ((0, 255, 255), "+ Positive polarity"),
        ((255, 140, 0), "- Negative polarity"),
    ]
    for i, (color, label) in enumerate(legends):
        y = h - 30 + i * 18
        cv2.rectangle(img, (10, y - 10), (24, y + 2), color, -1)
        cv2.putText(
            img, label,
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45,
            color, 1, cv2.LINE_AA
        )