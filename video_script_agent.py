# video_script_agent.py
import os
import json
from typing import List, Dict, Any
from crewai import Agent, Crew, Task, LLM
from video_config import MODEL_PROVIDER, MODEL_CONFIG, TOTAL_SEGMENTS
from video_script_prompts import (
    SCRIPT_WRITER_ROLE,
    SCRIPT_WRITER_GOAL,
    SCRIPT_WRITER_BACKSTORY,
    SCRIPT_GENERATION_TASK_TEMPLATE,
    SCRIPT_REGENERATION_TASK_TEMPLATE
)


class VideoScriptAgent:
    """
    CrewAI-powered video script generation agent
    """
    
    def __init__(self, model_provider: str = MODEL_PROVIDER):
        """Initialize the video script agent with specified model provider"""
        
        self.model_provider = model_provider
        self.model_config = MODEL_CONFIG[model_provider]
        
        print(f"🤖 Initializing VideoScriptAgent")
        print(f"📊 Provider: {model_provider}")
        print(f"📊 Model: {self.model_config['model']}")
        
        # Initialize LLM
        if model_provider == "anthropic":
            self.llm = LLM(
                model=self.model_config['model'],
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens']
            )
        else:  # groq
            self.llm = LLM(
                model=self.model_config['model'],
                temperature=self.model_config['temperature']
            )
        
        # Create script writer agent
        self.script_agent = Agent(
            role=SCRIPT_WRITER_ROLE,
            goal=SCRIPT_WRITER_GOAL,
            backstory=SCRIPT_WRITER_BACKSTORY,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=2
        )
    
    async def generate_script_segments(
        self,
        prompt: str,
        category: str,
        num_segments: int = None,
        retry_count: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Generate video script segments using CrewAI
        
        Args:
            prompt: Video topic/prompt
            category: Topic category
            num_segments: Number of segments (defaults to config value)
            retry_count: Current retry attempt
            
        Returns:
            List of segment dictionaries with index, text, visual_hint
        """
        
        if num_segments is None:
            num_segments = TOTAL_SEGMENTS
        
        print(f"📝 Generating script for: {prompt[:60]}...")
        print(f"📊 Segments: {num_segments} | Category: {category}")
        
        try:
            # Calculate segment ranges for prompt
            middle_start = max(3, num_segments // 4)
            middle_end = num_segments - max(3, num_segments // 5)
            conclusion_start = num_segments - max(2, num_segments // 10)
            
            # Build task description
            if retry_count > 0:
                task_description = SCRIPT_REGENERATION_TASK_TEMPLATE.format(
                    original_topic=prompt,
                    category=category,
                    num_segments=num_segments,
                    error_message="Previous generation failed validation",
                    retry_count=retry_count,
                    critical_fixes="""
- Ensure each segment is exactly 30-40 words
- Return ONLY JSON array (no markdown, no extra text)
- Each object must have: index (int), text (string), visual_hint (string)
- Array must start with [ and end with ]
                    """
                )
            else:
                task_description = SCRIPT_GENERATION_TASK_TEMPLATE.format(
                    topic=prompt,
                    category=category,
                    num_segments=num_segments,
                    middle_start=middle_start,
                    middle_end=middle_end,
                    conclusion_start=conclusion_start
                )
            
            # Create task
            task = Task(
                description=task_description,
                expected_output=f"Valid JSON array with {num_segments} segment objects",
                agent=self.script_agent
            )
            
            # Execute with CrewAI
            crew = Crew(
                agents=[self.script_agent],
                tasks=[task],
                verbose=False
            )
            
            result = await crew.kickoff_async()
            raw_output = result.raw
            
            print("📦 Parsing script response...")
            
            # Extract JSON
            json_content = self._extract_json(raw_output)
            segments = json.loads(json_content)
            
            # Validate
            if not self._validate_segments(segments, num_segments):
                raise ValueError("Generated segments failed validation")
            
            print(f"✅ Script generated: {len(segments)} segments")
            
            # Ensure indices are correct
            for i, seg in enumerate(segments):
                seg['index'] = i
            
            return segments
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return self._create_fallback_segments(prompt, num_segments)
        
        except Exception as e:
            print(f"❌ Script generation error: {e}")
            return self._create_fallback_segments(prompt, num_segments)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON array from LLM response"""
        
        text = text.strip()
        
        # Remove markdown code blocks
        text = text.replace('```json\n', '')
        text = text.replace('```json', '')
        text = text.replace('\n```', '')
        text = text.replace('```', '')
        
        # Remove "Final Answer:" prefix
        if 'Final Answer:' in text:
            text = text.split('Final Answer:')[-1].strip()
        
        # Find JSON array
        start = text.find('[')
        end = text.rfind(']') + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")
        
        json_str = text[start:end]
        print(f"📝 Extracted JSON: {len(json_str)} characters")
        
        return json_str
    
    def _validate_segments(self, segments: list, expected_count: int) -> bool:
        """Validate generated segments"""
        
        if not isinstance(segments, list):
            print("❌ Response is not a list")
            return False
        
        if len(segments) < expected_count * 0.8:  # Allow 20% tolerance
            print(f"❌ Too few segments: {len(segments)}/{expected_count}")
            return False
        
        # Validate each segment
        for i, seg in enumerate(segments):
            if not isinstance(seg, dict):
                print(f"❌ Segment {i} is not a dict")
                return False
            
            if 'text' not in seg or not seg['text']:
                print(f"❌ Segment {i} missing text")
                return False
            
            if 'visual_hint' not in seg:
                seg['visual_hint'] = "Abstract geometric animation"
            
            # Check word count (should be 30-40 words) - just warn, don't fail
            word_count = len(seg['text'].split())
            if word_count < 20 or word_count > 60:
                print(f"⚠️  Segment {i} word count: {word_count} (expected 30-40)")
        
        print("✅ Validation passed")
        return True
    
    def _create_fallback_segments(self, topic: str, num_segments: int) -> List[Dict[str, Any]]:
        """Create fallback segments if AI generation fails"""
        
        print(f"⚠️  Using fallback script for: {topic}")
        
        segments = []
        
        # Introduction
        segments.append({
            "index": 0,
            "text": f"Welcome to this educational video about {topic}. Today we'll explore this fascinating subject in depth and understand its key concepts.",
            "visual_hint": "Title animation with dynamic shapes"
        })
        
        # Body segments
        section_count = num_segments - 2
        for i in range(1, section_count + 1):
            segments.append({
                "index": i,
                "text": f"In this section, we examine an important aspect of {topic}. Understanding these fundamentals helps build a complete picture of the topic.",
                "visual_hint": f"Animated visualization - variation {i}"
            })
        
        # Conclusion
        segments.append({
            "index": num_segments - 1,
            "text": f"We've covered the essential concepts of {topic}. Continue exploring to deepen your understanding. Thank you for watching this educational video.",
            "visual_hint": "Conclusion animation with summary"
        })
        
        return segments