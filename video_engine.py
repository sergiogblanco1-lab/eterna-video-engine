
pip uninstall moviepy -y
import os

# =====================================================
# CONFIG
# =====================================================

ASSETS = "assets"

IMAGE_PATH = os.path.join(ASSETS, "photo1.jpg")
MUSIC_PATH = os.path.join(ASSETS, "music.mp3")

OUTPUT = "output.mp4"

# =====================================================
# PARAMETROS ETERNA
# =====================================================

DURATION_IMAGE = 5  # segundos por foto
VIDEO_SIZE = (1080, 1920)  # vertical

# =====================================================
# INTRO (pantalla negra con golpe emocional)
# =====================================================

intro = ColorClip(size=VIDEO_SIZE, color=(0, 0, 0), duration=3)

# =====================================================
# FOTO (con pequeño zoom emocional)
# =====================================================

image = (
    ImageClip(IMAGE_PATH)
    .set_duration(DURATION_IMAGE)
    .resize(height=1920)
    .set_position("center")
)

# efecto zoom suave (tipo recuerdo)
image = image.fx(vfx.resize, lambda t: 1 + 0.02 * t)

# fade
image = image.crossfadein(1)

# =====================================================
# TEXTO (simulación frase)
# =====================================================

text = (
    TextClip(
        "Hay momentos que\nmerecen quedarse\npara siempre...",
        fontsize=60,
        color="white",
        method="caption",
        size=(900, None),
    )
    .set_position(("center", "bottom"))
    .set_duration(DURATION_IMAGE)
    .set_start(2)
)

# =====================================================
# COMPOSICIÓN
# =====================================================

video = CompositeVideoClip([image, text], size=VIDEO_SIZE)

final_video = concatenate_videoclips([intro, video])

# =====================================================
# AUDIO
# =====================================================

audio = AudioFileClip(MUSIC_PATH).subclip(0, final_video.duration)
final_video = final_video.set_audio(audio)

# =====================================================
# EXPORT
# =====================================================

final_video.write_videofile(
    OUTPUT,
    fps=24,
    codec="libx264",
    audio_codec="aac"
)