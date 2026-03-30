from datetime import datetime
from pathlib import Path
<<<<<<< HEAD
import gc
import numpy as np
=======
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

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

# =========================================================
# CONFIG
# =========================================================

W = 720
H = 1280
FPS = 20

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "renders"
OUTPUT_DIR.mkdir(exist_ok=True)

<<<<<<< HEAD
TEMP_DIR = BASE_DIR / "temp_fixed"
TEMP_DIR.mkdir(exist_ok=True)

ASSETS_DIR = BASE_DIR / "photos_logo"

=======
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
VIDEO_BITRATE = "1600k"
AUDIO_BITRATE = "96k"

# =========================================================
# DURACIONES
# =========================================================

<<<<<<< HEAD
# LOGO INICIAL
OPEN_LOGO_ONLY_DURATION = 2.0
OPEN_LOGO_FADE_DURATION = 3.0
OPEN_LOGO_FADE_OUT = 1.8

# INTRO
INTRO_TEXT_DURATION = 4.8
INTRO_GAP_DURATION = 3.0
INTRO_TEXT_FADE = 1.4

# NEGRO DESPUÉS DE "ES MAGIA."
TRANSITION_BLACK_DURATION = 4.0

# FOTOS
PHOTO_DURATION = 8.2
PHOTO_DURATION_FIRST = 12.2
PHOTO_DURATION_LONG = 9.8

PHOTO_FADE_IN = 7.0
PHOTO_FADE_OUT = 2.8

=======
OPEN_LOGO_ONLY_DURATION = 2.0
OPEN_LOGO_FADE_DURATION = 2.0

INTRO_TEXT_DURATION = 4.8
INTRO_GAP_DURATION = 2.0
INTRO_TEXT_FADE = 1.4

TRANSITION_BLACK_DURATION = 6.0

PHOTO_DURATIONS = [7.2, 8.2, 7.3, 8.4, 7.4, 8.6]
PHOTO_FADE_IN = 1.8
PHOTO_FADE_OUT = 1.8

# zoom un poco más vivo
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
PHOTO_ZOOM_IN_START = 1.00
PHOTO_ZOOM_IN_END = 1.07
PHOTO_ZOOM_OUT_START = 1.05
PHOTO_ZOOM_OUT_END = 1.00

<<<<<<< HEAD
# FRASES EN FOTOS
PHRASE_DURATION = 5.0
PHRASE_FADE = 1.0
PHRASE_START_DELAY = 1.2

# FINAL
FINAL_BLACK_BEFORE_LOGO = 3.8
FINAL_LOGO_DURATION = 5.5
FINAL_BLACK_HOLD_DURATION = 8.5
FINAL_FADE = 1.8
FINAL_LOGO_FADE_IN = 1.8
FINAL_LOGO_FADE_OUT = 1.8

# AUDIO
HEART_VOLUME = 3.0
HEART_FADE_OUT = 2.4

MUSIC_FADE_IN = 4.0
MUSIC_FADE_OUT = 3.0
MUSIC_VOLUME = 0.8
=======
PHRASE_DURATION = 4.2
PHRASE_FADE = 1.4

FINAL_LINE_1_DURATION = 4.5
FINAL_GAP_DURATION = 2.0
FINAL_LINE_2_DURATION = 4.8
FINAL_LOGO_DURATION = 5.5
FINAL_BLACK_HOLD_DURATION = 3.0
FINAL_FADE = 1.8

HEART_VOLUME = 3.0
HEART_FADE_OUT = 1.4

MUSIC_FADE_IN = 5.5
MUSIC_FADE_OUT = 3.0
MUSIC_VOLUME = 0.8
MUSIC_FINAL_VOLUME = 0.85
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

# =========================================================
# TEXTOS
# =========================================================

INTRO_LINES = [
    "No es un momento...",
    "No es solo un recuerdo...",
    "Es magia.",
]

