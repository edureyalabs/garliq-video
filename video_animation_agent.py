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
    AI agent that generates high-quality HTML5 animation code for video segments.
    Supports full autonomy in choosing tools: Canvas, SVG, CSS, GSAP, Lucide, etc.
    """
    
    def __init__(self):
        """Initialize the animation coding agent with configured LLM"""
        print("🎨 Initializing VideoAnimationAgent (Full Autonomy Mode)")
        print(f"📊 Provider: {MODEL_PROVIDER}")
        print(f"📊 Model: {MODEL_CONFIG[MODEL_PROVIDER]['model']}")
        print(f"🎯 Animation Stack: Canvas2D + SVG + CSS3 + GSAP + Lucide")
        print(f"🤖 Agent Autonomy: FULL (chooses best tools per segment)")
        
        # ✅ FIX: Initialize LLM object properly for CrewAI
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
        Agent has full autonomy to choose: Canvas, SVG, CSS, GSAP, Lucide, etc.
        
        Args:
            segment_text: The narration text for this segment
            visual_hint: Description of what to visualize
            segment_index: Index of the segment (0-based)
            
        Returns:
            Complete HTML document with animation code
        """
        print(f"🎨 Generating animation for segment {segment_index}...")
        print(f"   Narration: {segment_text[:70]}...")
        print(f"   Visual: {visual_hint[:70]}...")
        
        try:
            # Create the animation coder agent with proper LLM object and tools parameter
            animation_coder = Agent(
                role=ANIMATION_CODER_ROLE,
                goal=ANIMATION_CODER_GOAL,
                backstory=ANIMATION_CODER_BACKSTORY,
                llm=self.llm,
                verbose=False,
                allow_delegation=False,
                tools=[]  # ✅ FIX: Add empty tools list to prevent NoneType iteration error
            )
            print(f"  ✓ Agent created successfully")
            
        except Exception as e:
            print(f"  ✗ Agent creation failed: {e}")
            print(f"     Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_animation(segment_text, visual_hint, segment_index)
        
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
            import traceback
            traceback.print_exc()
            return self._create_fallback_animation(segment_text, visual_hint, segment_index)
        
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
            print(f"     Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_animation(segment_text, visual_hint, segment_index)
        
        try:
            # Extract HTML code from response
            html_code = self._extract_html(str(result))
            
            if not html_code:
                print(f"⚠️  No valid HTML found, using fallback")
                return self._create_fallback_animation(segment_text, visual_hint, segment_index)
            
            # Validate the code (flexible validation)
            validation_result = self._validate_animation_code(html_code, segment_index)
            
            if not validation_result['valid']:
                print(f"⚠️  Validation issues: {validation_result['issues']}")
                print(f"⚠️  Using fallback animation")
                return self._create_fallback_animation(segment_text, visual_hint, segment_index)
            
            print(f"✅ Animation generated: {len(html_code)} chars")
            print(f"   Tools detected: {', '.join(validation_result['tools_used'])}")
            return html_code
            
        except Exception as e:
            print(f"❌ HTML extraction/validation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_animation(segment_text, visual_hint, segment_index)
    
    def _extract_html(self, response: str) -> Optional[str]:
        """
        Extract complete HTML document from AI response.
        Handles various response formats with flexibility.
        """
        
        # Remove markdown code blocks if present
        response = re.sub(r'```html\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'```HTML\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()
        
        # Method 1: Find complete HTML document
        doctype_pattern = r'<!DOCTYPE html>.*?</html>'
        match = re.search(doctype_pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            html_code = match.group(0)
            if len(html_code) > 500:  # Reasonable minimum size
                print(f"  ✓ Extracted complete HTML document ({len(html_code)} chars)")
                return html_code
        
        # Method 2: Find HTML tag to closing HTML tag
        html_pattern = r'<html[^>]*>.*?</html>'
        match = re.search(html_pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            html_code = match.group(0)
            # Add DOCTYPE if missing
            if '<!DOCTYPE' not in html_code:
                html_code = '<!DOCTYPE html>\n' + html_code
            if len(html_code) > 500:
                print(f"  ✓ Extracted HTML with added DOCTYPE ({len(html_code)} chars)")
                return html_code
        
        # Method 3: If response looks like HTML (starts with < and ends with >)
        if response.strip().startswith('<') and response.strip().endswith('>'):
            if 'html' in response.lower() or 'canvas' in response.lower():
                # Wrap in basic structure if needed
                if '<html' not in response.lower():
                    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; padding: 0; width: 1920px; height: 1080px; overflow: hidden; }}
        #canvas {{ width: 1920px; height: 1080px; }}
    </style>
</head>
<body>
{response}
<script>
    window.startRecording = function() {{
        return new Promise(resolve => {{
            setTimeout(() => {{
                window.recordingComplete = true;
                resolve();
            }}, 15000);
        }});
    }};
</script>
</body>
</html>"""
                else:
                    html_code = response
                
                if len(html_code) > 500:
                    print(f"  ✓ Wrapped HTML fragments ({len(html_code)} chars)")
                    return html_code
        
        print(f"  ✗ Could not extract valid HTML from response")
        return None
    
    def _validate_animation_code(self, html_code: str, segment_index: int) -> dict:
        """
        Flexible validation that adapts to whatever tools the agent chose.
        Returns validation result with detected tools.
        
        Returns:
            {
                'valid': bool,
                'issues': list of str,
                'tools_used': list of str,
                'animation_type': str
            }
        """
        
        issues = []
        tools_used = []
        animation_type = 'unknown'
        
        # REQUIRED: Basic HTML structure
        if '<!DOCTYPE html>' not in html_code and '<html' not in html_code.lower():
            issues.append("Missing HTML document structure")
        
        # REQUIRED: Canvas element OR SVG elements
        has_canvas = '<canvas' in html_code.lower() and 'id="canvas"' in html_code.lower()
        has_svg = '<svg' in html_code.lower()
        
        if not has_canvas and not has_svg:
            issues.append("Missing canvas element (<canvas id='canvas'>) or SVG elements")
        
        if has_canvas:
            tools_used.append('Canvas2D')
            animation_type = 'canvas-based'
        
        if has_svg:
            tools_used.append('SVG')
            if animation_type == 'canvas-based':
                animation_type = 'hybrid-canvas-svg'
            else:
                animation_type = 'svg-based'
        
        # REQUIRED: Animation mechanism (at least one)
        has_raf = 'requestAnimationFrame' in html_code
        has_css_animation = '@keyframes' in html_code or 'animation:' in html_code
        has_gsap = 'gsap' in html_code.lower() or 'TweenMax' in html_code or 'TimelineMax' in html_code
        
        if not (has_raf or has_css_animation or has_gsap):
            issues.append("No animation mechanism found (requestAnimationFrame, CSS @keyframes, or GSAP)")
        
        if has_raf:
            tools_used.append('RAF-loop')
        if has_css_animation:
            tools_used.append('CSS-animations')
        if has_gsap:
            tools_used.append('GSAP')
        
        # REQUIRED: Recording interface
        has_start_recording = 'window.startRecording' in html_code or 'startRecording' in html_code
        
        if not has_start_recording:
            issues.append("Missing window.startRecording() function")
        
        # DETECT: Optional libraries used
        if 'lucide' in html_code.lower():
            tools_used.append('Lucide-icons')
        
        if 'chart.js' in html_code.lower() or 'Chart(' in html_code:
            tools_used.append('ChartJS')
        
        if 'anime' in html_code.lower() and 'anime(' in html_code:
            tools_used.append('AnimeJS')
        
        # DETECT: Canvas context usage
        if "getContext('2d')" in html_code or 'getContext("2d")' in html_code:
            if 'Canvas2D' not in tools_used:
                tools_used.append('Canvas2D')
        
        # QUALITY CHECKS (warnings, not failures)
        if len(html_code) < 800:
            print(f"  ⚠️  Warning: Code seems short ({len(html_code)} chars)")
        
        if 'fillStyle' not in html_code and 'stroke' not in html_code and '<rect' not in html_code and '<circle' not in html_code:
            print(f"  ⚠️  Warning: No drawing commands detected")
        
        # Determine validity
        is_valid = len(issues) == 0
        
        # Log validation result
        if is_valid:
            print(f"  ✅ Validation passed: {animation_type}")
        else:
            print(f"  ❌ Validation failed: {len(issues)} issue(s)")
            for issue in issues:
                print(f"     - {issue}")
        
        return {
            'valid': is_valid,
            'issues': issues,
            'tools_used': tools_used if tools_used else ['vanilla-js'],
            'animation_type': animation_type
        }
    
    def _create_fallback_animation(
        self,
        segment_text: str,
        visual_hint: str,
        segment_index: int
    ) -> str:
        """
        Create a high-quality fallback animation using Canvas + CSS.
        Uses segment index and text to create varied, professional animations.
        """
        
        # Extract keywords from segment text for context
        keywords = self._extract_keywords(segment_text)
        keyword_display = keywords[0] if keywords else "CONCEPT"
        
        # Color schemes based on segment index (cycling through palettes)
        color_schemes = [
            # Technology/Science (cyan, purple)
            {'bg': '#0a0e27', 'primary': '#00d4ff', 'secondary': '#8b5cf6', 'accent': '#ffffff'},
            # Business (gold, navy)
            {'bg': '#0f1419', 'primary': '#f59e0b', 'secondary': '#1e40af', 'accent': '#ffffff'},
            # Health (green, blue)
            {'bg': '#0a1a0f', 'primary': '#22c55e', 'secondary': '#3b82f6', 'accent': '#ffffff'},
            # Creative (pink, purple)
            {'bg': '#1a0a1a', 'primary': '#ec4899', 'secondary': '#8b5cf6', 'accent': '#f59e0b'},
            # Education (orange, cyan)
            {'bg': '#1a1410', 'primary': '#f97316', 'secondary': '#06b6d4', 'accent': '#fbbf24'},
        ]
        
        scheme = color_schemes[segment_index % len(color_schemes)]
        
        # Animation patterns based on segment position
        is_intro = segment_index == 0
        is_conclusion = segment_index > 5  # Assuming multi-segment video
        
        if is_intro:
            pattern = "intro"  # Bold, attention-grabbing
        elif is_conclusion:
            pattern = "conclusion"  # Satisfying, complete
        else:
            pattern = "content"  # Steady, informative
        
        html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Segment {segment_index} - Fallback Animation</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            overflow: hidden;
            background: {scheme['bg']};
            font-family: 'Arial', 'Helvetica', sans-serif;
            position: relative;
        }}
        
        #canvas {{
            position: absolute;
            top: 0;
            left: 0;
            width: 1920px;
            height: 1080px;
        }}
        
        .overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 1920px;
            height: 1080px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            pointer-events: none;
        }}
        
        .main-text {{
            font-size: 120px;
            font-weight: 800;
            color: {scheme['accent']};
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 10px;
            opacity: 0;
            animation: textFadeIn 1.5s ease-out 0.5s forwards;
            text-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .sub-text {{
            font-size: 48px;
            font-weight: 400;
            color: {scheme['primary']};
            text-align: center;
            margin-top: 40px;
            opacity: 0;
            animation: textFadeIn 1.5s ease-out 1.5s forwards;
        }}
        
        @keyframes textFadeIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .particle {{
            position: absolute;
            width: 8px;
            height: 8px;
            background: {scheme['primary']};
            border-radius: 50%;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <canvas id="canvas" width="1920" height="1080"></canvas>
    
    <div class="overlay">
        <div class="main-text">{keyword_display}</div>
        <div class="sub-text">Educational Animation</div>
    </div>
    
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const WIDTH = 1920;
        const HEIGHT = 1080;
        const centerX = WIDTH / 2;
        const centerY = HEIGHT / 2;
        
        // Particle system
        class Particle {{
            constructor() {{
                this.reset();
            }}
            
            reset() {{
                this.x = Math.random() * WIDTH;
                this.y = Math.random() * HEIGHT;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
                this.size = Math.random() * 3 + 1;
                this.life = 1;
                this.decay = Math.random() * 0.01 + 0.005;
            }}
            
            update() {{
                this.x += this.vx;
                this.y += this.vy;
                this.life -= this.decay;
                
                if (this.life <= 0 || this.x < 0 || this.x > WIDTH || this.y < 0 || this.y > HEIGHT) {{
                    this.reset();
                }}
            }}
            
            draw() {{
                ctx.fillStyle = '{scheme['primary']}' + Math.floor(this.life * 255).toString(16).padStart(2, '0');
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }}
        }}
        
        // Create particles
        const particles = [];
        for (let i = 0; i < 150; i++) {{
            particles.push(new Particle());
        }}
        
        // Geometric shapes
        class GeometricShape {{
            constructor() {{
                this.x = Math.random() * WIDTH;
                this.y = Math.random() * HEIGHT;
                this.size = Math.random() * 100 + 50;
                this.rotation = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 0.02;
                this.type = Math.floor(Math.random() * 3); // 0: circle, 1: square, 2: triangle
                this.opacity = Math.random() * 0.3 + 0.1;
            }}
            
            update() {{
                this.rotation += this.rotationSpeed;
            }}
            
            draw() {{
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                ctx.globalAlpha = this.opacity;
                ctx.strokeStyle = '{scheme['secondary']}';
                ctx.lineWidth = 3;
                
                if (this.type === 0) {{
                    // Circle
                    ctx.beginPath();
                    ctx.arc(0, 0, this.size / 2, 0, Math.PI * 2);
                    ctx.stroke();
                }} else if (this.type === 1) {{
                    // Square
                    ctx.strokeRect(-this.size / 2, -this.size / 2, this.size, this.size);
                }} else {{
                    // Triangle
                    ctx.beginPath();
                    ctx.moveTo(0, -this.size / 2);
                    ctx.lineTo(this.size / 2, this.size / 2);
                    ctx.lineTo(-this.size / 2, this.size / 2);
                    ctx.closePath();
                    ctx.stroke();
                }}
                
                ctx.restore();
            }}
        }}
        
        const shapes = [];
        for (let i = 0; i < 8; i++) {{
            shapes.push(new GeometricShape());
        }}
        
        // Animation loop
        let startTime = null;
        
        function animate(timestamp) {{
            if (!startTime) startTime = timestamp;
            const elapsed = timestamp - startTime;
            const time = elapsed / 1000;
            
            // Clear canvas
            ctx.clearRect(0, 0, WIDTH, HEIGHT);
            
            // Draw gradient background
            const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, WIDTH / 2);
            gradient.addColorStop(0, '{scheme['bg']}');
            gradient.addColorStop(1, '{scheme['bg']}' + '80');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, WIDTH, HEIGHT);
            
            // Update and draw shapes
            shapes.forEach(shape => {{
                shape.update();
                shape.draw();
            }});
            
            // Update and draw particles
            particles.forEach(particle => {{
                particle.update();
                particle.draw();
            }});
            
            // Draw pulsing circle in center
            const pulse = Math.sin(time * 2) * 0.3 + 0.7;
            ctx.strokeStyle = '{scheme['primary']}';
            ctx.lineWidth = 5;
            ctx.globalAlpha = 0.5;
            ctx.beginPath();
            ctx.arc(centerX, centerY, 200 * pulse, 0, Math.PI * 2);
            ctx.stroke();
            ctx.globalAlpha = 1;
            
            requestAnimationFrame(animate);
        }}
        
        // Start animation
        requestAnimationFrame(animate);
        
        // Recording interface
        window.startRecording = function() {{
            return new Promise((resolve) => {{
                console.log('Recording started (fallback animation)');
                setTimeout(() => {{
                    window.recordingComplete = true;
                    console.log('Recording complete');
                    resolve();
                }}, 15000);
            }});
        }};
        
        console.log('Fallback animation ready - Segment {segment_index}');
    </script>
</body>
</html>"""
        
        return html_code
    
    def _extract_keywords(self, text: str) -> list:
        """Extract key words from segment text for fallback animation"""
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                       'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                       'this', 'that', 'these', 'those', 'we', 'you', 'they', 'it', 'its'}
        
        words = text.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if len(w) > 3 and w.lower() not in common_words]
        
        return keywords[:3] if keywords else ['ANIMATION']