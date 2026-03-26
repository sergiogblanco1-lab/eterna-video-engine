from datetime import datetime
from pathlib import Path

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    vfx,
    afx,
)

# =========================================================
# CONFIG GENERAL
# =========================================================

W = 1080
H = 1920
FPS = 24

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "renders"
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================================
# ARCHIVOS
# =========================================================

PHOTOS = [
    BASE_DIR / "foto1.jpg",
    BASE_DIR / "foto2.jpg",
    BASE_DIR / "foto3.jpg",
    BASE_DIR / "foto4.jpg",
    BASE_DIR / "foto5.jpg",
    BASE_DIR / "foto6.jpg",
]

MUSIC_PATH = BASE_DIR / "music.mp3"
HEART_PATH = BASE_DIR / "heart.mp3"
FONT_PATH = BASE_DIR / "font.ttf"

# =========================================================
# DURACIONES
# =========================================================

# 1) Inicio logo
OPEN_LOGO_DURATION = 2.0
OPEN_LOGO_FADE = 0.8

# 2) Intro por frases
INTRO_TEXT_DURATION = 1.65
INTRO_GAP_DURATION = 0.65
INTRO_TEXT_FADE = 0.45

# 3) Transición crítica
TRANSITION_BLACK_DURATION = 2.8
HEART_ONLY_LEAD = 0.65
HEART_FADE_OUT = 1.5
MUSIC_FADE_IN = 1.5

# 4) Fotos
# 5.4 te deja más cerca del rango 55s–1:05
PHOTO_DURATION = 5.4
PHOTO_FADE_IN = 0.8
PHOTO_FADE_OUT = 1.0
PHOTO_ZOOM_END = 1.07

# 5) Final emocional
FINAL_LINE_1_DURATION = 2.4
FINAL_GAP_DURATION = 0.9
FINAL_LINE_2_DURATION = 2.9
FINAL_LOGO_DURATION = 2.2
FINAL_FADE = 1.0

# Export
VIDEO_BITRATE = "3200k"
AUDIO_BITRATE = "192k"

# =========================================================
# COPY DEFINITIVO
# =========================================================

INTRO_LINES = [
    "No es un vídeo.",
    "No es un momento.",
    "Es un recuerdo.",
    "Es magia.",
]

FINAL_LINE_1 = "Alguien pensó en ti…"
FINAL_LINE_2 = "…eso es magia."
LOGO_TEXT = "ETERNA"

# =========================================================
# HELPERS
# =========================================================

def font_kwargs():
    if FONT_PATH.exists():
        return {"font": str(FONT_PATH)}
    return {}

def ensure_files_exist():
    missing = []

    for p in PHOTOS:
        if not p.exists():
            missing.append(str(p))

    if not MUSIC_PATH.exists():
        missing.append(str(MUSIC_PATH))

    if not HEART_PATH.exists():
        missing.append(str(HEART_PATH))

    if missing:
        print("\n❌ FALTAN ARCHIVOS:")
        for item in missing:
            print(" -", item)
        raise FileNotFoundError("Faltan archivos necesarios.")

def black_clip(duration: float):
    return ColorClip(size=(W, H), color=(0, 0, 0)).with_duration(duration)

def make_text(
    text: str,
    duration: float,
    font_size: int,
    fade_in: float,
    fade_out: float,
    y: int | str = "center",
):
    txt = TextClip(
        text=text,
        font_size=font_size,
        color="white",
        method="caption",
        size=(920, None),
        text_align="center",
        **font_kwargs(),
    )

    return (
        txt.with_duration(duration)
        .with_position(("center", y))
        .with_effects([
            vfx.FadeIn(fade_in),
            vfx.FadeOut(fade_out),
        ])
    )

def make_shadowed_text(
    text: str,
    duration: float,
    font_size: int,
    fade_in: float,
    fade_out: float,
    y: int | str = "center",
):
    shadow = TextClip(
        text=text,
        font_size=font_size,
        color="black",
        method="caption",
        size=(920, None),
        text_align="center",
        **font_kwargs(),
    )

    main = TextClip(
        text=text,
        font_size=font_size,
        color="white",
        method="caption",
        size=(920, None),
        text_align="center",
        **font_kwargs(),
    )

    shadow_y = y if isinstance(y, str) else y + 5

    shadow = (
        shadow.with_duration(duration)
        .with_position(("center", shadow_y))
        .with_effects([
            vfx.FadeIn(fade_in),
            vfx.FadeOut(fade_out),
        ])
    )

    main = (
        main.with_duration(duration)
        .with_position(("center", y))
        .with_effects([
            vfx.FadeIn(fade_in),
            vfx.FadeOut(fade_out),
        ])
    )

    return CompositeVideoClip([shadow, main], size=(W, H)).with_duration(duration)

def fit_image_to_frame(path: Path):
    clip = ImageClip(str(path))
    iw, ih = clip.size
    target_ratio = W / H
    image_ratio = iw / ih

    if image_ratio > target_ratio:
        clip = clip.resized(height=H)
        clip = clip.cropped(
            width=W,
            height=H,
            x_center=clip.w / 2,
            y_center=clip.h / 2,
        )
    else:
        clip = clip.resized(width=W)
        clip = clip.cropped(
            width=W,
            height=H,
            x_center=clip.w / 2,
            y_center=clip.h / 2,
        )

    return clip

# =========================================================
# BLOQUES DE VÍDEO
# =========================================================

def make_logo_block(duration: float, fade: float):
    bg = black_clip(duration)
    logo = make_shadowed_text(
        text=LOGO_TEXT,
        duration=duration,
        font_size=94,
        fade_in=fade,
        fade_out=fade,
        y="center",
    )
    return CompositeVideoClip([bg, logo], size=(W, H)).with_duration(duration)

