import torch
import cv2
import numpy as np
import threading
from huggingface_hub import hf_hub_download

device = "cuda" if torch.cuda.is_available() else "cpu"

_model = None
_model_lock = threading.Lock()  # ✅ thread-safe singleton


def load_surya():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                print("🔥 Loading Surya pretrained model...")
                try:
                    weights_path = hf_hub_download(
                        repo_id="nasa-ibm-ai4science/Surya-1.0",
                        filename="surya.366m.v1.pt"
                    )

                    # ── Try to find the real class name ──────────
                    arch = None
                    tried = []

                    # Attempt 1: SuryaModel
                    try:
                        from surya.models.embedding import SuryaModel
                        arch = SuryaModel()
                        tried.append("SuryaModel ✅")
                    except ImportError:
                        tried.append("SuryaModel ❌")

                    # Attempt 2: Surya
                    if arch is None:
                        try:
                            from surya.models.embedding import Surya
                            arch = Surya()
                            tried.append("Surya ✅")
                        except ImportError:
                            tried.append("Surya ❌")

                    # Attempt 3: SuryaEncoder
                    if arch is None:
                        try:
                            from surya.models.embedding import SuryaEncoder
                            arch = SuryaEncoder()
                            tried.append("SuryaEncoder ✅")
                        except ImportError:
                            tried.append("SuryaEncoder ❌")

                    # Attempt 4: load full checkpoint directly
                    if arch is None:
                        print("⚠ No known class found, loading checkpoint directly...")
                        checkpoint = torch.load(
                            weights_path,
                            map_location=device,
                            weights_only=False
                        )
                        # Checkpoint might already be the model
                        if hasattr(checkpoint, 'eval'):
                            checkpoint.eval()
                            _model = checkpoint
                            print("✅ Surya loaded as full model object")
                            return _model
                        else:
                            raise ImportError(
                                f"Could not find model class. Tried: {tried}"
                            )

                    # Load weights into architecture
                    checkpoint = torch.load(
                        weights_path,
                        map_location=device,
                        weights_only=False
                    )
                    if isinstance(checkpoint, dict):
                        key = "state_dict" if "state_dict" in checkpoint else None
                        arch.load_state_dict(
                            checkpoint[key] if key else checkpoint
                        )
                    else:
                        arch = checkpoint

                    arch.eval()
                    _model = arch
                    print(f"✅ Surya loaded. Tried: {tried}")

                except Exception:
                    print("⚠ Surya unavailable — running in mock mode")
                    logger.exception("Surya load failed")
                    _model = "mock"

    return _model


def validate_stack(image_stack: np.ndarray) -> np.ndarray:
    """
    Accepts [C, H, W] numpy array.
    Raises ValueError with a clear message on bad input.
    """
    if not isinstance(image_stack, np.ndarray):
        raise ValueError(
            f"Expected numpy array, got {type(image_stack)}"
        )
    if image_stack.ndim != 3:
        raise ValueError(
            f"Expected 3D array [C, H, W], got shape {image_stack.shape}"
        )
    C, H, W = image_stack.shape
    if C < 1:
        raise ValueError("image_stack must have at least 1 channel")
    if H < 32 or W < 32:
        raise ValueError(
            f"Image too small: ({H}, {W}). Minimum 32×32."
        )
    return image_stack.astype(np.float32)


def preprocess_multichannel(image_stack: np.ndarray) -> torch.Tensor:
    C, H, W = image_stack.shape
    target = 224

    # ✅ Resize each channel independently
    resized = np.stack([
        cv2.resize(image_stack[c], (target, target),
                   interpolation=cv2.INTER_LINEAR)
        for c in range(C)
    ], axis=0)  # [C, 224, 224]

    # ✅ Per-channel z-score normalisation
    mean = resized.mean(axis=(1, 2), keepdims=True)
    std  = resized.std(axis=(1, 2), keepdims=True) + 1e-6
    normalized = (resized - mean) / std

    # ✅ Pad or trim to 13 channels (Surya's expected input)
    TARGET_C = 13
    if C < TARGET_C:
        pad = np.zeros((TARGET_C - C, target, target), dtype=np.float32)
        normalized = np.concatenate([normalized, pad], axis=0)
    elif C > TARGET_C:
        normalized = normalized[:TARGET_C]

    return (
        torch.tensor(normalized)
            .float()
            .unsqueeze(0)   # [1, 13, 224, 224]
            .to(device)
    )


def analyze_multichannel(image_stack: np.ndarray) -> dict:
    model = load_surya()

    # Mock mode — Surya unavailable
    if model == "mock":
        return {
            "intensity":           0.0,
            "magnetic_complexity": 0.0,
            "flare_risk":          "Surya unavailable — LLaVA analysis only",
            "embedding_dim":       0,
        }
    
    image_stack = validate_stack(image_stack)
    model = load_surya()
    tensor = preprocess_multichannel(image_stack)

    with torch.no_grad():
        output = model(tensor)

    embedding = output.cpu().numpy().flatten()
    return interpret_output(embedding)


def interpret_output(embedding: np.ndarray) -> dict:
    intensity = float(np.mean(np.abs(embedding)))
    variance  = float(np.var(embedding))

    # More physically motivated thresholds
    if intensity > 0.7:
        flare = "High — X-class likely"
    elif intensity > 0.45:
        flare = "Moderate — M-class possible"
    else:
        flare = "Low — C-class or below"

    return {
        "intensity":           round(intensity, 4),
        "magnetic_complexity": round(variance,  4),
        "flare_risk":          flare,
        "embedding_dim":       len(embedding),
    }