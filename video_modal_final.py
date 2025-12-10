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
def render_segment_video(segment: dict, audio_base64: str, audio_duration: float, animation_js: str) -> str:
    """
    Render segment video using AI-generated animation code
    
    Args:
        segment: dict with index, text, visual_hint
        audio_base64: base64-encoded audio WAV data
        audio_duration: duration of audio in seconds
        animation_js: AI-generated JavaScript animation code
        
    Returns:
        Base64-encoded MP4 file data
    """
    from playwright.sync_api import sync_playwright
    import subprocess
    
    # Import config for timeout
    import sys
    sys.path.insert(0, '/root')
    from video_config import FFMPEG_TIMEOUT_SECONDS
    
    segment_index = segment['index']
    segment_text = segment['text']
    
    print(f"🎨 [{segment_index}] Starting: {segment_text[:40]}...")
    print(f"    Audio duration: {audio_duration:.1f}s")
    print(f"    Animation code: {len(animation_js)} chars")
    
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
    
    # STEP 2: Calculate video duration
    video_duration_ms = max(int(audio_duration * 1000) + 1000, 12000)
    
    # STEP 3: Create HTML with AI-generated animation
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #000; overflow: hidden; }}
        #canvas {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <canvas id="canvas" width="1920" height="1080"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const WIDTH = 1920;
        const HEIGHT = 1080;
        const DURATION = {video_duration_ms};
        const FPS = 30;
        
        // AI-GENERATED ANIMATION CODE START
        {animation_js}
        // AI-GENERATED ANIMATION CODE END
        
        let mediaRecorder = null;
        let recordedChunks = [];
        let isRecording = false;
        let animationStartTime = null;
        
        window.startRecording = function() {{
            return new Promise((resolve, reject) => {{
                try {{
                    console.log('Starting recording...');
                    
                    // Warmup
                    for (let i = 0; i < 10; i++) {{
                        if (window.updateAnimation) window.updateAnimation(0);
                    }}
                    
                    const canvas = document.getElementById('canvas');
                    const stream = canvas.captureStream(FPS);
                    
                    mediaRecorder = new MediaRecorder(stream, {{
                        mimeType: 'video/webm;codecs=vp9',
                        videoBitsPerSecond: 10000000
                    }});
                    
                    mediaRecorder.ondataavailable = (e) => {{
                        if (e.data.size > 0) recordedChunks.push(e.data);
                    }};
                    
                    mediaRecorder.onstop = () => {{
                        console.log('Recording stopped, chunks:', recordedChunks.length);
                        const blob = new Blob(recordedChunks, {{ type: 'video/webm' }});
                        const reader = new FileReader();
                        reader.onloadend = () => {{
                            window.recordedVideoData = reader.result.split(',')[1];
                            window.recordingComplete = true;
                            resolve();
                        }};
                        reader.readAsDataURL(blob);
                    }};
                    
                    mediaRecorder.start(100);
                    isRecording = true;
                    animationStartTime = performance.now();
                    
                    function animate() {{
                        if (!isRecording) return;
                        
                        const elapsed = performance.now() - animationStartTime;
                        
                        if (elapsed >= DURATION) {{
                            isRecording = false;
                            mediaRecorder.stop();
                            return;
                        }}
                        
                        const time = elapsed / 1000;
                        
                        try {{
                            if (window.updateAnimation) window.updateAnimation(time);
                        }} catch (err) {{
                            console.error('Animation error:', err);
                        }}
                        
                        requestAnimationFrame(animate);
                    }}
                    
                    animate();
                    
                }} catch (error) {{
                    console.error('Recording error:', error);
                    reject(error);
                }}
            }});
        }};
        
        console.log('Ready');
    </script>
</body>
</html>"""
    
    html_path = f'/tmp/segment_{segment_index}.html'
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"✓ [{segment_index}] HTML created")
    
    # STEP 4: Render with Playwright
    webm_path = f'/tmp/segment_{segment_index}.webm'
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            page.on('console', lambda msg: print(f"  Browser: {msg.text}"))
            page.on('pageerror', lambda err: print(f"  Error: {err}"))
            
            page.goto(f'file://{html_path}')
            page.wait_for_timeout(2000)
            
            page.evaluate('window.startRecording()')
            page.wait_for_function('window.recordingComplete === true', timeout=int(video_duration_ms) + 10000)
            
            video_data_base64 = page.evaluate('window.recordedVideoData')
            
            if not video_data_base64:
                raise Exception("No video data")
            
            with open(webm_path, 'wb') as f:
                f.write(base64.b64decode(video_data_base64))
            
            page.close()
            context.close()
            browser.close()
        
        print(f"✓ [{segment_index}] WebM: {os.path.getsize(webm_path)} bytes")
        
    except Exception as e:
        print(f"❌ [{segment_index}] Playwright failed: {e}")
        raise
    
    # STEP 5: Verify WebM
    if not os.path.exists(webm_path) or os.path.getsize(webm_path) < 10000:
        raise Exception(f"WebM invalid: {webm_path}")
    
    # STEP 6: Merge with audio
    mp4_path = f'/tmp/segment_{segment_index}_final.mp4'
    
    try:
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', webm_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
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
    
    print(f"✅ [{segment_index}] Complete: {len(mp4_bytes)} bytes (returning as base64)")
    
    # Cleanup
    try:
        os.remove(html_path)
        os.remove(webm_path)
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
    
    web_app = FastAPI(title="Garliq Video Backend v4.0 - AI Animation Edition")
    
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
            "status": "Garliq Video Backend v4.0 - AI Animation Edition",
            "version": "4.0.0",
            "active_model_provider": MODEL_PROVIDER,
            "active_model": MODEL_CONFIG[MODEL_PROVIDER]['model'],
            "video_length_minutes": VIDEO_LENGTH_MINUTES,
            "total_segments": TOTAL_SEGMENTS,
            "ai_animations": USE_AI_ANIMATIONS,
            "architecture": "CrewAI-powered script + AI-generated animations",
            "features": [
                "✅ CrewAI script generation",
                "✅ AI-generated Three.js animations per segment",
                "✅ Model provider configuration (Groq/Anthropic)",
                "✅ Dynamic visuals based on content",
                "✅ Fallback animations if AI fails",
                "✅ Batch rendering with proper timeouts",
                "✅ Base64 container transfer",
                "✅ Token deduction"
            ]
        }
    
    @web_app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "model_provider": MODEL_PROVIDER,
            "ai_animations": USE_AI_ANIMATIONS,
            "video_config": {
                "length_minutes": VIDEO_LENGTH_MINUTES,
                "total_segments": TOTAL_SEGMENTS,
                "batch_size": 10,
                "ffmpeg_timeout": 180
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
            "message": "Video generation started with AI animations",
            "video_id": request.video_id,
            "model_provider": MODEL_PROVIDER,
            "expected_segments": TOTAL_SEGMENTS,
            "ai_animations_enabled": USE_AI_ANIMATIONS
        })
    
    return web_app