# video_animation_agent.py
import os
import json
import re
from typing import Optional
from crewai import Agent, Task, Crew
from video_config import MODEL_PROVIDER, MODEL_CONFIG
from video_animation_prompts import (
    ANIMATION_CODER_ROLE,
    ANIMATION_CODER_GOAL,
    ANIMATION_CODER_BACKSTORY,
    ANIMATION_GENERATION_TASK_TEMPLATE
)


class VideoAnimationAgent:
    """AI agent that generates Three.js animation code for video segments"""
    
    def __init__(self):
        """Initialize the animation coding agent with configured LLM"""
        print("🎨 Initializing VideoAnimationAgent")
        print(f"📊 Provider: {MODEL_PROVIDER}")
        print(f"📊 Model: {MODEL_CONFIG[MODEL_PROVIDER]['model']}")
        
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize LLM based on MODEL_PROVIDER"""
        from litellm import completion
        
        config = MODEL_CONFIG[MODEL_PROVIDER]
        
        if MODEL_PROVIDER == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
            return lambda messages: completion(
                model=config['model'],
                messages=messages,
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )
        
        elif MODEL_PROVIDER == "groq":
            os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
            return lambda messages: completion(
                model=config['model'],
                messages=messages,
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
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
        Generate Three.js animation code for a specific segment
        
        Args:
            segment_text: The narration text for this segment
            visual_hint: Description of what to visualize
            segment_index: Index of the segment (0-based)
            
        Returns:
            JavaScript code for Three.js animation
        """
        print(f"🎨 Generating animation code for segment {segment_index}...")
        print(f"   Text: {segment_text[:60]}...")
        print(f"   Hint: {visual_hint}")
        
        # Create the animation coder agent
        animation_coder = Agent(
            role=ANIMATION_CODER_ROLE,
            goal=ANIMATION_CODER_GOAL,
            backstory=ANIMATION_CODER_BACKSTORY,
            llm=MODEL_CONFIG[MODEL_PROVIDER]['model'],
            verbose=False,
            allow_delegation=False
        )
        
        # Create the task
        task_description = ANIMATION_GENERATION_TASK_TEMPLATE.format(
            segment_text=segment_text,
            visual_hint=visual_hint,
            segment_index=segment_index
        )
        
        animation_task = Task(
            description=task_description,
            agent=animation_coder,
            expected_output="Complete Three.js animation JavaScript code"
        )
        
        # Execute with CrewAI
        crew = Crew(
            agents=[animation_coder],
            tasks=[animation_task],
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            
            # Extract JavaScript code from response
            js_code = self._extract_javascript(str(result))
            
            if not js_code:
                print(f"⚠️  No valid JavaScript found, using fallback")
                return self._create_fallback_animation(segment_text, visual_hint, segment_index)
            
            # Validate the code has required elements
            if not self._validate_animation_code(js_code):
                print(f"⚠️  Animation code validation failed, using fallback")
                return self._create_fallback_animation(segment_text, visual_hint, segment_index)
            
            print(f"✅ Animation code generated: {len(js_code)} characters")
            return js_code
            
        except Exception as e:
            print(f"❌ Animation generation failed: {e}")
            return self._create_fallback_animation(segment_text, visual_hint, segment_index)
    
    def _extract_javascript(self, response: str) -> Optional[str]:
        """Extract JavaScript code from AI response"""
        
        # Try to find code in markdown blocks
        patterns = [
            r'```javascript\s*(.*?)\s*```',
            r'```js\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                code = match.group(1).strip()
                if len(code) > 200:  # Reasonable minimum length
                    return code
        
        # If no markdown blocks, try to extract everything between scene creation and animation function
        if 'const scene = new THREE.Scene()' in response and 'window.updateAnimation' in response:
            start = response.find('const scene = new THREE.Scene()')
            end = response.find("console.log('Animation ready')")
            if start != -1 and end != -1:
                return response[start:end + len("console.log('Animation ready')")]
        
        return None
    
    def _validate_animation_code(self, code: str) -> bool:
        """Validate that animation code has required elements"""
        required_elements = [
            'THREE.Scene',
            'THREE.PerspectiveCamera',
            'THREE.WebGLRenderer',
            'window.updateAnimation',
            'renderer.render'
        ]
        
        return all(element in code for element in required_elements)
    
    def _create_fallback_animation(
        self,
        segment_text: str,
        visual_hint: str,
        segment_index: int
    ) -> str:
        """Create a simple fallback animation if AI generation fails"""
        
        # Use segment index to vary colors
        hue = (segment_index * 0.15) % 1.0
        primary_color = f"0x{int(hue * 255):02x}{int((1-hue) * 255):02x}88"
        secondary_color = f"0x88{int(hue * 255):02x}{int((1-hue) * 255):02x}"
        
        return f"""
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a0a);

const camera = new THREE.PerspectiveCamera(75, WIDTH / HEIGHT, 0.1, 1000);
camera.position.z = 30;

const renderer = new THREE.WebGLRenderer({{ 
    canvas: document.getElementById('canvas'), 
    antialias: true,
    alpha: false
}});
renderer.setSize(WIDTH, HEIGHT);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const pointLight = new THREE.PointLight({primary_color}, 1, 100);
pointLight.position.set(20, 20, 20);
scene.add(pointLight);

const geometry = new THREE.IcosahedronGeometry(5, 1);
const material = new THREE.MeshPhongMaterial({{ color: {primary_color}, shininess: 100 }});
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

const particleCount = 300;
const particlesGeo = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
for (let i = 0; i < particleCount * 3; i++) {{
    positions[i] = (Math.random() - 0.5) * 50;
}}
particlesGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
const particlesMat = new THREE.PointsMaterial({{ color: {secondary_color}, size: 0.3 }});
const particles = new THREE.Points(particlesGeo, particlesMat);
scene.add(particles);

window.updateAnimation = function(time) {{
    mesh.rotation.x = time * 0.5;
    mesh.rotation.y = time * 0.3;
    particles.rotation.y = time * 0.1;
    camera.position.x = Math.sin(time * 0.2) * 3;
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
}};

console.log('Animation ready');
"""