# video_animation_agent.py - NO FALLBACK VERSION
# Replace your existing file with this

import os
import re
from typing import Optional
from crewai import Agent, Task, Crew, LLM
from video_config import MODEL_PROVIDER, MODEL_CONFIG
from video_animation_prompts import (
    ANIMATION_CODER_ROLE,
    ANIMATION_CODER_GOAL,
    ANIMATION_CODER_BACKSTORY,
    ANIMATION_GENERATION_TASK_TEMPLATE
)


class VideoAnimationAgent:
    """
    AI agent that generates high-quality HTML5 animation code for video segments.
    NO FALLBACKS - Fails immediately if generation doesn't work.
    """
    
    def __init__(self):
        """Initialize the animation coding agent with configured LLM"""
        print("🎨 Initializing VideoAnimationAgent (NO FALLBACK MODE)")
        print(f"📊 Provider: {MODEL_PROVIDER}")
        print(f"📊 Model: {MODEL_CONFIG[MODEL_PROVIDER]['model']}")
        print(f"🎯 Animation Stack: Canvas2D + SVG + CSS3 + GSAP + Lucide")
        print(f"⚠️  Fallback: DISABLED - Will fail if generation fails")
        
        # Initialize LLM object properly for CrewAI
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize LLM based on MODEL_PROVIDER"""
        
        if MODEL_PROVIDER == "anthropic":
            return LLM(
                model=MODEL_CONFIG[MODEL_PROVIDER]['model'],
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=MODEL_CONFIG[MODEL_PROVIDER]['temperature'],
                max_tokens=MODEL_CONFIG[MODEL_PROVIDER]['max_tokens']
            )
        
        elif MODEL_PROVIDER == "groq":
            return LLM(
                model=MODEL_CONFIG[MODEL_PROVIDER]['model'],
                temperature=MODEL_CONFIG[MODEL_PROVIDER]['temperature']
            )
        
        else:
            raise ValueError(f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER}")
    
    async def generate_animation_code(
        self,
        segment_text: str,
        visual_hint: str,
        segment_index: int
    ) -> str:
        """
        Generate complete HTML animation code for a specific segment.
        FAILS immediately if generation doesn't work (no fallback).
        
        Args:
            segment_text: The narration text for this segment
            visual_hint: Detailed description of what to visualize
            segment_index: Index of the segment (0-based)
            
        Returns:
            Complete HTML document with professional animation code
            
        Raises:
            Exception: If generation or validation fails
        """
        print(f"🎨 Generating animation for segment {segment_index}...")
        print(f"   Narration: {segment_text[:70]}...")
        print(f"   Visual: {visual_hint[:70]}...")
        
        try:
            # Create the animation coder agent
            animation_coder = Agent(
                role=ANIMATION_CODER_ROLE,
                goal=ANIMATION_CODER_GOAL,
                backstory=ANIMATION_CODER_BACKSTORY,
                llm=self.llm,
                verbose=False,
                allow_delegation=False,
                tools=[]
            )
            print(f"  ✓ Agent created successfully")
            
        except Exception as e:
            print(f"  ✗ Agent creation failed: {e}")
            raise Exception(f"Segment {segment_index}: Agent creation failed - {e}")
        
        try:
            # Create the task
            task_description = ANIMATION_GENERATION_TASK_TEMPLATE.format(
                segment_text=segment_text,
                visual_hint=visual_hint,
                segment_index=segment_index
            )
            
            animation_task = Task(
                description=task_description,
                agent=animation_coder,
                expected_output="Complete HTML document with animation code"
            )
            print(f"  ✓ Task created successfully")
            
        except Exception as e:
            print(f"  ✗ Task creation failed: {e}")
            raise Exception(f"Segment {segment_index}: Task creation failed - {e}")
        
        try:
            # Execute with CrewAI
            crew = Crew(
                agents=[animation_coder],
                tasks=[animation_task],
                verbose=False
            )
            print(f"  ✓ Crew created successfully")
            
            result = crew.kickoff()
            print(f"  ✓ Crew execution complete")
            
        except Exception as e:
            print(f"  ✗ Crew execution failed: {e}")
            raise Exception(f"Segment {segment_index}: Crew execution failed - {e}")
        
        try:
            # Extract HTML code from response
            html_code = self._extract_html(str(result))
            
            if not html_code:
                raise Exception(f"Segment {segment_index}: No valid HTML found in AI response")
            
            # Validate the code
            validation_result = self._validate_animation_code(html_code, segment_index)
            
            if not validation_result['valid']:
                issues_str = ', '.join(validation_result['issues'])
                raise Exception(f"Segment {segment_index}: Validation failed - {issues_str}")
            
            print(f"✅ Animation generated: {len(html_code)} chars")
            print(f"   Quality: {validation_result['quality_score']}/100")
            print(f"   Tools: {', '.join(validation_result['tools_used'])}")
            
            return html_code
            
        except Exception as e:
            print(f"❌ HTML extraction/validation failed: {e}")
            raise
    
    def _extract_html(self, response: str) -> Optional[str]:
        """Extract complete HTML document from AI response"""
        
        # Remove markdown code blocks
        response = re.sub(r'```html\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()
        
        # Method 1: Find complete HTML document
        doctype_pattern = r'<!DOCTYPE html>.*?</html>'
        match = re.search(doctype_pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            html_code = match.group(0)
            if len(html_code) > 500:
                print(f"  ✓ Extracted complete HTML document ({len(html_code)} chars)")
                return html_code
        
        # Method 2: Find HTML tag to closing HTML tag
        html_pattern = r'<html[^>]*>.*?</html>'
        match = re.search(html_pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            html_code = match.group(0)
            if '<!DOCTYPE' not in html_code:
                html_code = '<!DOCTYPE html>\n' + html_code
            if len(html_code) > 500:
                print(f"  ✓ Extracted HTML with added DOCTYPE ({len(html_code)} chars)")
                return html_code
        
        print(f"  ✗ Could not extract valid HTML from response")
        return None
    
    def _validate_animation_code(self, html_code: str, segment_index: int) -> dict:
        """
        Validate animation code quality.
        """
        
        issues = []
        warnings = []
        tools_used = []
        quality_score = 100
        
        # REQUIRED: Basic HTML structure
        if '<!DOCTYPE html>' not in html_code and '<html' not in html_code.lower():
            issues.append("Missing HTML document structure")
            quality_score -= 20
        
        # REQUIRED: Canvas element
        has_canvas = '<canvas' in html_code.lower() and 'id="canvas"' in html_code.lower()
        
        if not has_canvas:
            issues.append("Missing canvas element (<canvas id='canvas'>)")
            quality_score -= 20
        else:
            tools_used.append('Canvas2D')
        
        # REQUIRED: GSAP library
        has_gsap = 'gsap' in html_code.lower() and 'cdnjs.cloudflare.com/ajax/libs/gsap' in html_code
        
        if not has_gsap:
            issues.append("Missing GSAP library (required for animations)")
            quality_score -= 20
        else:
            tools_used.append('GSAP')
        
        # REQUIRED: Recording interface
        has_start_recording = 'window.startRecording' in html_code
        
        if not has_start_recording:
            issues.append("Missing window.startRecording() function")
            quality_score -= 20
        
        # REQUIRED: Text overlay structure
        has_overlay = '.overlay' in html_code or 'class="overlay"' in html_code
        
        if not has_overlay:
            warnings.append("Missing .overlay class (text layer)")
            quality_score -= 10
        
        # Check for professional elements
        if 'backdrop-filter' in html_code:
            tools_used.append('Glass-morphism')
            quality_score += 5
        
        if 'text-shadow' in html_code:
            quality_score += 3
        
        if 'gsap.from' in html_code or 'gsap.to' in html_code:
            tools_used.append('GSAP-animations')
            quality_score += 5
        
        if 'lucide' in html_code.lower():
            tools_used.append('Lucide-icons')
        
        # Ensure quality score is in range
        quality_score = max(0, min(100, quality_score))
        
        # Determine validity
        is_valid = len(issues) == 0
        
        # Log result
        if is_valid:
            print(f"  ✅ Validation passed (Quality: {quality_score}/100)")
        else:
            print(f"  ❌ Validation failed: {len(issues)} issue(s)")
            for issue in issues:
                print(f"     - {issue}")
        
        if warnings:
            for warning in warnings:
                print(f"  ⚠️  {warning}")
        
        return {
            'valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'tools_used': tools_used if tools_used else ['vanilla-js'],
            'quality_score': quality_score
        }