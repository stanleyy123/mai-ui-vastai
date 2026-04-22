import sys
import os
sys.path.insert(0, "/app/MAI-UI/src")

from mai_grounding_agent import MAIGroundingAgent
from PIL import Image

VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")

_agent: MAIGroundingAgent | None = None


def get_agent() -> MAIGroundingAgent:
    global _agent
    if _agent is None:
        _agent = MAIGroundingAgent(
            llm_base_url=VLLM_BASE_URL,
            model_name="MAI-UI-2B",
            runtime_conf={"temperature": 0.0, "max_tokens": 2048},
        )
    return _agent


async def ground(image: Image.Image, instruction: str, zoom_in: bool = True) -> dict:
    agent = get_agent()
    W, H = image.width, image.height

    # Pass 1 — coarse prediction on full image
    _, result = agent.predict(instruction, image)
    norm_cx, norm_cy = result["coordinate"]
    cx, cy = norm_cx * W, norm_cy * H

    if not zoom_in:
        return {"x": round(cx), "y": round(cy)}

    # Crop centered on (cx, cy) with half the original dimensions
    x1 = max(0.0, cx - W / 4)
    y1 = max(0.0, cy - H / 4)
    x2 = min(float(W), cx + W / 4)
    y2 = min(float(H), cy + H / 4)
    crop_w = x2 - x1
    crop_h = y2 - y1

    zoomed = image.crop((x1, y1, x2, y2)).resize((W, H), Image.LANCZOS)

    # Pass 2 — refined prediction on zoomed crop
    _, result2 = agent.predict(instruction, zoomed)
    norm_rx, norm_ry = result2["coordinate"]

    final_x = x1 + norm_rx * crop_w
    final_y = y1 + norm_ry * crop_h

    return {
        "x": round(final_x),
        "y": round(final_y),
        "coarse_x": round(cx),
        "coarse_y": round(cy),
    }
