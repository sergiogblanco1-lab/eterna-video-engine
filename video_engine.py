print("🚀 MAIN NUEVO CARGADO")

from pathlib import Path
from typing import List
from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from moviepy import (
    VideoClip,
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
    concatenate_audioclips,
)

# =========================================================
# CONFIG
# =========================================================

WIDTH = 720
HEIGHT = 1280
FPS = 24

INTRO_DURATION = 10.5
PHOTO_DURATION = 6.0

INPUTS_FOLDER = "inputs"
RENDERS_FOLDER = "renders"

SHHH_PATH = "audio/shhh.wav"
HEART_PATH = "audio/heartbeat.wav"
MUSIC_PATH = "audio/music.mp3"

FONT_PATH = "fonts/PlayfairDisplay-Regular.ttf"

INTRO_LINE_1 = "Hay recuerdos que nos unen."
INTRO_LINE_2 = "Hagamos magia."

# enumerate empieza en 0:
# 1 = foto 2
# 3 = foto 4
# 5 = foto 6
PHOTO_TEXTS = {
    1: "Siempre hay algo que permanece.",
    3: "Hay lazos que el tiempo no borra.",
    5: "Lo vivido sigue aquí.",
}

TEXT_COLOR = (245, 245, 245, 255)
TEXT_MAX_WIDTH = 580
TEXT_FONT_SIZE = 46
PHOTO_TEXT_Y = 940
TEXT_LINE_SPACING = 14

# Música
MUSIC_START_IN_VIDEO = 0.0
MUSIC_VOLUME = 0.55
MUSIC_SOURCE_START = 0.0

# Movimiento de foto
ZOOM_START = 1.00
ZOOM_END = 1.10
PAN_PIXELS_X = 26
PAN_PIXELS_Y = 18

# =========================================================
# FOLDERS
# =========================================================

Path(RENDERS_FOLDER).mkdir(parents=True, exist_ok=True)

# =========================================================
# HELPERS
# =========================================================

def get_output_path() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(Path(RENDERS_FOLDER) / f"eterna_{stamp}.mp4")


def load_photos(folder: str) -> List[str]:
    path = Path(folder)
    if not path.exists():
        raise FileNotFoundError(f"No existe la carpeta: {folder}")

    files = list(path.glob("*"))
    imgs = [
        str(f) for f in files
        if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
    ]
    imgs.sort()

    if len(imgs) < 6:
        raise ValueError(f"Necesitas al menos 6 fotos. Encontradas: {len(imgs)}")

    return imgs[:6]


def load_image(path: str) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def pil_to_np(img: Image.Image) -> np.ndarray:
    return np.array(img.convert("RGB"))


