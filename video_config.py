# video_config.py
import os

MODEL_PROVIDER = "anthropic"

MODEL_CONFIG = {
    "anthropic": {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "max_tokens": 45000
    },
    "groq": {
        "model": "groq/openai/gpt-oss-120b",
        "temperature": 0.6,
        "max_tokens": 35000
    }
}

VIDEO_LENGTH_MINUTES = 2
SEGMENTS_PER_MINUTE = 6
TOTAL_SEGMENTS = int(VIDEO_LENGTH_MINUTES * SEGMENTS_PER_MINUTE)

RENDER_BATCH_SIZE = 10

FFMPEG_TIMEOUT_SECONDS = 180
AUDIO_API_TIMEOUT = 30

MAX_RETRY_ATTEMPTS = 2

AUDIO_GENERATION_WORKERS = 10
VIDEO_RENDER_WORKERS = 6

# Scene-based animation system (replaces old background+overlay approach)
USE_AI_ANIMATIONS = True
ANIMATION_GENERATION_TIMEOUT = 90  # Increased for complex scenes

# Removed fallback - AI must succeed or fail clearly
ENABLE_FALLBACK_ANIMATIONS = False

BACKGROUND_MUSIC_FILES = [
    "music_one.mp3",
    "music_two.mp3",
    "music_three.mp3",
    "music_four.mp3"
]

BGM_VOLUME = 12

TRANSITION_DURATION = 0.5

TRANSITION_TYPES = [
    "fade",
    "fadeblack",
    "fadewhite",
    "wipeleft",
    "wiperight",
    "wipeup",
    "wipedown",
    "slideleft",
    "slideright",
    "slideup",
    "slidedown",
    "circlecrop",
    "rectcrop",
    "circleclose",
    "circleopen",
    "dissolve"
]

print("\n" + "╔" + "="*60 + "╗")
print("║" + " VIDEO GENERATION CONFIGURATION".center(60) + "║")
print("╠" + "="*60 + "╣")
print(f"║  Model Provider:      {MODEL_PROVIDER:<30} ║")
print(f"║  Model:               {MODEL_CONFIG[MODEL_PROVIDER]['model']:<30} ║")
print(f"║  Video Length:        {VIDEO_LENGTH_MINUTES} minute(s){''.ljust(36)} ║")
print(f"║  Total Segments:      {TOTAL_SEGMENTS:<42} ║")
print(f"║  Segments/Minute:     {SEGMENTS_PER_MINUTE:<42} ║")
print(f"║  Render Batch Size:   {RENDER_BATCH_SIZE:<42} ║")
print(f"║  FFmpeg Timeout:      {FFMPEG_TIMEOUT_SECONDS}s{''.ljust(40)} ║")
print(f"║  Animation System:    Scene-based (Topic-Specific){''.ljust(18)} ║")
print(f"║  Animation Timeout:   {ANIMATION_GENERATION_TIMEOUT}s{''.ljust(40)} ║")
print(f"║  Background Music:    {len(BACKGROUND_MUSIC_FILES)} tracks (volume: {BGM_VOLUME}%){''.ljust(20)} ║")
print(f"║  Transitions:         {len(TRANSITION_TYPES)} types ({TRANSITION_DURATION}s duration){''.ljust(18)} ║")
print(f"║  Architecture:        Complete auto-playing scenes{''.ljust(18)} ║")
print(f"║  Visual Style:        SVG diagrams + GSAP animations{''.ljust(14)} ║")
print(f"║  Est. Tokens:         ~{TOTAL_SEGMENTS * 200:<38} ║")
print("╚" + "="*60 + "╝\n")