from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class RenderRequest(BaseModel):
    order_id: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/render")
def render_video(data: RenderRequest):
    order_id = (data.order_id or "").strip()

    if not order_id:
        raise HTTPException(status_code=400, detail="order_id missing")

    print(f"🎬 Render pedido: {order_id}")

    return {
        "status": "accepted",
        "order_id": order_id
    }