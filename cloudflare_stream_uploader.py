# cloudflare_stream_uploader.py
import os
import requests
import time
from typing import Tuple, Optional

class CloudflareStreamUploader:
    """Upload videos to Cloudflare Stream with automatic HLS conversion"""
    
    def __init__(self):
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.api_token = os.getenv('CLOUDFLARE_STREAM_TOKEN')
        
        if not self.account_id or not self.api_token:
            raise Exception("Missing Cloudflare credentials: CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_STREAM_TOKEN")
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/stream"
        
        print(f"☁️  Cloudflare Stream initialized (Account: {self.account_id[:8]}...)")
    
    def upload_video(
        self, 
        video_path: str, 
        video_id: str,
        title: str = None
    ) -> Tuple[str, str, str]:
        """
        Upload video to Cloudflare Stream
        
        Args:
            video_path: Local path to MP4 file
            video_id: Your internal video ID
            title: Video title (optional)
        
        Returns:
            (cloudflare_video_uid, hls_url, mp4_url)
        """
        
        print(f"☁️  Starting Cloudflare Stream upload: {video_id}")
        print(f"   File: {video_path}")
        print(f"   Size: {os.path.getsize(video_path) / 1024 / 1024:.1f} MB")
        
        # Read video file
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        
        # Step 1: Create direct upload URL
        print("  1️⃣  Creating upload URL...")
        create_response = requests.post(
            f"{self.base_url}/direct_upload",
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            json={
                "maxDurationSeconds": 3600,  # 1 hour max duration
                "requireSignedURLs": False,   # Public videos (can be watched by anyone)
                "allowedOrigins": ["*"],      # Allow playback from any domain
                "meta": {
                    "name": title or video_id,
                    "internal_id": video_id
                }
            },
            timeout=30
        )
        
        if create_response.status_code != 200:
            raise Exception(f"Failed to create upload URL: {create_response.text}")
        
        upload_data = create_response.json()['result']
        upload_url = upload_data['uploadURL']
        cloudflare_video_uid = upload_data['uid']
        
        print(f"  ✓ Upload URL created")
        print(f"  ✓ Cloudflare UID: {cloudflare_video_uid}")
        
        # Step 2: Upload video to Cloudflare using POST with multipart form data
        print(f"  2️⃣  Uploading {len(video_bytes) / 1024 / 1024:.1f} MB...")
        upload_response = requests.post(
            upload_url,
            files={
                'file': ('video.mp4', video_bytes, 'video/mp4')
            },
            timeout=600  # 10 minutes for upload
        )
        
        if upload_response.status_code not in [200, 201]:
            raise Exception(f"Upload failed: {upload_response.text}")
        
        print(f"  ✓ Upload complete!")
        
        # Step 3: Wait for Cloudflare to process video (converts to HLS automatically)
        print(f"  3️⃣  Processing video (HLS conversion)...")
        ready = self._wait_for_processing(cloudflare_video_uid, max_wait=300)
        
        if not ready:
            raise Exception("Video processing timeout (5 minutes)")
        
        # Step 4: Get video details to extract correct playback URLs
        video_info = self.get_video_info(cloudflare_video_uid)
        
        # Extract URLs from Cloudflare response (they provide the correct subdomain)
        playback_info = video_info.get('playback', {})
        hls_url = playback_info.get('hls')
        dash_url = playback_info.get('dash')
        
        # If HLS URL not in playback, construct it using the preview URL pattern
        if not hls_url:
            preview_url = video_info.get('preview', '')
            if preview_url:
                # Extract customer subdomain from preview URL
                # Format: https://customer-xxx.cloudflarestream.com/uid/...
                import re
                match = re.search(r'(https://customer-[^/]+\.cloudflarestream\.com)', preview_url)
                if match:
                    base_url = match.group(1)
                    hls_url = f"{base_url}/{cloudflare_video_uid}/manifest/video.m3u8"
                    mp4_url = f"{base_url}/{cloudflare_video_uid}/downloads/default.mp4"
        
        # Fallback: use account-based URL if extraction failed
        if not hls_url:
            hls_url = f"https://customer-{self.account_id}.cloudflarestream.com/{cloudflare_video_uid}/manifest/video.m3u8"
            mp4_url = f"https://customer-{self.account_id}.cloudflarestream.com/{cloudflare_video_uid}/downloads/default.mp4"
        else:
            # Derive MP4 URL from HLS URL
            mp4_url = hls_url.replace('/manifest/video.m3u8', '/downloads/default.mp4')
        
        print(f"  ✅ Video ready on Cloudflare Stream!")
        print(f"     HLS URL: {hls_url}")
        print(f"     MP4 URL: {mp4_url}")
        print(f"     Cloudflare automatically generated:")
        print(f"       - 1080p quality")
        print(f"       - 720p quality")
        print(f"       - 480p quality")
        print(f"       - Adaptive bitrate streaming")
        
        return cloudflare_video_uid, hls_url, mp4_url
    
    def _wait_for_processing(self, cloudflare_video_uid: str, max_wait: int = 300) -> bool:
        """
        Wait for Cloudflare to finish processing video
        
        Args:
            cloudflare_video_uid: Cloudflare's video UID
            max_wait: Maximum seconds to wait
            
        Returns:
            True if ready, False if timeout
        """
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < max_wait:
            try:
                # Check video status
                response = requests.get(
                    f"{self.base_url}/{cloudflare_video_uid}",
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()['result']
                    status_info = data.get('status', {})
                    state = status_info.get('state', 'unknown')
                    
                    # Only print if status changed
                    if state != last_status:
                        print(f"     Status: {state}")
                        last_status = state
                    
                    if state == 'ready':
                        duration = data.get('duration', 0)
                        print(f"  ✓ Processing complete! Duration: {duration:.1f}s")
                        return True
                    
                    elif state == 'error':
                        error_msg = status_info.get('errorReasonText', 'Unknown error')
                        raise Exception(f"Cloudflare processing failed: {error_msg}")
                    
                    elif state in ['queued', 'inprogress', 'downloading']:
                        # Video is still processing
                        pass
                    
                    else:
                        print(f"     Unknown status: {state}")
                
            except requests.exceptions.Timeout:
                print(f"     Status check timeout, retrying...")
            except Exception as e:
                print(f"     Error checking status: {e}")
            
            time.sleep(10)  # Check every 10 seconds
        
        return False
    
    def delete_video(self, cloudflare_video_uid: str) -> bool:
        """
        Delete video from Cloudflare Stream
        
        Args:
            cloudflare_video_uid: Cloudflare's video UID
            
        Returns:
            True if deleted successfully
        """
        
        try:
            response = requests.delete(
                f"{self.base_url}/{cloudflare_video_uid}",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=30
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to delete video: {e}")
            return False
    
    def get_video_info(self, cloudflare_video_uid: str) -> dict:
        """
        Get video information from Cloudflare
        
        Args:
            cloudflare_video_uid: Cloudflare's video UID
            
        Returns:
            Video metadata dict
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/{cloudflare_video_uid}",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['result']
            else:
                return {}
        except Exception as e:
            print(f"Failed to get video info: {e}")
            return {}