PHOTO_PHRASES = {
<<<<<<< HEAD
    1: "Y de pronto...\ntodo tuvo sentido.",
    3: "El tiempo pasa...\npero contigo todo se queda.",
    5: "Y aunque cambie la vida...\ntu siempre seras hogar.",
}

# =========================================================
# PATHS
=======
    1: "Desde el primer momento...\nsupe que mi vida ya no era mia.",
    3: "Creces...\ny ojala pudiera detener el tiempo\nun segundo mas.",
    5: "Y pase lo que pase...\nsiempre vas a ser mi pequena.",
}

FINAL_LINE_1 = "Alguien penso en ti..."
FINAL_LINE_2 = "...de una forma que nunca vas a olvidar."
LOGO_TEXT = "ETERNA"

# =========================================================
# RUTAS
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
# =========================================================

def find_inputs_dir():
    for name in ["inputs", "INPUTS", "Inputs"]:
        p = BASE_DIR / name
        if p.exists():
            return p
    raise FileNotFoundError("No encuentro carpeta inputs")

<<<<<<< HEAD
def find_audio(filename: str) -> Path:
=======
def find_audio(filename):
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
    for p in [
        BASE_DIR / filename,
        BASE_DIR / "music" / filename,
        BASE_DIR / "audio" / filename,
    ]:
        if p.exists():
            return p
    raise FileNotFoundError(f"No encuentro {filename}")

<<<<<<< HEAD
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
=======
def get_photos(inputs_dir):
    photos = list(inputs_dir.glob("*.jpg"))
    photos += list(inputs_dir.glob("*.jpeg"))
    photos += list(inputs_dir.glob("*.png"))
    photos = sorted(set(photos))

    if len(photos) < 6:
        raise Exception("Necesitas al menos 6 fotos en la carpeta inputs")

    return photos[:6]
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

def resolve_paths():
    inputs_dir = find_inputs_dir()
    photos = get_photos(inputs_dir)
    music = find_audio("music.mp3")
    heart = find_audio("heart.mp3")

<<<<<<< HEAD
    logo_inicio = find_file_flexible(ASSETS_DIR, "2417")
    logo_final = find_file_flexible(ASSETS_DIR, "2418")

=======
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
    print("\n=== RUTAS ===")
    print("inputs :", inputs_dir)
    for i, p in enumerate(photos, start=1):
        print(f"foto {i} :", p.name)
    print("music  :", music)
    print("heart  :", heart)
<<<<<<< HEAD
    print("logo inicio :", logo_inicio.name)
    print("logo final  :", logo_final.name)

    return photos, music, heart, logo_inicio, logo_final
=======

    return photos, music, heart
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

# =========================================================
# HELPERS VISUALES
# =========================================================

<<<<<<< HEAD
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
=======
def black_clip(d):
    return ColorClip((W, H), color=(8, 8, 8)).with_duration(d)

def safe_text_clip(
    text,
    d,
    font_size=42,
    fade=1.0,
    y="center",
    stroke_width=1.1,
):
    txt = TextClip(
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
        text=text,
        font_size=font_size,
        color="white",
        method="caption",
<<<<<<< HEAD
        size=(int(W * width_ratio), int(H * height_ratio)),
=======
        size=(int(W * 0.72), int(H * 0.28)),
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
        text_align="center",
        horizontal_align="center",
        vertical_align="center",
        stroke_color="black",
        stroke_width=stroke_width,
        interline=6,
        margin=(0, 18),
<<<<<<< HEAD
    ).with_duration(duration)

# =========================================================
# TEXTO INTRO (LATIDO LENTO)
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
# TEXTO FOTOS (SIN LATIDO)
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
=======
    ).with_duration(d)

    return txt.with_position(("center", y)).with_effects([
        vfx.FadeIn(fade),
        vfx.FadeOut(fade),
    ])

