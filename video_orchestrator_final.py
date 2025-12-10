# video_orchestrator_final.py
import os
import asyncio
import subprocess
import requests
import time
import base64
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
    ANIMATION_GENERATION_TIMEOUT
)
from video_animation_agent import VideoAnimationAgent


class VideoOrchestrator:
    def __init__(self, supabase, render_fn):
        self.supabase = supabase
        self.render_fn = render_fn
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.total_segments = TOTAL_SEGMENTS
        self.animation_agent = VideoAnimationAgent()
        
    async def generate_video(self, video_id: str, user_id: str, topic_category: str):
        """Main video generation pipeline with AI-generated animations"""
        try:
            self._update_status(video_id, 'generating')
            
            video_data = self.supabase.table('video_generations').select('*').eq('id', video_id).single().execute()
            video = video_data.data
            prompt = video['prompt']
            
            print(f"\n{'='*70}")
            print(f"🎬 VIDEO GENERATION STARTED")
            print(f"{'='*70}")
            print(f"Video ID: {video_id}")
            print(f"Topic: {prompt}")
            print(f"Segments: {self.total_segments}")
            print(f"Batch Size: {RENDER_BATCH_SIZE}")
            print(f"AI Animations: {'Enabled' if USE_AI_ANIMATIONS else 'Disabled'}")
            print(f"{'='*70}\n")
            
            # PHASE 1: Generate script with CrewAI
            print("📝 PHASE 1: Generating script with CrewAI...")
            start_time = time.time()
            
            segments = await self._generate_script_segments(prompt, topic_category)
            
            for i, seg in enumerate(segments):
                seg['index'] = i
            
            print(f"✅ Script complete: {len(segments)} segments ({time.time() - start_time:.1f}s)\n")
            
            # PHASE 2: Generate audio in parallel
            print(f"🔊 PHASE 2: Generating audio ({AUDIO_GENERATION_WORKERS} workers)...")
            audio_start = time.time()
            
            audio_results = await self._generate_audio_parallel_with_retries(segments)
            
            successful_audio = sum(1 for r in audio_results if r[0] is not None)
            print(f"✅ Audio complete: {successful_audio}/{len(segments)} successful ({time.time() - audio_start:.1f}s)\n")
            
            # PHASE 3: Prepare valid segment-audio pairs
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
            
            # PHASE 4: Render videos in BATCHES with AI animations
            print(f"🎥 PHASE 4: Rendering videos with AI animations...")
            video_start = time.time()
            
            video_files = await self._render_videos_in_batches(valid_pairs)
            
            successful_videos = len(video_files)
            print(f"✅ Videos complete: {successful_videos}/{len(valid_pairs)} successful ({time.time() - video_start:.1f}s)\n")
            
            if len(video_files) == 0:
                raise Exception("No videos were successfully rendered")
            
            # PHASE 5: Concatenate
            print("🎞️  PHASE 5: Concatenating...")
            concat_start = time.time()
            
            final_video_path = await self._concatenate_videos(video_files)
            
            print(f"✅ Concatenation complete ({time.time() - concat_start:.1f}s)\n")
            
            # PHASE 6: Upload
            print("☁️  PHASE 6: Uploading...")
            upload_start = time.time()
            
            video_url = await self._upload_to_storage(final_video_path, video_id)
            
            print(f"✅ Upload complete ({time.time() - upload_start:.1f}s)\n")
            
            # Calculate actual duration from audio
            total_duration = sum(duration for _, _, duration in valid_pairs if duration > 0)
            if total_duration == 0:
                total_duration = len(video_files) * 12  # Fallback estimate
            
            # Update database
            self.supabase.table('video_generations').update({
                'video_url': video_url,
                'generation_status': 'completed',
                'duration_seconds': int(total_duration),
                'generation_error': None
            }).eq('id', video_id).execute()
            
            await self._deduct_tokens(user_id, video_id, len(segments))
            
            print(f"{'='*70}")
            print(f"✨ COMPLETE: {video_url}")
            print(f"{'='*70}\n")
            
            return {
                "success": True,
                "video_url": video_url,
                "duration": int(total_duration),
                "segments_rendered": successful_videos,
                "segments_total": len(segments)
            }
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            self._update_status(video_id, 'failed', str(e))
            raise
    
    async def _generate_script_segments(self, prompt: str, category: str) -> List[Dict[str, Any]]:
        """Generate script using CrewAI agent"""
        from video_script_agent import VideoScriptAgent
        
        agent = VideoScriptAgent()
        segments = await agent.generate_script_segments(prompt, category, self.total_segments)
        
        return segments
    
    async def _generate_audio_parallel_with_retries(
        self,
        segments: List[Dict]
    ) -> List[Tuple[Optional[str], float]]:
        """Generate audio for all segments in parallel with retry logic"""
        
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
        """Generate audio with retry logic, return (base64_audio, duration_seconds)"""
        
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
                        "voice": "Fritz-PlayAI",
                        "response_format": "wav"
                    },
                    timeout=AUDIO_API_TIMEOUT
                )
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    
                    if len(audio_bytes) > 1000:
                        # Encode to base64
                        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                        
                        # Estimate duration from byte size
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
        """Render videos in batches with AI-generated animations"""
        
        all_video_files = []
        total_segments = len(valid_pairs)
        
        # Process in batches
        for batch_start in range(0, total_segments, RENDER_BATCH_SIZE):
            batch_end = min(batch_start + RENDER_BATCH_SIZE, total_segments)
            batch = valid_pairs[batch_start:batch_end]
            
            print(f"\n  📦 Batch {batch_start//RENDER_BATCH_SIZE + 1}: Segments {batch_start}-{batch_end-1}")
            
            # Generate animations for this batch
            print(f"  🎨 Generating AI animations for batch...")
            batch_with_animations = await self._generate_batch_animations(batch)
            
            # Render videos
            batch_videos = await self._render_video_batch(batch_with_animations)
            all_video_files.extend(batch_videos)
            
            print(f"  ✓ Batch complete: {len(batch_videos)}/{len(batch)} successful\n")
            
            # Small delay between batches
            if batch_end < total_segments:
                await asyncio.sleep(2)
        
        return all_video_files
    
    async def _generate_batch_animations(
        self,
        batch: List[Tuple[Dict, str, float]]
    ) -> List[Tuple[Dict, str, float, str]]:
        """Generate AI animation code for each segment in batch"""
        
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
                    animation_js = self.animation_agent._create_fallback_animation(
                        segment['text'],
                        segment.get('visual_hint', ''),
                        segment['index']
                    )
            else:
                animation_js = self.animation_agent._create_fallback_animation(
                    segment['text'],
                    segment.get('visual_hint', ''),
                    segment['index']
                )
            
            batch_with_animations.append((segment, audio_b64, duration, animation_js))
        
        return batch_with_animations
    
    async def _render_video_batch(
        self,
        batch: List[Tuple[Dict, str, float, str]]
    ) -> List[str]:
        """Render a batch of videos with AI-generated animations"""
        
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
    
    async def _concatenate_videos(self, video_files: List[str]) -> str:
        """Concatenate all video files in order"""
        
        if not video_files:
            raise Exception("No video files to concatenate")
        
        def get_index(path: str) -> int:
            import re
            match = re.search(r'segment_(\d+)_final', path)
            return int(match.group(1)) if match else 0
        
        sorted_videos = sorted(video_files, key=get_index)
        
        concat_file = '/tmp/concat_list.txt'
        with open(concat_file, 'w') as f:
            for video_path in sorted_videos:
                if os.path.exists(video_path):
                    f.write(f"file '{video_path}'\n")
        
        output_path = '/tmp/final_video.mp4'
        
        result = subprocess.run([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Concat failed: {result.stderr}")
        
        os.remove(concat_file)
        for vp in sorted_videos:
            try:
                os.remove(vp)
            except:
                pass
        
        return output_path
    
    async def _upload_to_storage(self, video_path: str, video_id: str) -> str:
        """Upload final video to Supabase storage"""
        
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        
        storage_path = f"videos/{video_id}.mp4"
        
        try:
            self.supabase.storage.from_('videos').remove([storage_path])
        except:
            pass
        
        self.supabase.storage.from_('videos').upload(
            storage_path,
            video_bytes,
            {'content-type': 'video/mp4'}
        )
        
        url = self.supabase.storage.from_('videos').get_public_url(storage_path)
        return url
    
    async def _deduct_tokens(self, user_id: str, video_id: str, segment_count: int):
        """Deduct tokens for video generation"""
        
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
        """Update video generation status"""
        
        update_data = {'generation_status': status}
        if error:
            update_data['generation_error'] = error
        try:
            self.supabase.table('video_generations').update(update_data).eq('id', video_id).execute()
        except:
            pass