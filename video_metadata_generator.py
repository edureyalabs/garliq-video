# video_metadata_generator.py
import os
import requests
from typing import Optional


class VideoMetadataGenerator:
    """
    Generates video metadata (title and description) using Groq API
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
    
    def generate_title(self, prompt: str) -> str:
        """
        Generate a catchy YouTube-style title for the video
        
        Args:
            prompt: User's video topic/prompt
            
        Returns:
            Generated title (max 60 characters)
        """
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert YouTube video title creator. Create catchy, engaging titles that attract viewers while accurately representing the content."
                        },
                        {
                            "role": "user",
                            "content": f'Generate a short, catchy title (max 60 chars) for this educational video topic: "{prompt}". Return ONLY the title, nothing else. No quotes, no extra text.'
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 50
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                title = data['choices'][0]['message']['content'].strip()
                
                # Remove quotes if present
                title = title.strip('"').strip("'")
                
                # Ensure max length
                if len(title) > 60:
                    title = title[:57] + "..."
                
                return title
            else:
                print(f"⚠️  Title generation API error: {response.status_code}")
                return self._create_fallback_title(prompt)
                
        except Exception as e:
            print(f"⚠️  Title generation failed: {e}")
            return self._create_fallback_title(prompt)
    
    def generate_description(self, prompt: str, title: str) -> str:
        """
        Generate a comprehensive article-style description for the video
        
        Args:
            prompt: User's video topic/prompt
            title: Generated video title
            
        Returns:
            Generated description (800-1000 words)
        """
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert educational content writer. Create engaging, informative, and comprehensive descriptions for educational videos."
                        },
                        {
                            "role": "user",
                            "content": f'''Write a comprehensive 800-1000 word article-style description for an educational video titled "{title}" about: "{prompt}".

The description should:
- Start with an engaging hook that captures attention
- Explain the topic clearly and thoroughly
- Include key concepts and why they matter
- Provide context and real-world applications
- Be educational yet accessible to a general audience
- End with key takeaways or conclusions

Write in a friendly, conversational, yet informative tone.
Do NOT use markdown formatting (no #, **, etc).
Write in plain text paragraphs separated by double line breaks.
Return ONLY the description text, nothing else.'''
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                description = data['choices'][0]['message']['content'].strip()
                
                # Clean up any markdown that slipped through
                description = description.replace('**', '').replace('##', '').replace('#', '')
                
                return description
            else:
                print(f"⚠️  Description generation API error: {response.status_code}")
                return self._create_fallback_description(prompt, title)
                
        except Exception as e:
            print(f"⚠️  Description generation failed: {e}")
            return self._create_fallback_description(prompt, title)
    
    def _create_fallback_title(self, prompt: str) -> str:
        """Create a simple fallback title if API fails"""
        # Take first 50 chars of prompt and add "Explained"
        clean_prompt = prompt[:50].strip()
        if len(prompt) > 50:
            return f"{clean_prompt}... Explained"
        return f"{clean_prompt} - Educational Video"
    
    def _create_fallback_description(self, prompt: str, title: str) -> str:
        """Create a basic fallback description if API fails"""
        return f"""Welcome to this educational video about {prompt}.

In this comprehensive video, we explore the fascinating topic of {title}. This subject is important because it helps us understand fundamental concepts that impact various aspects of our world.

Throughout this video, we break down complex ideas into easy-to-understand segments. Each section builds upon the previous one, ensuring a complete understanding of the topic.

Key concepts covered include the foundational principles, practical applications, and real-world examples that demonstrate how this knowledge can be applied.

Whether you're a student, professional, or simply curious about this topic, this video provides valuable insights that will enhance your understanding.

The content is designed to be accessible yet informative, making it suitable for learners at various levels. We focus on clarity and engagement to ensure the material is both educational and enjoyable.

By the end of this video, you'll have a solid grasp of the core concepts and be able to apply this knowledge in practical situations.

Thank you for watching, and we hope you find this educational content valuable. Don't forget to explore more videos on related topics to deepen your understanding further."""