print("🔥 GUARDADO REAL VIDEO ENGINE 🔥")
from datetime import datetime
from pathlib import Path
import gc
import os
import shutil
import sys
import traceback

import numpy as np
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from PIL import Image, ImageOps
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_audioclips,
    concatenate_videoclips,
    vfx,
    afx,
)

app = FastAPI(title="ETERNA VIDEO ENGINE")


class RenderRequest(BaseModel):
    order_id: str
    photos: list[str]
    phrases: list[str]


# =========================================================
# CONFIG
# =========================================================

W = 720
H = 1280
FPS = 20

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "renders"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_DIR = BASE_DIR / "temp_fixed"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

INPUTS_DIR = BASE_DIR / "inputs"
INPUTS_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = BASE_DIR / "photos_logo"

VIDEO_BITRATE = "1600k"
AUDIO_BITRATE = "96k"

VIDEO_ENGINE_PUBLIC_URL = os.getenv("VIDEO_ENGINE_PUBLIC_URL", "").strip().rstrip("/")


# =========================================================
# DURACIONES
# =========================================================

OPEN_LOGO_ONLY_DURATION = 2.0
OPEN_LOGO_FADE_DURATION = 3.0
OPEN_LOGO_FADE_OUT = 1.8

INTRO_TEXT_DURATION = 4.8
INTRO_GAP_DURATION = 3.0
INTRO_TEXT_FADE = 1.4

TRANSITION_BLACK_DURATION = 4.0

PHOTO_DURATION = 8.2
PHOTO_DURATION_FIRST = 12.2
PHOTO_DURATION_LONG = 9.8

PHOTO_FADE_IN = 7.0
PHOTO_FADE_OUT = 2.8

PHOTO_ZOOM_IN_START = 1.00
PHOTO_ZOOM_IN_END = 1.07
PHOTO_ZOOM_OUT_START = 1.05
PHOTO_ZOOM_OUT_END = 1.00

PHRASE_DURATION = 5.0
PHRASE_FADE = 1.0
PHRASE_START_DELAY = 1.2

FINAL_BLACK_BEFORE_LOGO = 3.8
FINAL_LOGO_DURATION = 5.5
FINAL_BLACK_HOLD_DURATION = 8.5
FINAL_FADE = 1.8
FINAL_LOGO_FADE_IN = 1.8
FINAL_LOGO_FADE_OUT = 1.8

HEART_VOLUME = 3.0
HEART_FADE_OUT = 2.4

MUSIC_FADE_IN = 4.0
MUSIC_FADE_OUT = 3.0
MUSIC_VOLUME = 0.8


# =========================================================
# TEXTOS
# =========================================================

INTRO_LINES = [
    "No es un momento...",
    "No es solo un recuerdo...",
    "Es magia.",
]

PHOTO_PHRASES = {
    1: "Y de pronto...\ntodo tuvo sentido.",
    3: "El tiempo pasa...\npero contigo todo se queda.",
    5: "Y aunque cambie la vida...\ntu siempre seras hogar.",
}


# =========================================================
# PATHS
# =========================================================

def find_inputs_dir():
    for name in ["inputs", "INPUTS", "Inputs"]:
        p = BASE_DIR / name
        if p.exists():
            return p
    raise FileNotFoundError("No encuentro carpeta inputs")


def find_audio(filename: str) -> Path:
    for p in [
        BASE_DIR / filename,
        BASE_DIR / "music" / filename,
        BASE_DIR / "audio" / filename,
    ]:
        if p.exists():
            return p
    raise FileNotFoundError(f"No encuentro {filename}")


def find_file_flexible(folder: Path, keyword: str) -> Path:
    keyword = keyword.lower().strip()
    for f in folder.glob("*"):
        if keyword in f.name.lower():
            return f
    raise FileNotFoundError(f"No se encontró archivo con '{keyword}' en {folder}")