def normalize_image_to_temp(img_path: Path) -> Path:
    temp_dir = BASE_DIR / "temp_fixed"
    temp_dir.mkdir(exist_ok=True)

    out_path = temp_dir / f"{img_path.stem}_fixed.jpg"
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

    img = Image.open(img_path)
    img = ImageOps.exif_transpose(img)
    rgb = img.convert("RGB")
    rgb.save(out_path, quality=92)

    return out_path

<<<<<<< HEAD
def fit_cover(img_path: Path):
=======
def fit_cover(img_path):
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
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

<<<<<<< HEAD
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
=======
def build_photo_clip(img_path, duration, phrase=None, zoom_mode="in", move_x=0, move_y=0):
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
    base = fit_cover(img_path).with_duration(duration)

    if zoom_mode == "out":
        def zoom_factor(t):
            return PHOTO_ZOOM_OUT_START + (PHOTO_ZOOM_OUT_END - PHOTO_ZOOM_OUT_START) * (t / duration)
    else:
        def zoom_factor(t):
            return PHOTO_ZOOM_IN_START + (PHOTO_ZOOM_IN_END - PHOTO_ZOOM_IN_START) * (t / duration)

    moving = base.resized(lambda t: zoom_factor(t))

<<<<<<< HEAD
=======
    # desplazamiento suave lateral/vertical
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
    def pos_fn(t):
        x = move_x * (t / duration)
        y = move_y * (t / duration)
        return ("center", "center") if (move_x == 0 and move_y == 0) else (x, y)

    if move_x != 0 or move_y != 0:
        moving = moving.with_position(pos_fn)

<<<<<<< HEAD
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
=======
    moving = moving.with_effects([
        vfx.BlackAndWhite(),
        vfx.FadeIn(PHOTO_FADE_IN),
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
        vfx.FadeOut(PHOTO_FADE_OUT),
    ])

    layers = [moving]

    if phrase:
<<<<<<< HEAD
        phrase_clip = (
            photo_phrase_text(
                phrase,
                duration=PHRASE_DURATION,
                font_size=38,
                fade=PHRASE_FADE,
            )
            .with_start(PHRASE_START_DELAY)
        )
=======
        phrase_clip = safe_text_clip(
            phrase,
            d=PHRASE_DURATION,
            font_size=38,
            fade=PHRASE_FADE,
            y=int(H * 0.78),
            stroke_width=1.2,
        ).with_start((duration - PHRASE_DURATION) / 2)

>>>>>>> d8f23895562b21b821a76996e301409477b03cda
        layers.append(phrase_clip)

    return CompositeVideoClip(layers, size=(W, H)).with_duration(duration)

# =========================================================
<<<<<<< HEAD
# BLOQUE VIDEO
# =========================================================

def build_video(photos, logo_inicio_path, logo_final_path):
    clips = []

    # -----------------------------------------------------
    # LOGO INICIAL
    # -----------------------------------------------------
    clips.append(
        CompositeVideoClip([
            black_clip(OPEN_LOGO_ONLY_DURATION),
            logo_inicio_clip(OPEN_LOGO_ONLY_DURATION, logo_inicio_path),
        ], size=(W, H)).with_duration(OPEN_LOGO_ONLY_DURATION)
    )

    clips.append(black_clip(OPEN_LOGO_FADE_DURATION))

    # -----------------------------------------------------
    # INTRO FRASES
    # -----------------------------------------------------
=======
# VIDEO
# =========================================================

def build_video(photos):
    clips = []

    clips.append(
        CompositeVideoClip([
            black_clip(OPEN_LOGO_ONLY_DURATION),
            safe_text_clip(
                LOGO_TEXT,
                d=OPEN_LOGO_ONLY_DURATION,
                font_size=56,
                fade=0.0,
            ),
        ], size=(W, H)).with_duration(OPEN_LOGO_ONLY_DURATION)
    )

    clips.append(
        CompositeVideoClip([
            black_clip(OPEN_LOGO_FADE_DURATION),
            safe_text_clip(
                LOGO_TEXT,
                d=OPEN_LOGO_FADE_DURATION,
                font_size=56,
                fade=OPEN_LOGO_FADE_DURATION,
            ),
        ], size=(W, H)).with_duration(OPEN_LOGO_FADE_DURATION)
    )

