import os
import asyncio
import subprocess
import requests
import time
import base64
import random
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from video_config import (
    TOTAL_SEGMENTS,
    RENDER_BATCH_SIZE,
    FFMPEG_TIMEOUT_SECONDS,
    MAX_RETRY_ATTEMPTS,
    AUDIO_GENERATION_WORKERS,
    AUDIO_API_TIMEOUT,
    VIDEO_RENDER_WORKERS,
    USE_AI_ANIMATIONS,
    ANIMATION_GENERATION_TIMEOUT,
    BACKGROUND_MUSIC_FILES,
    BGM_VOLUME,
    TRANSITION_DURATION,
    TRANSITION_TYPES
)
from video_animation_agent import VideoAnimationAgent
from video_metadata_generator import VideoMetadataGenerator


class VideoOrchestrator:
    def __init__(self, supabase, render_fn):
        self.supabase = supabase
        self.render_fn = render_fn
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.total_segments = TOTAL_SEGMENTS
        self.animation_agent = VideoAnimationAgent()
        self.metadata_generator = VideoMetadataGenerator()
        
    async def generate_video(self, video_id: str, user_id: str, topic_category: str):
        try:
            self._update_status(video_id, 'generating')
            
            video_data = self.supabase.table('video_generations').select('*').eq('id', video_id).single().execute()
            video = video_data.data
            prompt = video['prompt']
            
            print(f"\n{'='*70}")
            print(f"🎬 VIDEO GENERATION STARTED (CLOUDFLARE STREAM + HLS)")
            print(f"{'='*70}")
            print(f"Video ID: {video_id}")
            print(f"Topic: {prompt}")
            print(f"Segments: {self.total_segments}")
            print(f"Batch Size: {RENDER_BATCH_SIZE}")
            print(f"AI Animations: {'Enabled' if USE_AI_ANIMATIONS else 'Disabled'}")
            print(f"Background Music: {len(BACKGROUND_MUSIC_FILES)} tracks @ {BGM_VOLUME}% volume")
            print(f"Transitions: {len(TRANSITION_TYPES)} types @ {TRANSITION_DURATION}s duration")
            print(f"Streaming: Cloudflare Stream with Adaptive HLS")
            print(f"Quality: 5 Mbps 1080p (auto-generates 720p, 480p)")
            print(f"{'='*70}\n")
            
            print("📝 PHASE 0: Generating metadata...")
            metadata_start = time.time()
            
            if not video.get('title') or video.get('title') == 'Educational Video':
                print("  🏷️  Generating title...")
                title = self.metadata_generator.generate_title(prompt)
                print(f"  ✓ Title: {title}")
            else:
                title = video['title']
                print(f"  ✓ Using existing title: {title}")
            
            print("  📄 Generating description...")
            description = self.metadata_generator.generate_description(prompt, title)
            print(f"  ✓ Description: {len(description)} characters")
            
            self.supabase.table('video_generations').update({
                'title': title,
                'description': description
            }).eq('id', video_id).execute()
            
            print(f"✅ Metadata complete ({time.time() - metadata_start:.1f}s)\n")
            
            print("📝 PHASE 1: Generating script with CrewAI...")
            start_time = time.time()
            
            segments = await self._generate_script_segments(prompt, topic_category)
            
            for i, seg in enumerate(segments):
                seg['index'] = i
            
            print(f"✅ Script complete: {len(segments)} segments ({time.time() - start_time:.1f}s)\n")
            
            print(f"🔊 PHASE 2: Generating audio ({AUDIO_GENERATION_WORKERS} workers)...")
            audio_start = time.time()
            
            audio_results = await self._generate_audio_parallel_with_retries(segments)
            
            successful_audio = sum(1 for r in audio_results if r[0] is not None)
            print(f"✅ Audio complete: {successful_audio}/{len(segments)} successful ({time.time() - audio_start:.1f}s)\n")
            
            print("🎬 PHASE 3: Preparing video rendering...")
            
            valid_pairs = []
            for segment, (audio_b64, duration) in zip(segments, audio_results):
                if audio_b64:
                    valid_pairs.append((segment, audio_b64, duration))
                else:
                    print(f"⚠️  Skipping segment {segment['index']}: No valid audio")
            
            if len(valid_pairs) == 0:
                raise Exception("No segments with valid audio")
            
            print(f"✓ Ready to render: {len(valid_pairs)} segments\n")
            
            print(f"🎥 PHASE 4: Rendering videos with AI animations (5 Mbps, normalized)...")
            video_start = time.time()
            
            video_files = await self._render_videos_in_batches(valid_pairs)
            
            successful_videos = len(video_files)
            print(f"✅ Videos complete: {successful_videos}/{len(valid_pairs)} successful ({time.time() - video_start:.1f}s)\n")
            
            if len(video_files) == 0:
                raise Exception("No videos were successfully rendered")
            
            print("🎞️  PHASE 5: Concatenating with transitions + background music...")
            concat_start = time.time()
            
            final_video_path = await self._concatenate_videos_with_transitions(video_files)
            
            concat_time = time.time() - concat_start
            print(f"✅ Concatenation complete ({concat_time:.1f}s)\n")
            
            print("☁️  PHASE 6: Uploading to Cloudflare Stream...")
            upload_start = time.time()
            
            cloudflare_uid, hls_url, mp4_url = await self._upload_to_cloudflare_stream(
                final_video_path, 
                video_id, 
                title
            )
            
            print(f"✅ Upload complete ({time.time() - upload_start:.1f}s)\n")
            
            total_duration = sum(duration for _, _, duration in valid_pairs if duration > 0)
            if total_duration == 0:
                total_duration = len(video_files) * 12
            
            self.supabase.table('video_generations').update({
                'cloudflare_video_uid': cloudflare_uid,
                'video_url': hls_url,
                'mp4_url': mp4_url,
                'generation_status': 'completed',
                'duration_seconds': int(total_duration),
                'generation_error': None
            }).eq('id', video_id).execute()
            
            await self._deduct_tokens(user_id, video_id, len(segments))
            
            print(f"{'='*70}")
            print(f"✨ COMPLETE - CLOUDFLARE STREAM READY")
            print(f"{'='*70}")
            print(f"🎥 Title: {title}")
            print(f"📄 Description: {len(description)} chars")
            print(f"🌐 HLS URL: {hls_url}")
            print(f"📦 MP4 URL: {mp4_url}")
            print(f"⏱️  Concat Time: {concat_time:.1f}s")
            print(f"⚡ Cloudflare Stream Features:")
            print(f"   - Adaptive HLS streaming (1080p, 720p, 480p)")
            print(f"   - Global CDN delivery (285+ cities)")
            print(f"   - Zero buffering guaranteed")
            print(f"   - Automatic quality switching")
            print(f"   - Background music with transitions")
            print(f"{'='*70}\n")
            
            return {
                "success": True,
                "video_url": hls_url,
                "mp4_url": mp4_url,
                "cloudflare_video_uid": cloudflare_uid,
                "title": title,
                "description": description,
                "duration": int(total_duration),
                "segments_rendered": successful_videos,
                "segments_total": len(segments),
                "concat_time_seconds": round(concat_time, 1),
                "streaming_platform": "Cloudflare Stream",
                "streaming_optimized": True
            }
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            self._update_status(video_id, 'failed', str(e))
            raise
    
    async def _generate_script_segments(self, prompt: str, category: str) -> List[Dict[str, Any]]:
        from video_script_agent import VideoScriptAgent
        
        agent = VideoScriptAgent()
        segments = await agent.generate_script_segments(prompt, category, self.total_segments)
        
        return segments
    
    async def _generate_audio_parallel_with_retries(
        self,
        segments: List[Dict]
    ) -> List[Tuple[Optional[str], float]]:
        audio_results = [(None, 0.0)] * len(segments)
        
        with ThreadPoolExecutor(max_workers=AUDIO_GENERATION_WORKERS) as executor:
            future_to_index = {
                executor.submit(self._generate_single_audio_with_retry, seg): seg['index']
                for seg in segments
            }
            
            completed = 0
            total = len(segments)
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                completed += 1
                
                try:
                    audio_b64, duration = future.result()
                    audio_results[index] = (audio_b64, duration)
                    status = "✓" if audio_b64 else "✗"
                    print(f"  [{completed}/{total}] Audio {index}: {status} ({duration:.1f}s)")
                except Exception as e:
                    print(f"  [{completed}/{total}] Audio {index}: ✗ {e}")
                    audio_results[index] = (None, 0.0)
        
        return audio_results
    
    def _generate_single_audio_with_retry(
        self,
        segment: Dict,
        max_retries: int = MAX_RETRY_ATTEMPTS
    ) -> Tuple[Optional[str], float]:
        segment_index = segment['index']
        segment_text = segment['text']
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/audio/speech",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "playai-tts",
                        "input": segment_text,
                        "voice": "Cheyenne-PlayAI",
                        "response_format": "wav"
                    },
                    timeout=AUDIO_API_TIMEOUT
                )
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    
                    if len(audio_bytes) > 1000:
                        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                        estimated_duration = len(audio_bytes) / 172000
                        
                        return (audio_b64, max(estimated_duration, 8.0))
                    else:
                        raise Exception(f"Audio too small: {len(audio_bytes)} bytes")
                else:
                    raise Exception(f"TTS API error: {response.status_code}")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                else:
                    return (None, 0.0)
        
        return (None, 0.0)
    
    async def _render_videos_in_batches(
        self,
        valid_pairs: List[Tuple[Dict, str, float]]
    ) -> List[str]:
        all_video_files = []
        total_segments = len(valid_pairs)
        
        for batch_start in range(0, total_segments, RENDER_BATCH_SIZE):
            batch_end = min(batch_start + RENDER_BATCH_SIZE, total_segments)
            batch = valid_pairs[batch_start:batch_end]
            
            print(f"\n  📦 Batch {batch_start//RENDER_BATCH_SIZE + 1}: Segments {batch_start}-{batch_end-1}")
            
            print(f"  🎨 Generating AI animations for batch...")
            batch_with_animations = await self._generate_batch_animations(batch)
            
            batch_videos = await self._render_video_batch(batch_with_animations)
            all_video_files.extend(batch_videos)
            
            print(f"  ✓ Batch complete: {len(batch_videos)}/{len(batch)} successful\n")
            
            if batch_end < total_segments:
                await asyncio.sleep(2)
        
        return all_video_files
    
    async def _generate_batch_animations(
        self,
        batch: List[Tuple[Dict, str, float]]
    ) -> List[Tuple[Dict, str, float, str]]:
        batch_with_animations = []
        
        for segment, audio_b64, duration in batch:
            if USE_AI_ANIMATIONS:
                try:
                    animation_js = await asyncio.wait_for(
                        self.animation_agent.generate_animation_code(
                            segment_text=segment['text'],
                            visual_hint=segment.get('visual_hint', ''),
                            segment_index=segment['index']
                        ),
                        timeout=ANIMATION_GENERATION_TIMEOUT
                    )
                except Exception as e:
                    print(f"  ⚠️  Animation generation failed for segment {segment['index']}: {e}")
                    animation_js = self._create_fallback_animation(segment, segment['index'])
            else:
                animation_js = self._create_fallback_animation(segment, segment['index'])
            
            batch_with_animations.append((segment, audio_b64, duration, animation_js))
        
        return batch_with_animations
    
    def _create_fallback_animation(self, segment: Dict, index: int) -> str:
        text = segment.get('text', 'Educational Content')
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Segment {index}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ 
  font-family: Arial, sans-serif;
  width: 1920px; 
  height: 1080px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}}