def get_photos(inputs_dir: Path):
    exts = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]

    photos = []

    for i in range(1, 7):
        found = None

        names = [
            f"PHOTO{i}",
            f"photo{i}",
            f"FOTO{i}",
            f"foto{i}",
        ]

        for name in names:
            for ext in exts:
                candidate = inputs_dir / f"{name}{ext}"
                if candidate.exists():
                    found = candidate
                    break
            if found is not None:
                break

        if found is None:
            print(f"[WARN] No encontré PHOTO{i}/FOTO{i}")

        photos.append(found)

    if all(p is not None for p in photos):
        return photos

    print("[INFO] Usando fallback de fotos automáticas")

    all_photos = []
    all_photos += list(inputs_dir.glob("*.jpg"))
    all_photos += list(inputs_dir.glob("*.jpeg"))
    all_photos += list(inputs_dir.glob("*.png"))
    all_photos += list(inputs_dir.glob("*.JPG"))
    all_photos += list(inputs_dir.glob("*.JPEG"))
    all_photos += list(inputs_dir.glob("*.PNG"))

    all_photos = sorted(set(all_photos))

    if len(all_photos) < 6:
        raise Exception("Necesitas al menos 6 fotos en la carpeta inputs")

    return all_photos[:6]


def resolve_paths():
    inputs_dir = find_inputs_dir()
    photos = get_photos(inputs_dir)
    music = find_audio("music.mp3")
    heart = find_audio("heart.mp3")

    logo_inicio = find_file_flexible(ASSETS_DIR, "2417")
    logo_final = find_file_flexible(ASSETS_DIR, "2418")

    print("\n=== RUTAS ===")
    print("inputs :", inputs_dir)
    for i, p in enumerate(photos, start=1):
        print(f"foto {i} :", p.name)
    print("music  :", music)
    print("heart  :", heart)
    print("logo inicio :", logo_inicio.name)
    print("logo final  :", logo_final.name)

    return photos, music, heart, logo_inicio, logo_final


# =========================================================
# HELPERS VISUALES
# =========================================================

def black_clip(duration):
    return ColorClip((W, H), color=(0, 0, 0)).with_duration(duration)


def base_text_clip(
    text,
    duration,
    font_size=42,
    width_ratio=0.80,
    height_ratio=0.28,
    stroke_width=1.1,
):
    return TextClip(
        text=text,
        font_size=font_size,
        color="white",
        method="caption",
        size=(int(W * width_ratio), int(H * height_ratio)),
        text_align="center",
        horizontal_align="center",
        vertical_align="center",
        stroke_color="black",
        stroke_width=stroke_width,
        interline=6,
        margin=(0, 18),
    ).with_duration(duration)


# =========================================================
# TEXTO INTRO
# =========================================================

def pulsing_text_heart_slow(text, duration, font_size=42, pos="center", fade=1.0):
    base = base_text_clip(
        text=text,
        duration=duration,
        font_size=font_size,
        width_ratio=0.80,
        height_ratio=0.28,
        stroke_width=1.1,
    )

    def scale_fn(t):
        beat = (t % 2.2) / 2.2

        if beat < 0.20:
            return 1.00 + 0.05 * (beat / 0.20)
        elif beat < 0.45:
            return 1.05 - 0.03 * ((beat - 0.20) / 0.25)
        elif beat < 0.70:
            return 1.02 + 0.04 * ((beat - 0.45) / 0.25)
        elif beat < 0.90:
            return 1.06 - 0.04 * ((beat - 0.70) / 0.20)
        else:
            return 1.02

    if pos == "center":
        y_pos = ("center", "center")
    else:
        y_pos = ("center", int(H * 0.60))

    return (
        base
        .resized(lambda t: scale_fn(t))
        .with_opacity(1.0)
        .with_position(y_pos)
        .with_effects([
            vfx.FadeIn(fade),
            vfx.FadeOut(fade),
        ])
    )


