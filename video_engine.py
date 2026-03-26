from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    concatenate_audioclips,
    afx,
    vfx,
)

# =========================================================
# CONFIG GENERAL
# =========================================================

W = 720
H = 1280
FPS = 20

VIDEO_BITRATE = "1800k"
AUDIO_BITRATE = "128k"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "renders"
TEMP_DIR = BASE_DIR / "temp_fixed"
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------
# RECURSOS
# ---------------------------------------------------------

FONT_PATH = BASE_DIR / "font.ttf"
MUSIC_PATH = BASE_DIR / "music.mp3"
HEART_PATH = BASE_DIR / "heart.mp3"

PHOTOS = [
    BASE_DIR / "foto1.jpg",
    BASE_DIR / "foto2.jpg",
    BASE_DIR / "foto3.jpg",
    BASE_DIR / "foto4.jpg",
    BASE_DIR / "foto5.jpg",
    BASE_DIR / "foto6.jpg",
]

# =========================================================
# TEXTOS
# =========================================================

LOGO_TEXT = "ETERNA"

INTRO_LINES = [
    "No es un vídeo.",
    "No es solo un momento.",
    "Esto es magia.",
]

PHOTO_LINES = [
    "Tu frase 1 aquí",
    "Tu frase 2 aquí",
    "Tu frase 3 aquí",
]

FINAL_LINES = [
    "Es bonito que alguien se acuerde de ti…",
    "Eso es magia.",
]

# =========================================================
# DURACIONES
# =========================================================

OPEN_LOGO_DURATION = 2.6
OPEN_LOGO_FADE = 1.0

INTRO_LINE_DURATION = 3.0
INTRO_LINE_FADE = 0.85
INTRO_GAP = 0.25

PRE_PHOTOS_BLACK = 1.2

PHOTO_DURATION = 5.6
PHOTO_FADE = 1.0

PHOTO_TEXT_DURATION = 3.0
PHOTO_TEXT_FADE = 0.85

FINAL_LINE_DURATION = 3.0
FINAL_LINE_FADE = 0.85
FINAL_GAP = 0.65

FINAL_BLACK_BEFORE_LOGO = 0.7
FINAL_LOGO_DURATION = 3.8
FINAL_LOGO_FADE = 1.2

HEART_FADE_OUT = 2.0
MUSIC_FADE_IN = 2.0
MUSIC_FADE_OUT = 2.5

# =========================================================
# ESTILO
# =========================================================

BG_COLOR = (0, 0, 0)
TEXT_COLOR = "white"

LOGO_FONT_SIZE = 72
INTRO_FONT_SIZE = 58
PHOTO_FONT_SIZE = 56
FINAL_FONT_SIZE = 54

TEXT_BOTTOM_Y = int(H * 0.82)

# =========================================================
# HELPERS
# =========================================================

def assert_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No existe {label}: {path}")


def fix_image_orientation(src_path: Path) -> Path:
    """
    Corrige orientación EXIF y guarda una copia temporal.
    """
    out_path = TEMP_DIR / f"fixed_{src_path.stem}.jpg"
    with Image.open(src_path) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(out_path, quality=95)
    return out_path


def make_black_clip(duration: float):
    return ColorClip(size=(W, H), color=BG_COLOR, duration=duration)


def make_text_clip(
    text: str,
    font_size: int,
    duration: float,
    fade: float,
    y_pos,
):
    """
    method='label' para evitar cortes raros de texto.
    """
    txt = TextClip(
        text=text,
        font=str(FONT_PATH),
        font_size=font_size,
        color=TEXT_COLOR,
        method="label",
        text_align="center",
    )

    txt = txt.with_duration(duration)
    txt = txt.with_position(("center", y_pos))
    txt = txt.with_effects(
        [
            vfx.CrossFadeIn(fade),
            vfx.CrossFadeOut(fade),
        ]
    )
    return txt


def make_center_text_block(text: str, font_size: int, duration: float, fade: float):
    base = make_black_clip(duration)
    txt = make_text_clip(
        text=text,
        font_size=font_size,
        duration=duration,
        fade=fade,
        y_pos="center",
    )
    return CompositeVideoClip([base, txt], size=(W, H)).with_duration(duration)


