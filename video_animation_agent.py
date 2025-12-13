# video_animation_agent.py
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
    AI agent that generates complete scene-based HTML animations for educational explainer videos.
    Creates topic-specific SVG diagrams and auto-playing animations.
    """
    
    def __init__(self):
        """Initialize the animation coding agent with configured LLM"""
        print("🎨 Initializing VideoAnimationAgent (Scene-Based Architecture)")
        print(f"📊 Provider: {MODEL_PROVIDER}")
        print(f"📊 Model: {MODEL_CONFIG[MODEL_PROVIDER]['model']}")
        print(f"🎯 Output: Complete auto-playing scene HTML files")
        print(f"🎯 Style: Topic-specific SVG diagrams + GSAP animations")
        
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
        Generate complete scene-based HTML animation code for a specific segment.
        
        Args:
            segment_text: The narration text for this segment
            visual_hint: Detailed description of what to visualize
            segment_index: Index of the segment (0-based)
            
        Returns:
            Complete HTML document with auto-playing scene animation
            
        Raises:
            Exception: If generation or validation fails
        """
        print(f"🎨 Generating scene {segment_index}...")
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
                expected_output="Complete auto-playing scene HTML with topic-specific animations"
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
                print(f"  ⚠️  Validation warnings: {issues_str}")
                # Don't fail, just warn - AI might have created good content anyway
            
            print(f"✅ Scene generated: {len(html_code)} chars")
            print(f"   Quality: {validation_result['quality_score']}/100")
            print(f"   Features: {', '.join(validation_result['features'])}")
            
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
        
        # Method 3: Just look for body tag
        body_pattern = r'<body[^>]*>.*?</body>'
        match = re.search(body_pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            body_code = match.group(0)
            html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Scene</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
</head>
{body_code}
</html>'''
            print(f"  ✓ Extracted body and wrapped in HTML ({len(html_code)} chars)")
            return html_code
        
        print(f"  ✗ Could not extract valid HTML from response")
        return None
    
    def _validate_animation_code(self, html_code: str, segment_index: int) -> dict:
        """
        Validate scene-based animation code quality.
        """
        
        issues = []
        warnings = []
        features = []
        quality_score = 100
        
        # CRITICAL: Full-screen check
        if 'max-width: 1400px' in html_code or 'max-width: 1200px' in html_code or 'max-width: 1000px' in html_code:
            issues.append("Content restricted by max-width (should be full-screen)")
            quality_score -= 15
        
        # Check for viewport size
        if 'width: 1920px' in html_code and 'height: 1080px' in html_code:
            features.append('Full-screen')
            quality_score += 5
        
        # Check for GSAP
        has_gsap = 'gsap' in html_code.lower() and 'cdnjs.cloudflare.com/ajax/libs/gsap' in html_code
        if has_gsap:
            features.append('GSAP')
            
            # Check for timeline (auto-play indicator)
            if 'gsap.timeline()' in html_code or 'gsap.from' in html_code or 'gsap.to' in html_code:
                features.append('Auto-play')
                quality_score += 10
            else:
                warnings.append("GSAP loaded but no animations found")
                quality_score -= 5
        else:
            issues.append("Missing GSAP library")
            quality_score -= 20
        
        # Check for SVG content (topic-specific visuals)
        if '<svg' in html_code:
            features.append('SVG')
            
            # Check for substantive SVG (not just empty)
            svg_elements = len(re.findall(r'<(rect|circle|line|polygon|path|text)', html_code))
            if svg_elements >= 3:
                features.append(f'SVG-rich ({svg_elements} elements)')
                quality_score += 10
            elif svg_elements > 0:
                features.append(f'SVG-basic ({svg_elements} elements)')
                quality_score += 5
        else:
            warnings.append("No SVG content found (might be text-only scene)")
        
        # Check for Lucide icons
        if 'lucide' in html_code.lower():
            features.append('Lucide-icons')
            
            # Check for unsafe icon names
            unsafe_icons = ['memory', 'chip', 'circuit', 'processor', 'code-2']
            for icon in unsafe_icons:
                if f'data-lucide="{icon}"' in html_code:
                    warnings.append(f"Potentially unsafe Lucide icon: '{icon}'")
                    quality_score -= 3
        
        # Check for canvas (we don't want this)
        if '<canvas' in html_code:
            warnings.append("Canvas element found (prefer SVG)")
            quality_score -= 5
        
        # Check for appropriate text sizes
        large_text_found = False
        if 'font-size: 5rem' in html_code or 'font-size: 6rem' in html_code or 'font-size: 4rem' in html_code:
            large_text_found = True
            features.append('Large-text')
            quality_score += 5
        
        if not large_text_found:
            warnings.append("Title text might be too small")
            quality_score -= 5
        
        # Check for gradient backgrounds
        if 'linear-gradient' in html_code or 'radial-gradient' in html_code:
            features.append('Gradient-bg')
        
        # Check for animations/transitions
        if '@keyframes' in html_code or 'animation:' in html_code:
            features.append('CSS-animations')
            quality_score += 5
        
        # Check if Lucide icons are initialized
        if 'lucide.createIcons()' in html_code:
            quality_score += 3
        
        # Ensure quality score is in range
        quality_score = max(0, min(100, quality_score))
        
        # Determine validity
        is_valid = len(issues) == 0 and quality_score >= 50
        
        # Log result
        if is_valid:
            print(f"  ✅ Validation passed (Quality: {quality_score}/100)")
        else:
            print(f"  ⚠️  Validation warnings: {len(issues)} issue(s), {len(warnings)} warning(s)")
            for issue in issues:
                print(f"     - {issue}")
        
        if warnings:
            for warning in warnings:
                print(f"  ℹ️  {warning}")
        
        return {
            'valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'features': features if features else ['basic-html'],
            'quality_score': quality_score
        }