# =========================================================
# TEXTO FOTOS
# =========================================================

def photo_phrase_text(text, duration, font_size=38, fade=1.0):
    base = TextClip(
        text=text,
        font_size=font_size,
        color="white",
        method="caption",
        size=(int(W * 0.78), int(H * 0.26)),
        text_align="center",
        stroke_color="black",
        stroke_width=1.1
    ).with_duration(duration)

    return (
        base
        .with_opacity(1.0)
        .with_position(("center", int(H * 0.62)))
        .with_effects([
            vfx.FadeIn(fade),
            vfx.FadeOut(fade),
        ])
    )


# =========================================================
# LOGOS
# =========================================================

def process_logo(logo_path: Path, duration: float, max_w_ratio: float, max_h_ratio: float):
    logo = ImageClip(str(logo_path)).with_duration(duration)

    max_w = int(W * max_w_ratio)
    max_h = int(H * max_h_ratio)

    scale = min(max_w / logo.w, max_h / logo.h)
    logo = logo.resized(scale)

    return logo.with_position(("center", "center"))


def logo_inicio_clip(duration, logo_inicio_path: Path):
    return (
        process_logo(logo_inicio_path, duration, 0.85, 0.30)
        .with_effects([
            vfx.FadeOut(OPEN_LOGO_FADE_OUT)
        ])
    )


def logo_final_clip(duration, logo_final_path: Path):
    return (
        process_logo(logo_final_path, duration, 0.95, 0.82)
        .with_effects([
            vfx.FadeIn(FINAL_LOGO_FADE_IN),
            vfx.FadeOut(FINAL_LOGO_FADE_OUT),
        ])
    )


# =========================================================
# HELPERS DE IMAGEN
# =========================================================

def normalize_image_to_temp(img_path: Path) -> Path:
    out_path = TEMP_DIR / f"{img_path.stem}_fixed.jpg"

    img = Image.open(img_path)
    img = ImageOps.exif_transpose(img)
    rgb = img.convert("RGB")
    rgb.save(out_path, quality=92)

    return out_path


def fit_cover(img_path: Path):
    fixed_path = normalize_image_to_temp(Path(img_path))
    clip = ImageClip(str(fixed_path))
    scale = max(W / clip.w, H / clip.h)
    clip = clip.resized(scale)

    return clip.cropped(
        width=W,
        height=H,
        x_center=clip.w / 2,
        y_center=clip.h / 2,
    )


# =========================================================
# BLOQUE DE FOTO
# =========================================================

def build_photo_clip(
    img_path,
    duration,
    phrase=None,
    zoom_mode="in",
    move_x=0,
    move_y=0,
    is_color=False,
    is_first=False,
):
    base = fit_cover(img_path).with_duration(duration)

    if zoom_mode == "out":
        def zoom_factor(t):
            return PHOTO_ZOOM_OUT_START + (PHOTO_ZOOM_OUT_END - PHOTO_ZOOM_OUT_START) * (t / duration)
    else:
        def zoom_factor(t):
            return PHOTO_ZOOM_IN_START + (PHOTO_ZOOM_IN_END - PHOTO_ZOOM_IN_START) * (t / duration)

    moving = base.resized(lambda t: zoom_factor(t))

    def pos_fn(t):
        x = move_x * (t / duration)
        y = move_y * (t / duration)
        return ("center", "center") if (move_x == 0 and move_y == 0) else (x, y)

    if move_x != 0 or move_y != 0:
        moving = moving.with_position(pos_fn)

    if not is_color:
        moving = moving.with_effects([vfx.BlackAndWhite()])
    else:
        bw = moving.with_effects([vfx.BlackAndWhite()])
        moving = CompositeVideoClip([
            bw.with_opacity(0.7),
            moving.with_opacity(0.3),
        ], size=(W, H)).with_duration(duration)

    fade_in = PHOTO_FADE_IN + 3.0 if is_first else PHOTO_FADE_IN

    moving = moving.with_effects([
        vfx.FadeIn(fade_in),
        vfx.FadeOut(PHOTO_FADE_OUT),
    ])

    layers = [moving]

    if phrase:
        phrase_clip = (
            photo_phrase_text(
                phrase,
                duration=PHRASE_DURATION,
                font_size=38,
                fade=PHRASE_FADE,
            )
            .with_start(PHRASE_START_DELAY)
        )
        layers.append(phrase_clip)

    return CompositeVideoClip(layers, size=(W, H)).with_duration(duration)


