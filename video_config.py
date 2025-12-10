# video_config.py
import os

# ============================================================================
# MODEL PROVIDER CONFIGURATION
# ============================================================================

# Choose your AI model provider: "anthropic" or "groq"
MODEL_PROVIDER = "anthropic"  # Change this to switch providers globally

# Model configurations for each provider
MODEL_CONFIG = {
    "anthropic": {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "max_tokens": 10000
    },
    "groq": {
        "model": "groq/llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 25000
    }
}

#claude-sonnet-4-20250514_claude-opus-4-5-20251101

# ============================================================================
# VIDEO GENERATION SETTINGS
# ============================================================================

# Video length configuration
VIDEO_LENGTH_MINUTES = 1  # Change this to 5, 10, 15, etc.
SEGMENTS_PER_MINUTE = 6  # How many segments per minute
TOTAL_SEGMENTS = VIDEO_LENGTH_MINUTES * SEGMENTS_PER_MINUTE

# ============================================================================
# RENDERING CONFIGURATION
# ============================================================================

# Batch processing
RENDER_BATCH_SIZE = 10  # Render 10 videos at a time (prevents GPU overload)

# Timeouts
FFMPEG_TIMEOUT_SECONDS = 180  # 3 minutes for FFmpeg encoding
AUDIO_API_TIMEOUT = 30  # 30 seconds for audio generation API

# Retry logic
MAX_RETRY_ATTEMPTS = 2  # Retry failed operations up to 2 times

# Worker counts
AUDIO_GENERATION_WORKERS = 10  # Parallel audio generation
VIDEO_RENDER_WORKERS = 6  # Parallel video rendering (controlled by Modal)

# ============================================================================
# AI ANIMATION GENERATION SETTINGS
# ============================================================================

# Animation generation
USE_AI_ANIMATIONS = True  # Set to False to use fallback hardcoded animations
ANIMATION_GENERATION_TIMEOUT = 60  # Max time to wait for AI animation code

# Animation fallback
ENABLE_FALLBACK_ANIMATIONS = True  # Use simple fallback if AI fails

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
print(f"║  AI Animations:       {'Enabled' if USE_AI_ANIMATIONS else 'Disabled'}{''.ljust(36)} ║")
print(f"║  Est. Tokens:         ~{TOTAL_SEGMENTS * 150:<38} ║")
print("╚" + "="*60 + "╝\n")