# video_modal_final.py
import modal
import os
import time
import base64

app = modal.App("garliq-video-backend")

base_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "crewai==0.86.0",
        "crewai-tools==0.17.0",
        "litellm==1.79.1",
        "anthropic>=0.18.0",
        "requests==2.31.0",
        "supabase==2.7.4",
        "httpx==0.27.0",
        "pydantic>=2.6.1",
        "fastapi==0.104.1",
        "uvicorn==0.24.0"
    )
    .apt_install("ffmpeg")
    .add_local_dir(".", "/root")
)

render_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("playwright==1.40.0")
    .apt_install("ffmpeg")
    .run_commands("playwright install chromium", "playwright install-deps")
    .add_local_dir(".", "/root")
)

secrets = modal.Secret.from_name("garliq-secrets")


@app.function(
    image=render_image,
    timeout=600,
    cpu=2.0,
    memory=4096,
    secrets=[secrets],
    retries=0
)
def render_segment_video(segment: dict, audio_base64: str, audio_duration: float, animation_html: str) -> str:
    """
    Render segment video using AI-generated HTML5 animation code
    FIXED: Uses Playwright video recording to capture ENTIRE viewport (canvas + HTML)
    
    Args:
        segment: dict with index, text, visual_hint
        audio_base64: base64-encoded audio WAV data
        audio_duration: duration of audio in seconds
        animation_html: AI-generated complete HTML animation code
        
    Returns:
        Base64-encoded MP4 file data (5 Mbps bitrate, normalized for concatenation)
    """
    from playwright.sync_api import sync_playwright
    import subprocess
    import time
    
    # Import config
    import sys
    sys.path.insert(0, '/root')
    from video_config import FFMPEG_TIMEOUT_SECONDS
    
    segment_index = segment['index']
    segment_text = segment['text']
    
    print(f"🎨 [{segment_index}] Starting: {segment_text[:40]}...")
    print(f"    Audio duration: {audio_duration:.1f}s")
    print(f"    Animation HTML: {len(animation_html)} chars")
    
    # STEP 1: Decode audio from base64
    try:
        audio_bytes = base64.b64decode(audio_base64)
        if len(audio_bytes) < 1000:
            raise Exception(f"Audio too small: {len(audio_bytes)} bytes")
    except Exception as e:
        raise Exception(f"Audio decode failed: {e}")
    
    # Save audio to temp file
    audio_path = f'/tmp/audio_{segment_index}.wav'
    with open(audio_path, 'wb') as f:
        f.write(audio_bytes)
    
    print(f"✓ [{segment_index}] Audio decoded: {len(audio_bytes)} bytes")
    
    # STEP 2: Calculate video duration (minimum 12 seconds)
    video_duration_ms = max(int(audio_duration * 1000) + 1000, 12000)
    video_duration_sec = video_duration_ms / 1000
    
    # STEP 3: Save HTML to temp file
    html_path = f'/tmp/segment_{segment_index}.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(animation_html)
    
    print(f"✓ [{segment_index}] HTML saved")
    
    # STEP 4: Render with Playwright - CAPTURE ENTIRE VIEWPORT
    video_path = f'/tmp/segment_{segment_index}_recording.webm'
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-features=IsolateOrigins',
                    '--disable-site-isolation-trials',
                    '--allow-running-insecure-content',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # ================================================================
            # KEY FIX: Enable video recording on the context
            # This captures ENTIRE viewport (canvas + HTML overlays)
            # ================================================================
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1,
                bypass_csp=True,
                ignore_https_errors=True,
                record_video_dir='/tmp',  # Enable video recording
                record_video_size={'width': 1920, 'height': 1080}  # Full HD
            )
            
            page = context.new_page()
            
            # Console logging
            def handle_console(msg):
                text = msg.text
                if 'chunk' not in text.lower():  # Don't log chunk messages
                    print(f"  Browser [{msg.type}]: {text}")
            
            def handle_error(err):
                error_msg = str(err)
                print(f"  Browser Error: {error_msg}")
            
            page.on('console', handle_console)
            page.on('pageerror', handle_error)
            
            # Navigate to HTML
            print(f"  📄 Loading HTML file...")
            page.goto(f'file://{html_path}', wait_until='networkidle', timeout=30000)
            
            # Wait for page to be ready
            print(f"  ⏳ Waiting for page ready...")
            page.wait_for_timeout(2000)
            
            # Check if GSAP loaded
            gsap_loaded = page.evaluate("typeof gsap !== 'undefined'")
            lucide_loaded = page.evaluate("typeof lucide !== 'undefined'")
            
            print(f"  📦 Library status:")
            print(f"     GSAP: {'✅ Loaded' if gsap_loaded else '❌ NOT LOADED'}")
            print(f"     Lucide: {'✅ Loaded' if lucide_loaded else '❌ NOT LOADED'}")
            
            # CRITICAL: If GSAP didn't load, FAIL
            if not gsap_loaded:
                context.close()
                browser.close()
                raise Exception(f"GSAP library failed to load")
            
            # Initialize Lucide icons
            try:
                page.evaluate("if (typeof lucide !== 'undefined') lucide.createIcons();")
            except:
                pass
            
            # Wait for animations to initialize
            print(f"  ⏳ Waiting for animations to initialize...")
            page.wait_for_timeout(1000)
            
            print(f"  ✓ Animation ready")
            
            # ================================================================
            # RECORDING: Playwright records entire viewport automatically
            # ================================================================
            print(f"  📹 Recording viewport for {video_duration_sec:.1f}s...")
            
            # Just wait for the duration - Playwright is recording
            start_time = time.time()
            page.wait_for_timeout(int(video_duration_ms))
            actual_duration = time.time() - start_time
            
            print(f"  ✓ Recording complete ({actual_duration:.1f}s)")
            
            # Close page to finalize video
            page.close()
            context.close()
            browser.close()
        
        # ================================================================
        # Get the recorded video file
        # Playwright saves it with a random name in /tmp
        # ================================================================
        import glob
        import shutil
        
        # Find the most recently created .webm file
        webm_files = glob.glob('/tmp/*.webm')
        if not webm_files:
            raise Exception("No video file created by Playwright")
        
        # Get the newest file
        latest_webm = max(webm_files, key=os.path.getctime)
        
        # Move to our expected path
        shutil.move(latest_webm, video_path)
        
        webm_size = os.path.getsize(video_path)
        print(f"✓ [{segment_index}] Video captured: {webm_size} bytes")
        
        if webm_size < 10000:
            raise Exception(f"Video file too small: {webm_size} bytes")
        
    except Exception as e:
        print(f"❌ [{segment_index}] Rendering FAILED: {e}")
        raise Exception(f"Segment {segment_index} rendering failed: {e}")
    
    # STEP 5: Verify video file
    if not os.path.exists(video_path) or os.path.getsize(video_path) < 10000:
        raise Exception(f"Video file invalid: {video_path}")
    
    # STEP 6: Merge with audio using FFmpeg
    mp4_path = f'/tmp/segment_{segment_index}_final.mp4'
    
    try:
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            
            # ✅ VIDEO ENCODING - NORMALIZED FOR CONCATENATION
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-profile:v', 'high',
            '-level', '4.0',
            '-pix_fmt', 'yuv420p',
            
            # ✅ FRAME RATE & TIMING
            '-r', '30',
            '-video_track_timescale', '30000',
            '-vsync', 'cfr',
            
            # ✅ GOP & KEYFRAMES
            '-g', '30',
            '-keyint_min', '30',
            '-sc_threshold', '0',
            
            # ✅ BITRATE CONTROL
            '-b:v', '5000k',
            '-maxrate', '5500k',
            '-bufsize', '10000k',
            
            # ✅ STREAMING OPTIMIZATION
            '-movflags', '+faststart',
            
            # ✅ AUDIO ENCODING - NORMALIZED
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '48000',
            '-ac', '2',
            
            '-shortest',
            mp4_path
        ], capture_output=True, text=True, timeout=FFMPEG_TIMEOUT_SECONDS)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr[:200]}")
        
    except subprocess.TimeoutExpired:
        raise Exception(f"FFmpeg timeout after {FFMPEG_TIMEOUT_SECONDS}s")
    except Exception as e:
        raise Exception(f"FFmpeg error: {e}")
    
    # STEP 7: Verify MP4
    if not os.path.exists(mp4_path) or os.path.getsize(mp4_path) < 10000:
        raise Exception(f"MP4 invalid")
    
    # STEP 8: Read MP4 and encode as base64
    with open(mp4_path, 'rb') as f:
        mp4_bytes = f.read()
    
    mp4_base64 = base64.b64encode(mp4_bytes).decode('utf-8')
    
    print(f"✅ [{segment_index}] Complete: {len(mp4_bytes)} bytes (5 Mbps, concat-ready)")
    
    # Cleanup
    try:
        os.remove(html_path)
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(mp4_path)
    except:
        pass
    
    return mp4_base64