# =========================================================
# BLOQUE VIDEO
# =========================================================

def build_video(photos, logo_inicio_path, logo_final_path):
    clips = []

    clips.append(
        CompositeVideoClip([
            black_clip(OPEN_LOGO_ONLY_DURATION),
            logo_inicio_clip(OPEN_LOGO_ONLY_DURATION, logo_inicio_path),
        ], size=(W, H)).with_duration(OPEN_LOGO_ONLY_DURATION)
    )

    clips.append(black_clip(OPEN_LOGO_FADE_DURATION))

    for i, line in enumerate(INTRO_LINES):
        clips.append(
            CompositeVideoClip([
                black_clip(INTRO_TEXT_DURATION),
                pulsing_text_heart_slow(
                    line,
                    duration=INTRO_TEXT_DURATION,
                    font_size=42,
                    pos="center",
                    fade=INTRO_TEXT_FADE,
                ),
            ], size=(W, H)).with_duration(INTRO_TEXT_DURATION)
        )

        if i < len(INTRO_LINES) - 1:
            clips.append(black_clip(INTRO_GAP_DURATION))

    clips.append(black_clip(TRANSITION_BLACK_DURATION))

    movement_plan = [
        {"zoom_mode": "in",  "move_x":  18, "move_y":   0},
        {"zoom_mode": "out", "move_x": -18, "move_y":   0},
        {"zoom_mode": "in",  "move_x":   0, "move_y": -14},
        {"zoom_mode": "in",  "move_x":   0, "move_y":  14},
        {"zoom_mode": "out", "move_x":  16, "move_y":   0},
        {"zoom_mode": "in",  "move_x": -16, "move_y":   0},
    ]

    for i, p in enumerate(photos):
        if i == 0:
            duration = PHOTO_DURATION_FIRST
        elif i in [3, 5]:
            duration = PHOTO_DURATION_LONG
        else:
            duration = PHOTO_DURATION

        movement = movement_plan[i]
        phrase = PHOTO_PHRASES.get(i)

        clips.append(
            build_photo_clip(
                p,
                duration=duration,
                phrase=phrase,
                zoom_mode=movement["zoom_mode"],
                move_x=movement["move_x"],
                move_y=movement["move_y"],
                is_color=(i in [3, 5]),
                is_first=(i == 0),
            )
        )

        if i == 4:
            clips.append(black_clip(1.25))

    clips.append(black_clip(FINAL_BLACK_BEFORE_LOGO))

    clips.append(
        CompositeVideoClip([
            black_clip(FINAL_LOGO_DURATION),
            logo_final_clip(FINAL_LOGO_DURATION, logo_final_path),
        ], size=(W, H)).with_duration(FINAL_LOGO_DURATION)
    )

    clips.append(black_clip(FINAL_BLACK_HOLD_DURATION))

    return concatenate_videoclips(clips, method="compose").with_fps(FPS)


# =========================================================
# AUDIO
# =========================================================

def loop_audio(audio_clip, duration):
    parts = []
    remaining = duration

    while remaining > 0:
        take = min(audio_clip.duration, remaining)
        parts.append(audio_clip.subclipped(0, take))
        remaining -= take

    return concatenate_audioclips(parts)


