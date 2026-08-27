"""Chatterbox 모델을 한 번만 적재하는 다국어 TTS API 서버."""
import os
import uuid
from pathlib import Path

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Chatterbox Multilingual TTS")
OUTPUT_DIR = Path(os.getenv("TTS_OUTPUT_DIR", "./tts_outputs"))
LANGUAGES = {"ko": "ko", "en": "en", "ja": "ja"}
model = None


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1500)
    language: str


@app.on_event("startup")
def startup():
    global model
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    print(f"Chatterbox TTS ready on {device}")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/synthesize")
def synthesize(request: TTSRequest):
    if request.language not in LANGUAGES:
        raise HTTPException(400, "language must be ko, en, or ja")
    if model is None:
        raise HTTPException(503, "TTS model is loading")
    output = OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"
    with torch.inference_mode():
        wav = model.generate(request.text.strip(), language_id=LANGUAGES[request.language])
    torchaudio.save(str(output), wav.cpu(), model.sr)
    return FileResponse(output, media_type="audio/wav", filename=output.name)
