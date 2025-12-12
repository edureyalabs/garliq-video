# video_animation_prompts.py

ANIMATION_CODER_ROLE = """Expert HTML/CSS/JavaScript animator who creates educational video segments"""

ANIMATION_CODER_GOAL = """Create professional animated HTML files with text overlays and background effects using GSAP"""

ANIMATION_CODER_BACKSTORY = """You create educational animations similar to Kurzgesagt, TED-Ed, and Khan Academy videos. Your animations feature large text overlays with smooth GSAP animations and beautiful background effects."""

ANIMATION_GENERATION_TASK_TEMPLATE = """Create an animated HTML file for this educational video segment.

SEGMENT INFO:
- Narration: "{segment_text}"
- Visual: "{visual_hint}"
- Segment Number: {segment_index}

CRITICAL REQUIREMENTS - YOUR HTML MUST LOOK LIKE THIS:

1. LOAD THESE LIBRARIES (copy exactly):
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
```

2. CREATE TEXT OVERLAYS (main content):
```html
<div class="overlay">
  <div class="content-container">
    <h1 class="main-title">YOUR TITLE HERE</h1>
    <p class="subtitle">Your subtitle here</p>
    
    <!-- For lists/bullets: -->
    <ul class="key-points">
      <li>
        <i data-lucide="check-circle" class="icon"></i>
        <span>Point 1</span>
      </li>
      <li>
        <i data-lucide="zap" class="icon"></i>
        <span>Point 2</span>
      </li>
    </ul>
    
    <!-- For stats/numbers: -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">100</div>
        <div class="stat-label">Label</div>
      </div>
    </div>
  </div>
</div>
```

3. STYLE WITH GLASS EFFECT (copy exactly):
```css
.content-container {{
  max-width: 1400px;
  padding: 50px 60px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}}

.main-title {{
  font-size: 4rem;
  font-weight: 800;
  color: white;
  text-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}}

.subtitle {{
  font-size: 1.8rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.9);
}}
```

4. ANIMATE WITH GSAP (copy exactly):
```javascript
// Title entrance
gsap.from('.main-title', {{
  scale: 0.5,
  opacity: 0,
  duration: 1.2,
  ease: 'elastic.out(1, 0.5)',
  delay: 0.3
}});

// Subtitle entrance
gsap.from('.subtitle', {{
  y: 30,
  opacity: 0,
  duration: 0.8,
  ease: 'power3.out',
  delay: 0.8
}});

// Bullet points (staggered)
gsap.from('.key-points li', {{
  x: -30,
  opacity: 0,
  duration: 0.6,
  stagger: 0.15,
  ease: 'power3.out',
  delay: 1.2
}});

// Initialize Lucide icons
if (typeof lucide !== 'undefined') lucide.createIcons();
```

5. ADD BACKGROUND (Canvas or CSS):
```javascript
// Simple particle background
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

class Particle {{
  constructor() {{
    this.x = Math.random() * 1920;
    this.y = Math.random() * 1080;
    this.vx = (Math.random() - 0.5) * 2;
    this.vy = (Math.random() - 0.5) * 2;
  }}
  update() {{
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > 1920) this.vx *= -1;
    if (this.y < 0 || this.y > 1080) this.vy *= -1;
  }}
  draw() {{
    ctx.fillStyle = 'rgba(0, 212, 255, 0.5)';
    ctx.beginPath();
    ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
    ctx.fill();
  }}
}}

const particles = Array(100).fill().map(() => new Particle());

function animate() {{
  ctx.clearRect(0, 0, 1920, 1080);
  ctx.fillStyle = '#0a0e27';
  ctx.fillRect(0, 0, 1920, 1080);
  particles.forEach(p => {{ p.update(); p.draw(); }});
  requestAnimationFrame(animate);
}}
animate();
```

6. REQUIRED RECORDING FUNCTION (copy exactly):
```javascript
window.startRecording = function() {{
  return new Promise((resolve) => {{
    setTimeout(() => {{
      window.recordingComplete = true;
      resolve();
    }}, 15000);
  }});
}};
```

WHAT TO CREATE:

Based on the segment text and visual hint:
- If it's an intro (segment 0): Big title + subtitle + dramatic entrance
- If it mentions numbers/stats: Create stat cards with numbers
- If it's a list/steps: Create bullet points with icons
- Otherwise: Title + description + background animation

COLOR SCHEMES (pick one based on topic):
- Technology: Background #0a0e27, Primary #00d4ff, Secondary #8b5cf6
- Business: Background #0f1419, Primary #f59e0b, Secondary #1e40af  
- Health: Background #0a1a0f, Primary #22c55e, Secondary #3b82f6
- Education: Background #1a1410, Primary #f97316, Secondary #06b6d4

EXAMPLE OUTPUT:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Segment {segment_index}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ 
      font-family: 'Poppins', sans-serif;
      width: 1920px; 
      height: 1080px;
      overflow: hidden;
      background: #0a0e27;
      position: relative;
    }}
    
    #canvas {{
      position: absolute;
      top: 0; left: 0;
      width: 1920px; height: 1080px;
      z-index: 1;
    }}
    
    .overlay {{
      position: absolute;
      top: 0; left: 0;
      width: 1920px; height: 1080px;
      z-index: 10;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 60px;
    }}
    
    .content-container {{
      max-width: 1400px;
      width: 100%;
      padding: 50px 60px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      border: 2px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      text-align: center;
    }}
    
    .main-title {{
      font-size: 4rem;
      font-weight: 800;
      color: white;
      text-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      margin-bottom: 20px;
    }}
    
    .subtitle {{
      font-size: 1.8rem;
      font-weight: 300;
      color: rgba(255, 255, 255, 0.9);
      line-height: 1.6;
    }}
    
    .key-points {{
      list-style: none;
      margin-top: 30px;
      text-align: left;
    }}
    
    .key-points li {{
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 20px;
      margin-bottom: 15px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 15px;
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.15);
    }}
    
    .key-points .icon {{
      width: 24px;
      height: 24px;
      color: #00d4ff;
    }}
    
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 25px;
      margin-top: 30px;
    }}
    
    .stat-card {{
      padding: 30px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      border: 2px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }}
    
    .stat-number {{
      font-size: 3rem;
      font-weight: 800;
      color: #00d4ff;
      margin-bottom: 10px;
    }}
    
    .stat-label {{
      font-size: 1rem;
      color: rgba(255, 255, 255, 0.8);
    }}
  </style>
</head>
<body>
  <canvas id="canvas" width="1920" height="1080"></canvas>
  
  <div class="overlay">
    <div class="content-container">
      <h1 class="main-title">YOUR TITLE HERE</h1>
      <p class="subtitle">Your subtitle or description here</p>
      
      <ul class="key-points">
        <li>
          <i data-lucide="check-circle" class="icon"></i>
          <span>First key point</span>
        </li>
        <li>
          <i data-lucide="zap" class="icon"></i>
          <span>Second key point</span>
        </li>
        <li>
          <i data-lucide="star" class="icon"></i>
          <span>Third key point</span>
        </li>
      </ul>
    </div>
  </div>
  
  <script>
    // Canvas background
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    class Particle {{
      constructor() {{
        this.x = Math.random() * 1920;
        this.y = Math.random() * 1080;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.size = Math.random() * 3 + 1;
      }}
      update() {{
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < 0 || this.x > 1920) this.vx *= -1;
        if (this.y < 0 || this.y > 1080) this.vy *= -1;
      }}
      draw() {{
        ctx.fillStyle = 'rgba(0, 212, 255, 0.5)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }}
    }}
    
    const particles = Array(100).fill().map(() => new Particle());
    
    function animate() {{
      ctx.clearRect(0, 0, 1920, 1080);
      ctx.fillStyle = '#0a0e27';
      ctx.fillRect(0, 0, 1920, 1080);
      particles.forEach(p => {{ p.update(); p.draw(); }});
      requestAnimationFrame(animate);
    }}
    animate();
    
    // GSAP animations
    gsap.from('.main-title', {{
      scale: 0.5,
      opacity: 0,
      duration: 1.2,
      ease: 'elastic.out(1, 0.5)',
      delay: 0.3
    }});
    
    gsap.from('.subtitle', {{
      y: 30,
      opacity: 0,
      duration: 0.8,
      ease: 'power3.out',
      delay: 0.8
    }});
    
    gsap.from('.key-points li', {{
      x: -30,
      opacity: 0,
      duration: 0.6,
      stagger: 0.15,
      ease: 'power3.out',
      delay: 1.2
    }});
    
    // Initialize icons
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    // Recording interface
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
</html>
```

NOW CREATE THE HTML:
- Use the structure shown above
- Put actual content based on the segment text
- Choose appropriate layout (title scene, bullet points, or stats)
- Use GSAP for animations
- Use Lucide icons where appropriate
- Include Canvas background with particles
- Return ONLY the complete HTML (no markdown, no explanations)
"""