def build_audio(duration, music_path, heart_path):
    heart_src = AudioFileClip(str(heart_path))
    music_src = AudioFileClip(str(music_path))

    magia_start = (
        OPEN_LOGO_ONLY_DURATION
        + OPEN_LOGO_FADE_DURATION
        + INTRO_TEXT_DURATION
        + INTRO_GAP_DURATION
        + INTRO_TEXT_DURATION
        + INTRO_GAP_DURATION
    )

    music_start = magia_start - 2.0
    heart_duration = magia_start + HEART_FADE_OUT

    heart_audio = (
        loop_audio(heart_src, heart_duration)
        .with_start(2)
        .with_effects([
            afx.AudioFadeOut(HEART_FADE_OUT)
        ])
        .with_volume_scaled(HEART_VOLUME)
    )

    music_audio = (
        loop_audio(music_src, max(0.1, duration - music_start))
        .with_start(music_start)
        .with_effects([
            afx.AudioFadeIn(MUSIC_FADE_IN),
            afx.AudioFadeOut(MUSIC_FADE_OUT)
        ])
        .with_volume_scaled(MUSIC_VOLUME)
    )

    return CompositeAudioClip([heart_audio, music_audio]).with_duration(duration)


# =========================================================
# RENDER REUTILIZABLE
# =========================================================

def render_eterna_video(photo_paths, phrase_1, phrase_2, phrase_3, output_path):
    global PHOTO_PHRASES

    if len(photo_paths) != 6:
        raise ValueError("Se necesitan exactamente 6 fotos")

    PHOTO_PHRASES = {
        1: phrase_1,
        3: phrase_2,
        5: phrase_3,
    }

    video = None
    audio = None
    final = None

    try:
        music_path = find_audio("music.mp3")
        heart_path = find_audio("heart.mp3")
        logo_inicio_path = find_file_flexible(ASSETS_DIR, "2417")
        logo_final_path = find_file_flexible(ASSETS_DIR, "2418")

        photos = [Path(p) for p in photo_paths]

        print("🔥 START render_eterna_video")
        print("🔥 photos:", photos)
        print("🔥 music_path:", music_path)
        print("🔥 heart_path:", heart_path)
        print("🔥 logo_inicio_path:", logo_inicio_path)
        print("🔥 logo_final_path:", logo_final_path)
        sys.stdout.flush()

        video = build_video(photos, logo_inicio_path, logo_final_path)
        print("🔥 build_video OK. duration:", video.duration)
        sys.stdout.flush()

        audio = build_audio(video.duration, music_path, heart_path)
        print("🔥 build_audio OK")
        sys.stdout.flush()

        final = video.with_audio(audio)
        print("🔥 final with audio OK")
        sys.stdout.flush()

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        print("🎬 EMPEZANDO RENDER...")
        print("📁 OUTPUT PATH:", out)
        sys.stdout.flush()

        final.write_videofile(
            str(out),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate=VIDEO_BITRATE,
            audio_bitrate=AUDIO_BITRATE,
            preset="ultrafast",
            threads=2,
        )

        print("✅ TERMINÓ write_videofile")
        print("📁 EXISTE ARCHIVO:", out.exists())
        print("📁 SIZE:", out.stat().st_size if out.exists() else "NO FILE")
        print(f"✅ VIDEO CREADO: {out}")
        sys.stdout.flush()

        return str(out)

    finally:
        for clip in [final, audio, video]:
            try:
                if clip is not None:
                    clip.close()
            except Exception:
                pass

        gc.collect()


# =========================================================
# DESCARGA DE FOTOS
# =========================================================

def download_file(url: str, dest: Path):
    print("⬇️ Descargando:", url)
    sys.stdout.flush()

    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    print("✅ Descargada en:", dest)
    sys.stdout.flush()