.content {{
  max-width: 1400px;
  padding: 60px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}}
h1 {{
  font-size: 4rem;
  font-weight: 800;
  color: white;
  text-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}}
</style>
</head>
<body>
<div class="content">
  <h1>Educational Video</h1>
</div>
<script>
window.startRecording = function() {{
  return new Promise((resolve) => {{
    setTimeout(() => {{
      window.recordingComplete = true;
      resolve();
    }}, 15000);
  }});
}};
</script>
</body>
</html>"""
    
    async def _render_video_batch(
        self,
        batch: List[Tuple[Dict, str, float, str]]
    ) -> List[str]:
        video_files = []
        tasks = []
        
        for segment, audio_b64, duration, animation_js in batch:
            task = self.render_fn.spawn(segment, audio_b64, duration, animation_js)
            tasks.append((segment['index'], task))
        
        completed = 0
        total = len(tasks)
        
        for segment_index, task in tasks:
            completed += 1
            
            try:
                video_base64 = task.get(timeout=300)
                
                if video_base64 and len(video_base64) > 1000:
                    video_bytes = base64.b64decode(video_base64)
                    video_path = f'/tmp/segment_{segment_index}_final.mp4'
                    
                    with open(video_path, 'wb') as f:
                        f.write(video_bytes)
                    
                    if os.path.exists(video_path) and os.path.getsize(video_path) > 10000:
                        video_files.append(video_path)
                        print(f"    [{completed}/{total}] Video {segment_index}: ✓ ({len(video_bytes)//1024} KB)")
                    else:
                        print(f"    [{completed}/{total}] Video {segment_index}: ✗ File write failed")
                else:
                    print(f"    [{completed}/{total}] Video {segment_index}: ✗ Invalid base64 data")
            except Exception as e:
                print(f"    [{completed}/{total}] Video {segment_index}: ✗ {e}")
        
        return video_files
    
    async def _concatenate_videos_with_transitions(self, video_files: List[str]) -> str:
        if not video_files:
            raise Exception("No video files to concatenate")
        
        def get_index(path: str) -> int:
            import re
            match = re.search(r'segment_(\d+)_final', path)
            return int(match.group(1)) if match else 0
        
        sorted_videos = sorted(video_files, key=get_index)
        
        for video_path in sorted_videos:
            if not os.path.exists(video_path):
                raise Exception(f"Video file missing: {video_path}")
            if os.path.getsize(video_path) < 10000:
                raise Exception(f"Video file too small: {video_path}")
        
        print(f"  📦 Concatenating {len(sorted_videos)} segments with transitions...")
        
        selected_bgm = random.choice(BACKGROUND_MUSIC_FILES)
        bgm_path = f'/root/{selected_bgm}'
        
        if not os.path.exists(bgm_path):
            print(f"  ⚠️  Background music not found: {bgm_path}, proceeding without BGM")
            bgm_path = None
        else:
            print(f"  🎵 Selected background music: {selected_bgm}")
        
        output_path = '/tmp/final_video.mp4'
        
        if len(sorted_videos) == 1:
            print("  ℹ️  Single video, adding background music only...")
            
            if bgm_path:
                try:
                    bgm_volume = BGM_VOLUME / 100.0
                    
                    result = subprocess.run([
                        'ffmpeg', '-y',
                        '-i', sorted_videos[0],
                        '-stream_loop', '-1',
                        '-i', bgm_path,
                        '-filter_complex',
                        f'[1:a]volume={bgm_volume},afade=t=in:st=0:d=2,afade=t=out:st=8:d=2[bgm];'
                        f'[0:a][bgm]amix=inputs=2:duration=first[aout]',
                        '-map', '0:v',
                        '-map', '[aout]',
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-b:a', '192k',
                        '-shortest',
                        output_path
                    ], capture_output=True, text=True, timeout=FFMPEG_TIMEOUT_SECONDS)
                    
                    if result.returncode == 0 and os.path.exists(output_path):
                        print(f"  ✅ Single video with BGM complete")
                        os.remove(sorted_videos[0])
                        return output_path
                except Exception as e:
                    print(f"  ⚠️  BGM mixing failed: {e}, using original video")
            
            import shutil
            shutil.copy(sorted_videos[0], output_path)
            os.remove(sorted_videos[0])
            return output_path
        
        print(f"  🎬 Building transition filter chain...")
        
        transitions = []
        for i in range(len(sorted_videos) - 1):
            transition_type = random.choice(TRANSITION_TYPES)
            transitions.append(transition_type)
            print(f"     Transition {i}: {transition_type}")
        
        video_durations = []
        for vp in sorted_videos:
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                vp
            ], capture_output=True, text=True, timeout=30)
            
            try:
                duration = float(result.stdout.strip())
                video_durations.append(duration)
            except:
                video_durations.append(12.0)
        
        filter_parts = []
        for i in range(len(sorted_videos)):
            filter_parts.append(f'[{i}:v]')
        
        current_label = filter_parts[0]
        
        offset = 0.0
        for i in range(len(sorted_videos) - 1):
            transition = transitions[i]
            offset += video_durations[i] - TRANSITION_DURATION
            
            next_input = filter_parts[i + 1]
            output_label = f'[v{i}]' if i < len(sorted_videos) - 2 else '[vout]'
            
            xfade_filter = f'{current_label}{next_input}xfade=transition={transition}:duration={TRANSITION_DURATION}:offset={offset}{output_label}'
            filter_parts.append(xfade_filter)
            
            current_label = output_label
        
        video_filter = ';'.join(filter_parts[len(sorted_videos):])
        
        input_args = []
        for vp in sorted_videos:
            input_args.extend(['-i', vp])
        
        if bgm_path:
            bgm_volume = BGM_VOLUME / 100.0
            total_video_duration = sum(video_durations) - (len(sorted_videos) - 1) * TRANSITION_DURATION
            
            audio_filter_parts = []
            for i in range(len(sorted_videos)):
                audio_filter_parts.append(f'[{i}:a]')
            
            audio_concat = ''.join(audio_filter_parts) + f'concat=n={len(sorted_videos)}:v=0:a=1[main_audio];'
            
            bgm_filter = f'[{len(sorted_videos)}:a]volume={bgm_volume},afade=t=in:st=0:d=2,afade=t=out:st={total_video_duration-2}:d=2,aloop=loop=-1:size=2e9[bgm];'
            
            audio_mix = '[main_audio][bgm]amix=inputs=2:duration=first[aout]'
            
            full_audio_filter = audio_concat + bgm_filter + audio_mix
            
            full_filter = video_filter + ';' + full_audio_filter
            
            input_args.extend(['-stream_loop', '-1', '-i', bgm_path])
            
            map_args = ['-map', '[vout]', '-map', '[aout]']
        else:
            audio_concat_parts = []
            for i in range(len(sorted_videos)):
                audio_concat_parts.append(f'[{i}:a]')
            
            audio_concat = ''.join(audio_concat_parts) + f'concat=n={len(sorted_videos)}:v=0:a=1[aout]'
            
            full_filter = video_filter + ';' + audio_concat
            
            map_args = ['-map', '[vout]', '-map', '[aout]']
        
        try:
            cmd = [
                'ffmpeg', '-y'
            ] + input_args + [
                '-filter_complex', full_filter
            ] + map_args + [
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-b:v', '5000k',
                '-maxrate', '5500k',
                '-bufsize', '10000k',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-ar', '48000',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=FFMPEG_TIMEOUT_SECONDS * 2
            )
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg failed: {result.stderr[:300]}")
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 100000:
                raise Exception("Output file invalid")
            
            file_size_mb = os.path.getsize(output_path) / 1024 / 1024
            print(f"  ✅ Concatenation with transitions + BGM complete: {file_size_mb:.1f} MB")
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Concatenation timeout after {FFMPEG_TIMEOUT_SECONDS * 2}s")
        except Exception as e:
            raise Exception(f"Concatenation error: {e}")
        
        for vp in sorted_videos:
            try:
                os.remove(vp)
            except:
                pass
        
        return output_path
    
    async def _upload_to_cloudflare_stream(
        self, 
        video_path: str, 
        video_id: str, 
        title: str
    ) -> Tuple[str, str, str]:
        from cloudflare_stream_uploader import CloudflareStreamUploader
        
        uploader = CloudflareStreamUploader()
        
        cloudflare_uid, hls_url, mp4_url = uploader.upload_video(
            video_path=video_path,
            video_id=video_id,
            title=title
        )
        
        try:
            os.remove(video_path)
        except:
            pass
        
        return cloudflare_uid, hls_url, mp4_url
    
    async def _deduct_tokens(self, user_id: str, video_id: str, segment_count: int):
        token_cost = segment_count * 300
        try:
            self.supabase.rpc('deduct_tokens_for_video', {
                'p_user_id': user_id,
                'p_amount': token_cost,
                'p_description': f'Video: {segment_count} segments',
                'p_video_id': video_id
            }).execute()
        except Exception as e:
            print(f"⚠️  Token deduction failed: {e}")
    
    def _update_status(self, video_id: str, status: str, error: str = None):
        update_data = {'generation_status': status}
        if error:
            update_data['generation_error'] = error
        try:
            self.supabase.table('video_generations').update(update_data).eq('id', video_id).execute()
        except:
            pass