def get_font(size: int):
    candidates = [
        FONT_PATH,
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass

    return ImageFont.load_default()


FONT = get_font(TEXT_FONT_SIZE)
DUMMY_IMG = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
DUMMY_DRAW = ImageDraw.Draw(DUMMY_IMG)


def measure_text(text: str, font) -> tuple[int, int]:
    x0, y0, x1, y1 = DUMMY_DRAW.textbbox((0, 0), text, font=font)
    return x1 - x0, y1 - y0


def wrap_text(text: str, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""

    for word in words:
        test = f"{current} {word}" if current else word
        w, _ = measure_text(test, FONT)

        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_centered_text(base_rgb: np.ndarray, text: str, y_center: int) -> np.ndarray:
    img = Image.fromarray(base_rgb).convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = wrap_text(text, TEXT_MAX_WIDTH)

    line_heights = []
    line_widths = []

    for line in lines:
        x0, y0, x1, y1 = draw.textbbox((0, 0), line, font=FONT)
        line_widths.append(x1 - x0)
        line_heights.append(y1 - y0)

    total_height = sum(line_heights) + max(0, (len(lines) - 1) * TEXT_LINE_SPACING)
    current_y = y_center - total_height // 2

    for i, line in enumerate(lines):
        w = line_widths[i]
        h = line_heights[i]
        x = (WIDTH - w) // 2

        draw.text((x + 2, current_y + 2), line, font=FONT, fill=(0, 0, 0, 110))
        draw.text((x, current_y), line, font=FONT, fill=TEXT_COLOR)

        current_y += h + TEXT_LINE_SPACING

    composed = Image.alpha_composite(img, overlay)
    return np.array(composed.convert("RGB"))


def fit_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    w, h = img.size
    ratio = w / h
    target_ratio = target_w / target_h

    if ratio > target_ratio:
        new_h = target_h
        new_w = int(ratio * new_h)
    else:
        new_w = target_w
        new_h = int(new_w / ratio)

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def make_animated_photo_frames(path: str, phrase: str | None = None) -> np.ndarray:
    base_img = load_image(path)

    canvas_w = int(WIDTH * ZOOM_END) + abs(PAN_PIXELS_X) * 2 + 40
    canvas_h = int(HEIGHT * ZOOM_END) + abs(PAN_PIXELS_Y) * 2 + 40

    prepared = fit_cover(base_img, canvas_w, canvas_h)
    prepared_np = pil_to_np(prepared)

    if phrase:
        prepared_np = draw_centered_text(prepared_np, phrase, int(PHOTO_TEXT_Y * (canvas_h / HEIGHT)))

    return prepared_np


# =========================================================
# INTRO
# =========================================================

gradient = np.linspace(0, 18, HEIGHT, dtype=np.uint8).reshape(HEIGHT, 1, 1)
INTRO_BG = np.repeat(gradient, WIDTH, axis=1)
INTRO_BG = np.repeat(INTRO_BG, 3, axis=2)


def fade_alpha(t: float, start: float, end: float) -> float:
    if end <= start:
        return 1.0

    progress = (t - start) / (end - start)
    progress = max(0.0, min(1.0, progress))
    fade_in = min(progress * 2.0, 1.0)
    fade_out = min((1.0 - progress) * 2.0, 1.0)
    return min(fade_in, fade_out)


def render_fading_text(bg_rgb: np.ndarray, text: str, alpha: float) -> np.ndarray:
    img = Image.fromarray(bg_rgb.copy()).convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = wrap_text(text, TEXT_MAX_WIDTH)

    line_sizes = [draw.textbbox((0, 0), line, font=FONT) for line in lines]
    widths = [x1 - x0 for x0, y0, x1, y1 in line_sizes]
    heights = [y1 - y0 for x0, y0, x1, y1 in line_sizes]

    total_height = sum(heights) + max(0, (len(lines) - 1) * TEXT_LINE_SPACING)
    current_y = HEIGHT // 2 - total_height // 2

    for i, line in enumerate(lines):
        x = (WIDTH - widths[i]) // 2
        fill = (245, 245, 245, int(255 * alpha))
        shadow = (0, 0, 0, int(110 * alpha))

        draw.text((x + 2, current_y + 2), line, font=FONT, fill=shadow)
        draw.text((x, current_y), line, font=FONT, fill=fill)

        current_y += heights[i] + TEXT_LINE_SPACING

    return np.array(Image.alpha_composite(img, overlay).convert("RGB"))


def intro_frame(t: float) -> np.ndarray:
    if 4.5 <= t <= 6.5:
        alpha = fade_alpha(t, 4.5, 6.5)
        return render_fading_text(INTRO_BG, INTRO_LINE_1, alpha)

    if 7.5 <= t <= 10.0:
        alpha = fade_alpha(t, 7.5, 10.0)
        return render_fading_text(INTRO_BG, INTRO_LINE_2, alpha)

    return INTRO_BG


def build_intro() -> VideoClip:
    return VideoClip(frame_function=intro_frame, duration=INTRO_DURATION).with_fps(FPS)


# =========================================================
# PHOTO CLIPS
# =========================================================

def build_photo_clip(path: str, phrase: str | None = None, index: int = 0) -> VideoClip:
    prepared = make_animated_photo_frames(path, phrase)
    source_h, source_w = prepared.shape[:2]

    extra_w = max(0, source_w - WIDTH)
    extra_h = max(0, source_h - HEIGHT)

    directions = [
        (1, 1),
        (-1, 1),
        (1, -1),
        (-1, -1),
        (1, 0),
        (0, 1),
    ]
    dir_x, dir_y = directions[index % len(directions)]

    def frame_function(t: float) -> np.ndarray:
        progress = max(0.0, min(1.0, t / PHOTO_DURATION))

        zoom = ZOOM_START + (ZOOM_END - ZOOM_START) * progress

        crop_w = int(WIDTH / zoom)
        crop_h = int(HEIGHT / zoom)

        crop_w = min(crop_w, source_w)
        crop_h = min(crop_h, source_h)

        center_x = source_w // 2
        center_y = source_h // 2

        max_shift_x = min(extra_w // 4, PAN_PIXELS_X)
        max_shift_y = min(extra_h // 4, PAN_PIXELS_Y)

        shift_x = int(dir_x * max_shift_x * progress)
        shift_y = int(dir_y * max_shift_y * progress)

        left = center_x - crop_w // 2 + shift_x
        top = center_y - crop_h // 2 + shift_y

        left = max(0, min(left, source_w - crop_w))
        top = max(0, min(top, source_h - crop_h))

        cropped = prepared[top:top + crop_h, left:left + crop_w]
        frame = Image.fromarray(cropped).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        return np.array(frame)

    return VideoClip(frame_function=frame_function, duration=PHOTO_DURATION).with_fps(FPS)


# =========================================================
# AUDIO
# =========================================================

def build_looped_audio_segment(audio_path: str, source_start: float, target_duration: float):
    if not Path(audio_path).exists():
        return None

    base = AudioFileClip(audio_path)

    try:
        actual_source_start = max(0.0, min(source_start, max(0.0, base.duration - 0.01)))
        usable = base.subclipped(actual_source_start, base.duration)

        if usable.duration <= 0:
            usable.close()
            base.close()
            return None

        pieces = []
        remaining = target_duration

        while remaining > 0:
            part_duration = min(usable.duration, remaining)
            pieces.append(usable.subclipped(0, part_duration))
            remaining -= part_duration

        looped = concatenate_audioclips(pieces)

        usable.close()
        base.close()

        return looped

    except Exception:
        try:
            base.close()
        except Exception:
            pass
        raise


def build_audio(total_duration: float):
    clips = []

    if Path(SHHH_PATH).exists():
        shhh = (
            AudioFileClip(SHHH_PATH)
            .with_start(1.0)
            .with_volume_scaled(0.40)
        )
        clips.append(shhh)

    if Path(HEART_PATH).exists():
        heart_src = AudioFileClip(HEART_PATH)
        try:
            start_src = min(1.2, max(0.0, heart_src.duration - 0.01))
            end_src = min(6.2, heart_src.duration)

            if end_src > start_src:
                heart = (
                    heart_src
                    .subclipped(start_src, end_src)
                    .with_start(4.5)
                    .with_volume_scaled(0.35)
                )
                clips.append(heart)
            else:
                heart_src.close()
        except Exception:
            try:
                heart_src.close()
            except Exception:
                pass
            raise

    music_needed = max(0.0, total_duration - MUSIC_START_IN_VIDEO)
    if music_needed > 0 and Path(MUSIC_PATH).exists():
        looped_music = build_looped_audio_segment(
            audio_path=MUSIC_PATH,
            source_start=MUSIC_SOURCE_START,
            target_duration=music_needed,
        )

        if looped_music is not None:
            music = (
                looped_music
                .with_start(MUSIC_START_IN_VIDEO)
                .with_volume_scaled(MUSIC_VOLUME)
            )
            clips.append(music)

    if not clips:
        return None

    return CompositeAudioClip(clips)


# =========================================================
# MAIN
# =========================================================

def build_video():
    print("🔥 EJECUTANDO NUEVO VIDEO 🔥")

    photos = load_photos(INPUTS_FOLDER)

    clips = [build_intro()]

    for i, p in enumerate(photos):
        phrase = PHOTO_TEXTS.get(i)
        clips.append(build_photo_clip(p, phrase, i))

    video = concatenate_videoclips(clips, method="compose")

    audio = build_audio(video.duration)
    if audio is not None:
        video = video.with_audio(audio)

    output_path = get_output_path()

    print(f"🎬 Guardando vídeo en: {output_path}")

    try:
        video.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            audio_fps=44100,
        )
        print(f"✅ Vídeo creado: {output_path}")

    finally:
        try:
            video.close()
        except Exception:
            pass

        try:
            if audio is not None:
                audio.close()
        except Exception:
            pass

        for c in clips:
            try:
                c.close()
            except Exception:
                pass


if __name__ == "__main__":
    build_video()