def make_logo_block(duration: float, fade: float):
    base = make_black_clip(duration)
    txt = make_text_clip(
        text=LOGO_TEXT,
        font_size=LOGO_FONT_SIZE,
        duration=duration,
        fade=fade,
        y_pos="center",
    )
    return CompositeVideoClip([base, txt], size=(W, H)).with_duration(duration)


def build_ken_burns(clip: ImageClip, duration: float, zoom_start: float, zoom_end: float):
    """
    Zoom suave progresivo.
    """
    clip = clip.with_duration(duration)

    def zoom_factor(t):
        if duration <= 0:
            return zoom_end
        progress = min(max(t / duration, 0), 1)
        return zoom_start + (zoom_end - zoom_start) * progress

    return clip.resized(lambda t: zoom_factor(t))


def make_photo_base_clip(photo_path: Path, duration: float):
    fixed_path = fix_image_orientation(photo_path)

    clip = ImageClip(str(fixed_path)).with_duration(duration)

    # Escalado para cubrir pantalla vertical sin deformar
    scale = max(W / clip.w, H / clip.h)
    clip = clip.resized(scale)

    # Blanco y negro
    clip = clip.with_effects([vfx.BlackAndWhite()])

    # Zoom suave
    clip = build_ken_burns(
        clip=clip,
        duration=duration,
        zoom_start=1.00,
        zoom_end=1.08,
    )

    # Centrado
    clip = clip.with_position("center")

    # Recorte exacto al marco final
    clip = clip.cropped(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=W,
        height=H,
    )

    # Fundidos
    clip = clip.with_effects(
        [
            vfx.CrossFadeIn(PHOTO_FADE),
            vfx.CrossFadeOut(PHOTO_FADE),
        ]
    )

    return clip


def make_photo_block(photo_path: Path, duration: float, overlay_text: str | None = None):
    base = make_photo_base_clip(photo_path, duration)

    layers = [base]

    if overlay_text:
        txt = make_text_clip(
            text=overlay_text,
            font_size=PHOTO_FONT_SIZE,
            duration=PHOTO_TEXT_DURATION,
            fade=PHOTO_TEXT_FADE,
            y_pos=TEXT_BOTTOM_Y,
        )

        text_start = max((duration - PHOTO_TEXT_DURATION) / 2, 0.6)
        txt = txt.with_start(text_start)
        layers.append(txt)

    return CompositeVideoClip(layers, size=(W, H)).with_duration(duration)


def loop_audio_to_duration(audio_clip: AudioFileClip, duration: float):
    """
    Repite el audio hasta cubrir toda la duración.
    """
    if audio_clip.duration >= duration:
        return audio_clip.subclipped(0, duration)

    clips = []
    current = 0.0
    while current < duration:
        remaining = duration - current
        part = audio_clip.subclipped(0, min(audio_clip.duration, remaining))
        clips.append(part)
        current += part.duration

    return concatenate_audioclips(clips)


# =========================================================
# CONSTRUCCIÓN DEL VÍDEO
# =========================================================

