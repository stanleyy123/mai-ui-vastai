import base64
import io
import httpx
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from zoom_inference import ground


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Confirm vLLM is reachable before accepting traffic
    async with httpx.AsyncClient() as client:
        for _ in range(60):
            try:
                r = await client.get("http://localhost:8000/health", timeout=3)
                if r.status_code == 200:
                    break
            except Exception:
                pass
            import asyncio
            await asyncio.sleep(5)
        else:
            raise RuntimeError("vLLM did not become healthy in time")
    yield


app = FastAPI(lifespan=lifespan)


class GroundRequest(BaseModel):
    image: str          # base64-encoded PNG
    instruction: str
    zoom_in: bool = True


class GroundResponse(BaseModel):
    x: int
    y: int
    coarse_x: int | None = None
    coarse_y: int | None = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ground", response_model=GroundResponse)
async def ground_element(req: GroundRequest):
    try:
        image_bytes = base64.b64decode(req.image)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    if not req.instruction.strip():
        raise HTTPException(status_code=400, detail="instruction cannot be empty")

    try:
        result = await ground(image, req.instruction, req.zoom_in)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return GroundResponse(**result)
