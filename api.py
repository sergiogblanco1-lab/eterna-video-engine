from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()

class VideoRequest(BaseModel):
    order_id: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/render")
def render_video(data: VideoRequest):
    order_id = data.order_id
    subprocess.run(["python", "video_engine.py", order_id])
    return {"status": "render started", "order_id": order_id}