@app.function(
    image=base_image,
    secrets=[secrets],
    timeout=3600,
    cpu=2.0,
    memory=4096,
)
async def process_video_generation(request_dict: dict):
    import sys
    sys.path.insert(0, '/root')
    
    from video_orchestrator_final import VideoOrchestrator
    from supabase import create_client
    
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    video_id = request_dict["video_id"]
    user_id = request_dict["user_id"]
    topic_category = request_dict.get("topic_category", "general")
    
    try:
        orchestrator = VideoOrchestrator(supabase=supabase, render_fn=render_segment_video)
        
        result = await orchestrator.generate_video(
            video_id=video_id,
            user_id=user_id,
            topic_category=topic_category
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            supabase.table('video_generations').update({
                'generation_status': 'failed',
                'generation_error': str(e)
            }).eq('id', video_id).execute()
        except:
            pass
        
        return {"success": False, "error": str(e)}


@app.function(image=base_image, secrets=[secrets])
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import sys
    sys.path.insert(0, '/root')
    from video_config import MODEL_PROVIDER, MODEL_CONFIG, VIDEO_LENGTH_MINUTES, TOTAL_SEGMENTS, USE_AI_ANIMATIONS
    
    class GenerateVideoRequest(BaseModel):
        video_id: str
        user_id: str
        topic_category: str = "general"
    
    web_app = FastAPI(title="Garliq Video Backend v6.1 - Fixed Animation + Concat")
    
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @web_app.get("/")
    def read_root():
        return {
            "status": "Garliq Video Backend v6.1 - Fixed Animation + Concat",
            "version": "6.1.0",
            "active_model_provider": MODEL_PROVIDER,
            "active_model": MODEL_CONFIG[MODEL_PROVIDER]['model'],
            "video_length_minutes": VIDEO_LENGTH_MINUTES,
            "total_segments": TOTAL_SEGMENTS,
            "ai_animations": USE_AI_ANIMATIONS,
            "architecture": "CrewAI script + AI HTML5 animations + Cloudflare Stream",
            "animation_stack": "Canvas2D + SVG + CSS3 + GSAP + Lucide",
            "fixes": [
                "✅ Fixed LLM initialization for CrewAI",
                "✅ Normalized video encoding for perfect concat",
                "✅ Fixed timescale/framerate/GOP for stream-copy",
                "✅ Added comprehensive error logging",
                "✅ Guaranteed <10s concatenation time"
            ],
            "features": [
                "✅ CrewAI script generation",
                "✅ AI-generated HTML5 animations (full autonomy)",
                "✅ Canvas2D + SVG + CSS3 animations",
                "✅ GSAP + Lucide + Chart.js support",
                "✅ Normalized encoding (CFR, fixed timescale)",
                "✅ Ultra-fast stream-copy concatenation",
                "✅ 5 Mbps bitrate streaming",
                "✅ Cloudflare Stream with HLS",
                "✅ Adaptive bitrate (1080p, 720p, 480p)",
                "✅ Global CDN delivery"
            ]
        }
    
    @web_app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "model_provider": MODEL_PROVIDER,
            "ai_animations": USE_AI_ANIMATIONS,
            "animation_architecture": "HTML5 (Canvas + SVG + CSS + GSAP)",
            "agent_autonomy": "FULL",
            "streaming_platform": "Cloudflare Stream",
            "concat_strategy": "normalized-encoding + stream-copy",
            "video_config": {
                "length_minutes": VIDEO_LENGTH_MINUTES,
                "total_segments": TOTAL_SEGMENTS,
                "batch_size": 10,
                "ffmpeg_timeout": 180,
                "bitrate": "5 Mbps",
                "faststart_enabled": True,
                "hls_enabled": True,
                "concat_optimized": True
            }
        }
    
    @web_app.post("/generate-video")
    async def generate_video_endpoint(request: GenerateVideoRequest):
        request_dict = {
            "video_id": request.video_id,
            "user_id": request.user_id,
            "topic_category": request.topic_category
        }
        
        process_video_generation.spawn(request_dict)
        
        return JSONResponse({
            "success": True,
            "message": "Video generation started with fixed AI animations & optimized concatenation",
            "video_id": request.video_id,
            "model_provider": MODEL_PROVIDER,
            "expected_segments": TOTAL_SEGMENTS,
            "ai_animations_enabled": USE_AI_ANIMATIONS,
            "animation_stack": "Canvas2D + SVG + CSS3 + GSAP + Lucide Icons",
            "agent_autonomy": "FULL (chooses best tools per segment)",
            "streaming_platform": "Cloudflare Stream",
            "concat_optimization": "Normalized encoding for <10s stream-copy"
        })
    
    return web_app