def prepare_order_inputs(order_id: str, photo_urls: list[str]) -> list[str]:
    if len(photo_urls) != 6:
        raise ValueError("Se necesitan exactamente 6 URLs de fotos")

    order_input_dir = INPUTS_DIR / order_id
    if order_input_dir.exists():
        shutil.rmtree(order_input_dir)
    order_input_dir.mkdir(parents=True, exist_ok=True)

    local_paths = []

    for idx, url in enumerate(photo_urls, start=1):
        dest = order_input_dir / f"PHOTO{idx}.jpg"
        print(f"⬇️ Descargando foto {idx}: {url}")
        sys.stdout.flush()
        download_file(url, dest)
        local_paths.append(str(dest))

    print("🔥 prepare_order_inputs OK:", local_paths)
    sys.stdout.flush()

    return local_paths


def build_public_video_url(request: Request, filename: str) -> str:
    if VIDEO_ENGINE_PUBLIC_URL:
        return f"{VIDEO_ENGINE_PUBLIC_URL}/video/{filename}"
    base = str(request.base_url).rstrip("/")
    return f"{base}/video/{filename}"


# =========================================================
# ROUTES
# =========================================================

@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/video/{filename}")
def get_rendered_video(filename: str):
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Vídeo no encontrado")

    return FileResponse(
        str(file_path),
        media_type="video/mp4",
        filename=safe_name,
    )


@app.post("/render")
def render_video(data: RenderRequest, request: Request):
    print("🎬 Generando video para:", data.order_id)
    print("🔥 payload photos:", data.photos)
    print("🔥 payload phrases:", data.phrases)
    sys.stdout.flush()

    if not data.order_id.strip():
        raise HTTPException(status_code=400, detail="order_id vacío")

    if len(data.photos) != 6:
        raise HTTPException(status_code=400, detail="Se necesitan 6 fotos")

    if len(data.phrases) != 3:
        raise HTTPException(status_code=400, detail="Se necesitan 3 frases")

    order_id = data.order_id.strip()
    output_path = OUTPUT_DIR / f"{order_id}.mp4"

    try:
        print("🔥 START RENDER ENDPOINT")
        sys.stdout.flush()

        photo_paths = prepare_order_inputs(order_id, data.photos)
        print("🔥 PHOTOS DESCARGADAS")
        sys.stdout.flush()

        render_eterna_video(
            photo_paths=photo_paths,
            phrase_1=data.phrases[0],
            phrase_2=data.phrases[1],
            phrase_3=data.phrases[2],
            output_path=str(output_path),
        )

        print("🔥 VIDEO GENERADO")
        print("🔥 CHECK FILE EXISTS:", output_path)
        print("🔥 EXISTS:", output_path.exists())
        sys.stdout.flush()

        if not output_path.exists():
            print("❌ ARCHIVO NO EXISTE → el render se ha roto antes de terminar")
            sys.stdout.flush()
            return JSONResponse({
                "status": "error",
                "reason": "video_not_generated",
                "order_id": order_id,
            })

        video_url = build_public_video_url(request, output_path.name)
        print("🔥 video_url:", video_url)
        sys.stdout.flush()

        return JSONResponse({
            "status": "done",
            "order_id": order_id,
            "video_url": video_url,
        })

    except Exception as e:
        print("❌ ERROR RENDER:", str(e))
        traceback.print_exc()
        sys.stdout.flush()

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "order_id": order_id,
                "error": str(e),
            },
        )


# =========================================================
# MAIN LOCAL
# =========================================================

def main():
    photos, _, _, _, _ = resolve_paths()
    output_name = f"eterna_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = OUTPUT_DIR / output_name

    render_eterna_video(
        photo_paths=[str(p) for p in photos],
        phrase_1="Y de pronto...\ntodo tuvo sentido.",
        phrase_2="El tiempo pasa...\npero contigo todo se queda.",
        phrase_3="Y aunque cambie la vida...\ntu siempre seras hogar.",
        output_path=str(output_path),
    )

    print(f"🎉 Render local terminado: {output_path}")


if __name__ == "__main__":
    main()