def build_video():
    # ---- Validaciones
    assert_exists(FONT_PATH, "fuente")
    assert_exists(MUSIC_PATH, "música")
    assert_exists(HEART_PATH, "corazón")

    for i, p in enumerate(PHOTOS, start=1):
        assert_exists(p, f"foto {i}")

    # -----------------------------------------------------
    # BLOQUE 1 - APERTURA
    # -----------------------------------------------------

    logo_open = make_logo_block(
        duration=OPEN_LOGO_DURATION,
        fade=OPEN_LOGO_FADE,
    )

    intro_blocks = []
    for line in INTRO_LINES:
        intro_blocks.append(
            make_center_text_block(
                text=line,
                font_size=INTRO_FONT_SIZE,
                duration=INTRO_LINE_DURATION,
                fade=INTRO_LINE_FADE,
            )
        )
        if INTRO_GAP > 0:
            intro_blocks.append(make_black_clip(INTRO_GAP))

    pre_photos_black = make_black_clip(PRE_PHOTOS_BLACK)

    # -----------------------------------------------------
    # BLOQUE 2 - FOTOS
    # -----------------------------------------------------

    photo_blocks = []
    photo_text_map = {
        1: None,
        2: PHOTO_LINES[0],
        3: None,
        4: PHOTO_LINES[1],
        5: None,
        6: PHOTO_LINES[2],
    }

    for index, photo in enumerate(PHOTOS, start=1):
        photo_blocks.append(
            make_photo_block(
                photo_path=photo,
                duration=PHOTO_DURATION,
                overlay_text=photo_text_map[index],
            )
        )

    # -----------------------------------------------------
    # BLOQUE 3 - FINAL EMOCIONAL
    # -----------------------------------------------------

    final_blocks = []

    final_blocks.append(
        make_center_text_block(
            text=FINAL_LINES[0],
            font_size=FINAL_FONT_SIZE,
            duration=FINAL_LINE_DURATION,
            fade=FINAL_LINE_FADE,
        )
    )
    final_blocks.append(make_black_clip(FINAL_GAP))
    final_blocks.append(
        make_center_text_block(
            text=FINAL_LINES[1],
            font_size=FINAL_FONT_SIZE,
            duration=FINAL_LINE_DURATION,
            fade=FINAL_LINE_FADE,
        )
    )
    final_blocks.append(make_black_clip(FINAL_BLACK_BEFORE_LOGO))

    # -----------------------------------------------------
    # BLOQUE 4 - LOGO FINAL
    # -----------------------------------------------------

    logo_final = make_logo_block(
        duration=FINAL_LOGO_DURATION,
        fade=FINAL_LOGO_FADE,
    )

    # -----------------------------------------------------
    # MONTAJE TOTAL DE VÍDEO
    # -----------------------------------------------------

    clips = [logo_open] + intro_blocks + [pre_photos_black] + photo_blocks + final_blocks + [logo_final]
    final_video = concatenate_videoclips(clips, method="compose").with_fps(FPS)

    total_duration = final_video.duration

    # =====================================================
    # AUDIO
    # =====================================================

    # Corazón desde segundo 0
    heart = AudioFileClip(str(HEART_PATH))
    heart = loop_audio_to_duration(heart, total_duration)
    heart = heart.with_volume_scaled(2.4)

    # El corazón desaparece cuando va a entrar la música
    music_start = logo_open.duration + sum(c.duration for c in intro_blocks)
    heart_end = music_start + HEART_FADE_OUT
    heart = heart.with_effects(
        [
            afx.AudioFadeOut(HEART_FADE_OUT),
        ]
    )

    # Recorte exacto del corazón hasta su desaparición
    if heart_end < total_duration:
        heart = heart.subclipped(0, heart_end)

    # Música desde transición a fotos, hasta el final
    music_base = AudioFileClip(str(MUSIC_PATH))
    music_needed_duration = max(total_duration - music_start, 0.1)
    music = loop_audio_to_duration(music_base, music_needed_duration)
    music = music.with_start(music_start)
    music = music.with_effects(
        [
            afx.AudioFadeIn(MUSIC_FADE_IN),
            afx.AudioFadeOut(MUSIC_FADE_OUT),
        ]
    )

    final_audio = CompositeAudioClip([heart, music])
    final_video = final_video.with_audio(final_audio)

    return final_video


# =========================================================
# RENDER
# =========================================================

def main():
    output_name = f"eterna_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = OUTPUT_DIR / output_name

    print("==============================================")
    print("ETERNA - RENDER FINAL")
    print("==============================================")
    print(f"Base dir: {BASE_DIR}")
    print(f"Output:   {output_path}")
    print("")

    video = build_video()

    print(f"Duración total: {video.duration:.2f}s")
    print("Renderizando...")

    video.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate=VIDEO_BITRATE,
        audio_bitrate=AUDIO_BITRATE,
        preset="medium",
        threads=4,
    )

    print("")
    print("✅ Render terminado")
    print(f"Archivo final: {output_path}")


if __name__ == "__main__":
    main()