>>>>>>> d8f23895562b21b821a76996e301409477b03cda
    for i, line in enumerate(INTRO_LINES):
        clips.append(
            CompositeVideoClip([
                black_clip(INTRO_TEXT_DURATION),
<<<<<<< HEAD
                pulsing_text_heart_slow(
                    line,
                    duration=INTRO_TEXT_DURATION,
                    font_size=42,
                    pos="center",
=======
                safe_text_clip(
                    line,
                    d=INTRO_TEXT_DURATION,
                    font_size=42,
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
                    fade=INTRO_TEXT_FADE,
                ),
            ], size=(W, H)).with_duration(INTRO_TEXT_DURATION)
        )
<<<<<<< HEAD

        if i < len(INTRO_LINES) - 1:
            clips.append(black_clip(INTRO_GAP_DURATION))

    # -----------------------------------------------------
    # NEGRO DESPUÉS DE "ES MAGIA."
    # -----------------------------------------------------
    clips.append(black_clip(TRANSITION_BLACK_DURATION))

    # -----------------------------------------------------
    # MOVIMIENTOS SUAVES DIFERENTES POR FOTO
    # -----------------------------------------------------
=======
        if i < len(INTRO_LINES) - 1:
            clips.append(black_clip(INTRO_GAP_DURATION))

    clips.append(black_clip(TRANSITION_BLACK_DURATION))

    # movimientos suaves diferentes por foto
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
    movement_plan = [
        {"zoom_mode": "in",  "move_x":  18, "move_y":   0},
        {"zoom_mode": "out", "move_x": -18, "move_y":   0},
        {"zoom_mode": "in",  "move_x":   0, "move_y": -14},
        {"zoom_mode": "in",  "move_x":   0, "move_y":  14},
        {"zoom_mode": "out", "move_x":  16, "move_y":   0},
        {"zoom_mode": "in",  "move_x": -16, "move_y":   0},
    ]

<<<<<<< HEAD
    # -----------------------------------------------------
    # FOTOS
    # -----------------------------------------------------
    for i, p in enumerate(photos):
        if i == 0:
            duration = PHOTO_DURATION_FIRST
        elif i in [3, 5]:
            duration = PHOTO_DURATION_LONG
        else:
            duration = PHOTO_DURATION

        movement = movement_plan[i]
        phrase = PHOTO_PHRASES.get(i)
=======
    for i, p in enumerate(photos):
        phrase = PHOTO_PHRASES.get(i)
        duration = PHOTO_DURATIONS[i]
        movement = movement_plan[i]
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

        clips.append(
            build_photo_clip(
                p,
                duration=duration,
                phrase=phrase,
                zoom_mode=movement["zoom_mode"],
                move_x=movement["move_x"],
                move_y=movement["move_y"],
<<<<<<< HEAD
                is_color=(i in [3, 5]),
                is_first=(i == 0),
            )
        )

        if i == 4:
            clips.append(black_clip(1.25))

    # -----------------------------------------------------
    # FINAL
    # -----------------------------------------------------
    clips.append(black_clip(FINAL_BLACK_BEFORE_LOGO))
=======
            )
        )
        clips.append(black_clip(2.0))

    clips.append(
        CompositeVideoClip([
            black_clip(FINAL_LINE_1_DURATION),
            safe_text_clip(
                FINAL_LINE_1,
                d=FINAL_LINE_1_DURATION,
                font_size=42,
                fade=FINAL_FADE,
            ),
        ], size=(W, H)).with_duration(FINAL_LINE_1_DURATION)
    )

    clips.append(black_clip(FINAL_GAP_DURATION))

    clips.append(
        CompositeVideoClip([
            black_clip(FINAL_LINE_2_DURATION),
            safe_text_clip(
                FINAL_LINE_2,
                d=FINAL_LINE_2_DURATION,
                font_size=42,
                fade=FINAL_FADE,
            ),
        ], size=(W, H)).with_duration(FINAL_LINE_2_DURATION)
    )

    clips.append(black_clip(2.0))
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

    clips.append(
        CompositeVideoClip([
            black_clip(FINAL_LOGO_DURATION),
<<<<<<< HEAD
            logo_final_clip(FINAL_LOGO_DURATION, logo_final_path),
=======
            safe_text_clip(
                LOGO_TEXT,
                d=FINAL_LOGO_DURATION,
                font_size=56,
                fade=FINAL_FADE,
            ),
>>>>>>> d8f23895562b21b821a76996e301409477b03cda
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

<<<<<<< HEAD
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
# RENDER REUTILIZABLE PARA MAIN
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

        video = build_video(photos, logo_inicio_path, logo_final_path)
        audio = build_audio(video.duration, music_path, heart_path)
        final = video.with_audio(audio)

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        final.write_videofile(
            str(out),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate=VIDEO_BITRATE,
            audio_bitrate=AUDIO_BITRATE,
            preset="ultrafast",
            threads=4,
        )

        print(f"VIDEO CREADO: {out}")
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

=======
    intro_logo_total = OPEN_LOGO_ONLY_DURATION + OPEN_LOGO_FADE_DURATION
    intro_texts_total = (
        len(INTRO_LINES) * INTRO_TEXT_DURATION
        + (len(INTRO_LINES) - 1) * INTRO_GAP_DURATION
    )

    transition_start = intro_logo_total + intro_texts_total

    heart_start = OPEN_LOGO_ONLY_DURATION
    heart_end = transition_start + 2.0

    heart_duration = heart_end - heart_start
    heart = loop_audio(heart_src, heart_duration).with_start(heart_start).with_volume_scaled(HEART_VOLUME)
    heart = heart.with_effects([
        afx.AudioFadeOut(HEART_FADE_OUT),
    ])

    music_start = transition_start + 3.0
    music_duration = max(0.1, duration - music_start)

    music = loop_audio(music_src, music_duration).with_start(music_start)
    music = music.with_effects([
        afx.AudioFadeIn(MUSIC_FADE_IN),
        afx.AudioFadeOut(MUSIC_FADE_OUT),
    ]).with_volume_scaled(MUSIC_VOLUME)

    final_lift_start = max(music_start, duration - 15.0)
    final_lift_duration = max(0.1, duration - final_lift_start)

    music_lift = loop_audio(music_src, final_lift_duration).with_start(final_lift_start)
    music_lift = music_lift.with_effects([
        afx.AudioFadeIn(3.0),
        afx.AudioFadeOut(MUSIC_FADE_OUT),
    ]).with_volume_scaled(MUSIC_FINAL_VOLUME - MUSIC_VOLUME)

    return CompositeAudioClip([heart, music, music_lift]).with_duration(duration)

# =========================================================
# MAIN
# =========================================================

def main():
    photos, music_path, heart_path = resolve_paths()

    video = build_video(photos)
    audio = build_audio(video.duration, music_path, heart_path)
    final = video.with_audio(audio)

    out = OUTPUT_DIR / f"eterna_{datetime.now().strftime('%H%M%S')}.mp4"

    final.write_videofile(
        str(out),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate=VIDEO_BITRATE,
        audio_bitrate=AUDIO_BITRATE,
        preset="ultrafast",
        threads=4,
    )

    final.close()
    video.close()
    audio.close()

    print(f"VIDEO CREADO: {out}")
>>>>>>> d8f23895562b21b821a76996e301409477b03cda

if __name__ == "__main__":
    main()