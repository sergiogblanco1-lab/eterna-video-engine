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

VIDEO_BITRATE = "1600k"
AUDIO_BITRATE = "96k"

# =========================================================
# DURACIONES
# =========================================================

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
PHOTO_ZOOM_IN_START = 1.00
PHOTO_ZOOM_IN_END = 1.07
PHOTO_ZOOM_OUT_START = 1.05
PHOTO_ZOOM_OUT_END = 1.00

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

# =========================================================
# TEXTOS
# =========================================================

INTRO_LINES = [
    "No es un momento...",
    "No es solo un recuerdo...",
    "Es magia.",
]

PHOTO_PHRASES = {
    1: "Desde el primer momento...\nsupe que mi vida ya no era mia.",
    3: "Creces...\ny ojala pudiera detener el tiempo\nun segundo mas.",
    5: "Y pase lo que pase...\nsiempre vas a ser mi pequena.",
}

FINAL_LINE_1 = "Alguien penso en ti..."
FINAL_LINE_2 = "...de una forma que nunca vas a olvidar."
LOGO_TEXT = "ETERNA"

# =========================================================
# RUTAS
# =========================================================

def find_inputs_dir():
    for name in ["inputs", "INPUTS", "Inputs"]:
        p = BASE_DIR / name
        if p.exists():
            return p
    raise FileNotFoundError("No encuentro carpeta inputs")

def find_audio(filename):
    for p in [
        BASE_DIR / filename,
        BASE_DIR / "music" / filename,
        BASE_DIR / "audio" / filename,
    ]:
        if p.exists():
            return p
    raise FileNotFoundError(f"No encuentro {filename}")

def get_photos(inputs_dir):
    photos = list(inputs_dir.glob("*.jpg"))
    photos += list(inputs_dir.glob("*.jpeg"))
    photos += list(inputs_dir.glob("*.png"))
    photos = sorted(set(photos))

    if len(photos) < 6:
        raise Exception("Necesitas al menos 6 fotos en la carpeta inputs")

    return photos[:6]

def resolve_paths():
    inputs_dir = find_inputs_dir()
    photos = get_photos(inputs_dir)
    music = find_audio("music.mp3")
    heart = find_audio("heart.mp3")

    print("\n=== RUTAS ===")
    print("inputs :", inputs_dir)
    for i, p in enumerate(photos, start=1):
        print(f"foto {i} :", p.name)
    print("music  :", music)
    print("heart  :", heart)

    return photos, music, heart

# =========================================================
# HELPERS VISUALES
# =========================================================

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
        text=text,
        font_size=font_size,
        color="white",
        method="caption",
        size=(int(W * 0.72), int(H * 0.28)),
        text_align="center",
        horizontal_align="center",
        vertical_align="center",
        stroke_color="black",
        stroke_width=stroke_width,
        interline=6,
        margin=(0, 18),
    ).with_duration(d)

    return txt.with_position(("center", y)).with_effects([
        vfx.FadeIn(fade),
        vfx.FadeOut(fade),
    ])

def normalize_image_to_temp(img_path: Path) -> Path:
    temp_dir = BASE_DIR / "temp_fixed"
    temp_dir.mkdir(exist_ok=True)

    out_path = temp_dir / f"{img_path.stem}_fixed.jpg"

    img = Image.open(img_path)
    img = ImageOps.exif_transpose(img)
    rgb = img.convert("RGB")
    rgb.save(out_path, quality=92)

    return out_path

def fit_cover(img_path):
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

def build_photo_clip(img_path, duration, phrase=None, zoom_mode="in", move_x=0, move_y=0):
    base = fit_cover(img_path).with_duration(duration)

    if zoom_mode == "out":
        def zoom_factor(t):
            return PHOTO_ZOOM_OUT_START + (PHOTO_ZOOM_OUT_END - PHOTO_ZOOM_OUT_START) * (t / duration)
    else:
        def zoom_factor(t):
            return PHOTO_ZOOM_IN_START + (PHOTO_ZOOM_IN_END - PHOTO_ZOOM_IN_START) * (t / duration)

    moving = base.resized(lambda t: zoom_factor(t))

    # desplazamiento suave lateral/vertical
    def pos_fn(t):
        x = move_x * (t / duration)
        y = move_y * (t / duration)
        return ("center", "center") if (move_x == 0 and move_y == 0) else (x, y)

    if move_x != 0 or move_y != 0:
        moving = moving.with_position(pos_fn)

    moving = moving.with_effects([
        vfx.BlackAndWhite(),
        vfx.FadeIn(PHOTO_FADE_IN),
        vfx.FadeOut(PHOTO_FADE_OUT),
    ])

    layers = [moving]

    if phrase:
        phrase_clip = safe_text_clip(
            phrase,
            d=PHRASE_DURATION,
            font_size=38,
            fade=PHRASE_FADE,
            y=int(H * 0.78),
            stroke_width=1.2,
        ).with_start((duration - PHRASE_DURATION) / 2)

        layers.append(phrase_clip)

    return CompositeVideoClip(layers, size=(W, H)).with_duration(duration)

# =========================================================
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

    for i, line in enumerate(INTRO_LINES):
        clips.append(
            CompositeVideoClip([
                black_clip(INTRO_TEXT_DURATION),
                safe_text_clip(
                    line,
                    d=INTRO_TEXT_DURATION,
                    font_size=42,
                    fade=INTRO_TEXT_FADE,
                ),
            ], size=(W, H)).with_duration(INTRO_TEXT_DURATION)
        )
        if i < len(INTRO_LINES) - 1:
            clips.append(black_clip(INTRO_GAP_DURATION))

    clips.append(black_clip(TRANSITION_BLACK_DURATION))

    # movimientos suaves diferentes por foto
    movement_plan = [
        {"zoom_mode": "in",  "move_x":  18, "move_y":   0},
        {"zoom_mode": "out", "move_x": -18, "move_y":   0},
        {"zoom_mode": "in",  "move_x":   0, "move_y": -14},
        {"zoom_mode": "in",  "move_x":   0, "move_y":  14},
        {"zoom_mode": "out", "move_x":  16, "move_y":   0},
        {"zoom_mode": "in",  "move_x": -16, "move_y":   0},
    ]

    for i, p in enumerate(photos):
        phrase = PHOTO_PHRASES.get(i)
        duration = PHOTO_DURATIONS[i]
        movement = movement_plan[i]

        clips.append(
            build_photo_clip(
                p,
                duration=duration,
                phrase=phrase,
                zoom_mode=movement["zoom_mode"],
                move_x=movement["move_x"],
                move_y=movement["move_y"],
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

    clips.append(
        CompositeVideoClip([
            black_clip(FINAL_LOGO_DURATION),
            safe_text_clip(
                LOGO_TEXT,
                d=FINAL_LOGO_DURATION,
                font_size=56,
                fade=FINAL_FADE,
            ),
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

if __name__ == "__main__":
    main()