def make_intro_line(text: str):
    bg = black_clip(INTRO_TEXT_DURATION)
    txt = make_shadowed_text(
        text=text,
        duration=INTRO_TEXT_DURATION,
        font_size=74,
        fade_in=INTRO_TEXT_FADE,
        fade_out=INTRO_TEXT_FADE,
        y="center",
    )
    return CompositeVideoClip([bg, txt], size=(W, H)).with_duration(INTRO_TEXT_DURATION)

def make_gap():
    return black_clip(INTRO_GAP_DURATION)

def make_transition_black():
    return black_clip(TRANSITION_BLACK_DURATION)

def make_photo_clip(path: Path, index: int):
    base = fit_image_to_frame(path).with_duration(PHOTO_DURATION).with_fps(FPS)

    base = base.with_effects([
        vfx.BlackAndWhite(),
    ])

    zoom_end = PHOTO_ZOOM_END + (0.01 if index % 2 == 0 else 0.0)

    def zoom_factor(t: float):
        progress = max(0.0, min(1.0, t / PHOTO_DURATION))
        return 1.0 + (zoom_end - 1.0) * progress

    moving = base.resized(lambda t: zoom_factor(t))

    direction = -1 if index % 2 == 0 else 1
    drift = 18

    def pos_fn(t: float):
        progress = max(0.0, min(1.0, t / PHOTO_DURATION))
        x = direction * drift * (progress - 0.5)
        return (x, 0)

    moving = (
        moving.with_position(pos_fn)
        .with_effects([
            vfx.FadeIn(PHOTO_FADE_IN),
            vfx.FadeOut(PHOTO_FADE_OUT),
        ])
    )

    return CompositeVideoClip([moving], size=(W, H)).with_duration(PHOTO_DURATION)

def make_final_line(text: str, duration: float):
    bg = black_clip(duration)
    txt = make_shadowed_text(
        text=text,
        duration=duration,
        font_size=74,
        fade_in=0.7,
        fade_out=0.9,
        y="center",
    )
    return CompositeVideoClip([bg, txt], size=(W, H)).with_duration(duration)

# =========================================================
# MONTAJE VÍDEO
# =========================================================

def build_video():
    clips = []

    clips.append(make_logo_block(OPEN_LOGO_DURATION, OPEN_LOGO_FADE))
    clips.append(black_clip(0.45))

    for i, line in enumerate(INTRO_LINES):
        clips.append(make_intro_line(line))
        if i < len(INTRO_LINES) - 1:
            clips.append(make_gap())

    clips.append(make_transition_black())

    for i, photo in enumerate(PHOTOS):
        clips.append(make_photo_clip(photo, i))

    clips.append(make_final_line(FINAL_LINE_1, FINAL_LINE_1_DURATION))
    clips.append(black_clip(FINAL_GAP_DURATION))
    clips.append(make_final_line(FINAL_LINE_2, FINAL_LINE_2_DURATION))
    clips.append(black_clip(0.7))
    clips.append(make_logo_block(FINAL_LOGO_DURATION, FINAL_FADE))

    return concatenate_videoclips(clips, method="compose").with_fps(FPS)

# =========================================================
# AUDIO
# =========================================================

def build_audio(final_duration: float):
    heart = AudioFileClip(str(HEART_PATH))
    music = AudioFileClip(str(MUSIC_PATH))

    intro_duration = (
        OPEN_LOGO_DURATION
        + 0.45
        + len(INTRO_LINES) * INTRO_TEXT_DURATION
        + (len(INTRO_LINES) - 1) * INTRO_GAP_DURATION
    )

    transition_start = intro_duration
    heart_start = transition_start
    music_start = transition_start + HEART_ONLY_LEAD

    # Corazón limitado exactamente a la negra de transición
    heart_target_duration = TRANSITION_BLACK_DURATION
    if heart.duration > heart_target_duration:
        heart = heart.subclipped(0, heart_target_duration)
    else:
        heart = heart.with_duration(heart_target_duration)

    heart = (
        heart.with_effects([
            afx.AudioFadeOut(HEART_FADE_OUT),
        ])
        .with_start(heart_start)
    )

    # Música desde la transición hasta el final
    max_music_available = max(0.0, final_duration - music_start)
    if music.duration > max_music_available:
        music = music.subclipped(0, max_music_available)

    music = (
        music.with_effects([
            afx.AudioFadeIn(MUSIC_FADE_IN),
            afx.AudioFadeOut(2.6),
        ])
        .with_start(music_start)
    )

    return CompositeAudioClip([heart, music]).with_duration(final_duration)

# =========================================================
# EXPORT
# =========================================================

def export_video():
    ensure_files_exist()

    video = None
    audio = None
    final = None

    try:
        video = build_video()
        audio = build_audio(video.duration)
        final = video.with_audio(audio)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"eterna_definitivo_{timestamp}.mp4"

        print("\n🎬 GENERANDO ETERNA...")
        print("📁 Base:", BASE_DIR)
        print("🎵 Música:", MUSIC_PATH)
        print("🫀 Corazón:", HEART_PATH)
        print("💾 Salida:", output_path)
        print(f"⏱ Duración total aprox: {final.duration:.2f} s")

        final.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate=VIDEO_BITRATE,
            audio_bitrate=AUDIO_BITRATE,
        )

        print("\n✅ VÍDEO ETERNA GENERADO")
        print(output_path.resolve())

    finally:
        # Cerrar clips para evitar archivos bloqueados al re-renderizar
        if final is not None:
            final.close()
        if audio is not None:
            audio.close()
        if video is not None:
            video.close()

if __name__ == "__main__":
    export_video()