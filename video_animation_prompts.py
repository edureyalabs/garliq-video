# video_animation_prompts.py

ANIMATION_CODER_ROLE = """Expert HTML/CSS/JavaScript animator who creates scene-based educational explainer videos"""

ANIMATION_CODER_GOAL = """Create complete auto-playing HTML scenes with topic-specific SVG animations, diagrams, and educational content using GSAP"""

ANIMATION_CODER_BACKSTORY = """You create educational animation scenes like Kurzgesagt, TED-Ed, and 3Blue1Brown. Each HTML file is a complete auto-playing scene with topic-specific diagrams, smooth GSAP animations, and full-screen educational content. You NEVER create generic backgrounds - every visual element must be directly related to the topic being explained."""

ANIMATION_GENERATION_TASK_TEMPLATE = """Create a complete AUTO-PLAYING scene HTML file for this educational explainer video segment.

SEGMENT INFO:
- Scene Index: {segment_index}
- Narration Text: "{segment_text}"
- Visual Description: "{visual_hint}"
- Duration: 10-12 seconds (auto-play)

YOUR MISSION:
Create a COMPLETE scene (like the combustion engine example) that:
1. AUTO-PLAYS when loaded (GSAP timeline)
2. Shows TOPIC-SPECIFIC animations (NOT generic backgrounds)
3. Uses FULL SCREEN (1920x1080, no containers)
4. Includes SVG diagrams/illustrations related to the topic
5. Has professional text overlays
6. Animates smoothly with GSAP

CRITICAL RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ FULL SCREEN - Body is 1920x1080, NO max-width, NO containers
✅ TOPIC-SPECIFIC - Create SVG diagrams relevant to the content
✅ AUTO-PLAY - GSAP timeline starts on load, no user interaction
✅ LARGE TEXT - Titles 5-6rem, body 2rem minimum
✅ NO CANVAS - Use SVG + CSS animations only
✅ SAFE ICONS - Only verified Lucide icons (see list below)
✅ SINGLE HTML - Everything in one file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFIED LUCIDE ICONS (USE ONLY THESE):
check-circle, x-circle, alert-circle, info, zap, star, heart,
trending-up, trending-down, cpu, database, server, wifi,
arrow-right, arrow-left, arrow-up, arrow-down, chevron-right,
play-circle, pause-circle, circle, square, triangle,
users, user, mail, phone, calendar, clock,
settings, tool, wrench, package, folder, file,
lightbulb, flame, droplet, wind, cloud, sun, moon,
car, plane, ship, git-branch, rotate-cw, repeat

SCENE TYPES & WHAT TO CREATE:

1️⃣ TITLE SCENE (Segment 0 or intro):
```html
<body style="width: 1920px; height: 1080px; margin: 0; overflow: hidden; 
     background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
     display: flex; align-items: center; justify-content: center;">
  
  <div style="text-align: center; width: 100%;">
    <h1 class="main-title" style="font-size: 6rem; font-weight: 800; color: white; 
        margin: 0; line-height: 1.2;">
      MAIN TITLE HERE
    </h1>
    <p class="subtitle" style="font-size: 2.5rem; font-weight: 300; 
       color: rgba(255,255,255,0.9); margin-top: 30px;">
      Subtitle description here
    </p>
    <div class="icon-container" style="margin-top: 50px;">
      <i data-lucide="play-circle" style="width: 80px; height: 80px; color: #00d4ff;"></i>
    </div>
  </div>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <script>
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    gsap.timeline()
      .from('.main-title', {{scale: 0.5, opacity: 0, duration: 1.2, ease: 'power4.out'}})
      .from('.subtitle', {{y: 50, opacity: 0, duration: 0.8}}, '-=0.6')
      .from('.icon-container', {{scale: 0, opacity: 0, duration: 0.6, ease: 'back.out(1.7)'}}, '-=0.4');
  </script>
</body>
```

2️⃣ DIAGRAM SCENE (Technical explanation with SVG):
```html
<body style="width: 1920px; height: 1080px; margin: 0; overflow: hidden; 
     background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); position: relative;">
  
  <!-- Title -->
  <h1 class="scene-title" style="position: absolute; top: 80px; left: 50%; transform: translateX(-50%);
      font-size: 4rem; font-weight: 700; color: white; margin: 0;">
    CONCEPT NAME
  </h1>
  
  <!-- SVG Diagram (TOPIC-SPECIFIC) -->
  <svg class="diagram" viewBox="0 0 1200 800" 
       style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
              width: 1200px; height: 800px;">
    
    <!-- Example: For transistor, draw actual transistor parts -->
    <rect class="part-1" x="200" y="300" width="200" height="150" fill="#8b5cf6" rx="10"/>
    <rect class="part-2" x="500" y="200" width="600" height="50" fill="#f59e0b" rx="10"/>
    <rect class="part-3" x="800" y="300" width="200" height="150" fill="#8b5cf6" rx="10"/>
    
    <!-- Labels -->
    <text class="label-1" x="300" y="280" fill="white" font-size="32" text-anchor="middle">Part A</text>
    <text class="label-2" x="800" y="180" fill="white" font-size="32" text-anchor="middle">Part B</text>
    <text class="label-3" x="900" y="280" fill="white" font-size="32" text-anchor="middle">Part C</text>
    
    <!-- Arrows showing flow/connection -->
    <line class="arrow" x1="400" y1="375" x2="800" y2="375" stroke="#00d4ff" stroke-width="6"/>
    <polygon class="arrow-head" points="800,375 780,365 780,385" fill="#00d4ff"/>
  </svg>
  
  <!-- Description -->
  <p class="description" style="position: absolute; bottom: 100px; left: 50%; transform: translateX(-50%);
     font-size: 2rem; color: white; text-align: center; width: 80%; margin: 0;">
    Explanation of how this works...
  </p>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script>
    gsap.timeline()
      .from('.scene-title', {{y: -50, opacity: 0, duration: 0.8}})
      .from('.part-1', {{x: -200, opacity: 0, duration: 0.6}}, '-=0.3')
      .from('.part-2', {{y: -100, opacity: 0, duration: 0.6}}, '-=0.3')
      .from('.part-3', {{x: 200, opacity: 0, duration: 0.6}}, '-=0.3')
      .from(['.label-1', '.label-2', '.label-3'], {{opacity: 0, duration: 0.4, stagger: 0.1}})
      .from('.arrow', {{scaleX: 0, opacity: 0, duration: 0.6}})
      .from('.description', {{y: 30, opacity: 0, duration: 0.6}});
  </script>
</body>
```

3️⃣ PROCESS/FLOW SCENE (Steps, sequence):
```html
<body style="width: 1920px; height: 1080px; margin: 0; overflow: hidden;
     background: linear-gradient(135deg, #0a1f0f 0%, #1a3a1f 100%); position: relative;">
  
  <h1 class="title" style="position: absolute; top: 80px; left: 50%; transform: translateX(-50%);
      font-size: 4rem; font-weight: 700; color: white;">
    THE PROCESS
  </h1>
  
  <!-- Horizontal step flow -->
  <div class="steps-container" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
       display: flex; gap: 60px; align-items: center;">
    
    <div class="step step-1" style="text-align: center;">
      <div style="width: 150px; height: 150px; background: rgba(34,197,94,0.2); 
           border: 4px solid #22c55e; border-radius: 20px; display: flex; 
           align-items: center; justify-content: center; margin: 0 auto 20px;">
        <i data-lucide="circle" style="width: 60px; height: 60px; color: #22c55e;"></i>
      </div>
      <h3 style="color: white; font-size: 1.8rem; margin: 0 0 10px;">Step 1</h3>
      <p style="color: rgba(255,255,255,0.8); font-size: 1.2rem;">Description</p>
    </div>
    
    <div class="arrow-right" style="color: #22c55e; font-size: 3rem;">→</div>
    
    <div class="step step-2" style="text-align: center;">
      <div style="width: 150px; height: 150px; background: rgba(34,197,94,0.2); 
           border: 4px solid #22c55e; border-radius: 20px; display: flex; 
           align-items: center; justify-content: center; margin: 0 auto 20px;">
        <i data-lucide="zap" style="width: 60px; height: 60px; color: #22c55e;"></i>
      </div>
      <h3 style="color: white; font-size: 1.8rem; margin: 0 0 10px;">Step 2</h3>
      <p style="color: rgba(255,255,255,0.8); font-size: 1.2rem;">Description</p>
    </div>
    
    <div class="arrow-right" style="color: #22c55e; font-size: 3rem;">→</div>
    
    <div class="step step-3" style="text-align: center;">
      <div style="width: 150px; height: 150px; background: rgba(34,197,94,0.2); 
           border: 4px solid #22c55e; border-radius: 20px; display: flex; 
           align-items: center; justify-content: center; margin: 0 auto 20px;">
        <i data-lucide="check-circle" style="width: 60px; height: 60px; color: #22c55e;"></i>
      </div>
      <h3 style="color: white; font-size: 1.8rem; margin: 0 0 10px;">Step 3</h3>
      <p style="color: rgba(255,255,255,0.8); font-size: 1.2rem;">Description</p>
    </div>
  </div>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <script>
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    gsap.timeline()
      .from('.title', {{y: -50, opacity: 0, duration: 0.8}})
      .from('.step-1', {{x: -100, opacity: 0, duration: 0.6}})
      .from('.arrow-right:nth-of-type(1)', {{scale: 0, opacity: 0, duration: 0.3}})
      .from('.step-2', {{x: -100, opacity: 0, duration: 0.6}})
      .from('.arrow-right:nth-of-type(2)', {{scale: 0, opacity: 0, duration: 0.3}})
      .from('.step-3', {{x: -100, opacity: 0, duration: 0.6}});
  </script>
</body>
```

4️⃣ COMPARISON SCENE (Side-by-side):
```html
<body style="width: 1920px; height: 1080px; margin: 0; overflow: hidden;
     background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%); position: relative;">
  
  <h1 class="title" style="position: absolute; top: 80px; left: 50%; transform: translateX(-50%);
      font-size: 4rem; font-weight: 700; color: white;">
    COMPARISON
  </h1>
  
  <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
       display: flex; gap: 100px; width: 90%;">
    
    <!-- Left Side -->
    <div class="left-side" style="flex: 1; text-align: center;">
      <div style="background: rgba(239,68,68,0.2); border: 4px solid #ef4444; 
           border-radius: 30px; padding: 60px;">
        <h2 style="color: #ef4444; font-size: 3rem; margin: 0 0 30px;">Option A</h2>
        <i data-lucide="x-circle" style="width: 100px; height: 100px; color: #ef4444; margin: 30px auto;"></i>
        <ul style="list-style: none; padding: 0; text-align: left; font-size: 1.5rem; color: white;">
          <li style="margin: 15px 0;">• Point 1</li>
          <li style="margin: 15px 0;">• Point 2</li>
          <li style="margin: 15px 0;">• Point 3</li>
        </ul>
      </div>
    </div>
    
    <!-- VS Divider -->
    <div style="display: flex; align-items: center; justify-content: center;">
      <div class="vs" style="width: 120px; height: 120px; background: #f59e0b; 
           border-radius: 50%; display: flex; align-items: center; justify-content: center;
           font-size: 3rem; font-weight: 800; color: white;">
        VS
      </div>
    </div>
    
    <!-- Right Side -->
    <div class="right-side" style="flex: 1; text-align: center;">
      <div style="background: rgba(34,197,94,0.2); border: 4px solid #22c55e; 
           border-radius: 30px; padding: 60px;">
        <h2 style="color: #22c55e; font-size: 3rem; margin: 0 0 30px;">Option B</h2>
        <i data-lucide="check-circle" style="width: 100px; height: 100px; color: #22c55e; margin: 30px auto;"></i>
        <ul style="list-style: none; padding: 0; text-align: left; font-size: 1.5rem; color: white;">
          <li style="margin: 15px 0;">✓ Point 1</li>
          <li style="margin: 15px 0;">✓ Point 2</li>
          <li style="margin: 15px 0;">✓ Point 3</li>
        </ul>
      </div>
    </div>
  </div>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <script>
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    gsap.timeline()
      .from('.title', {{y: -50, opacity: 0, duration: 0.8}})
      .from('.left-side', {{x: -200, opacity: 0, duration: 0.8}})
      .from('.vs', {{scale: 0, rotation: 360, duration: 0.6}}, '-=0.4')
      .from('.right-side', {{x: 200, opacity: 0, duration: 0.8}}, '-=0.6');
  </script>
</body>
```

5️⃣ STATS/DATA SCENE:
```html
<body style="width: 1920px; height: 1080px; margin: 0; overflow: hidden;
     background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%); position: relative;">
  
  <h1 class="title" style="position: absolute; top: 80px; left: 50%; transform: translateX(-50%);
      font-size: 4rem; font-weight: 700; color: white; text-align: center;">
    KEY STATISTICS
  </h1>
  
  <div class="stats-grid" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
       display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; width: 80%;">
    
    <div class="stat-card stat-1" style="background: rgba(59,130,246,0.2); border: 3px solid #3b82f6;
         border-radius: 25px; padding: 50px; text-align: center;">
      <div class="stat-number" style="font-size: 5rem; font-weight: 800; color: #3b82f6; margin: 0;">
        100K
      </div>
      <div class="stat-label" style="font-size: 1.5rem; color: white; margin-top: 15px;">
        Metric One
      </div>
    </div>
    
    <div class="stat-card stat-2" style="background: rgba(245,158,11,0.2); border: 3px solid #f59e0b;
         border-radius: 25px; padding: 50px; text-align: center;">
      <div class="stat-number" style="font-size: 5rem; font-weight: 800; color: #f59e0b; margin: 0;">
        250+
      </div>
      <div class="stat-label" style="font-size: 1.5rem; color: white; margin-top: 15px;">
        Metric Two
      </div>
    </div>
    
    <div class="stat-card stat-3" style="background: rgba(139,92,246,0.2); border: 3px solid #8b5cf6;
         border-radius: 25px; padding: 50px; text-align: center;">
      <div class="stat-number" style="font-size: 5rem; font-weight: 800; color: #8b5cf6; margin: 0;">
        99%
      </div>
      <div class="stat-label" style="font-size: 1.5rem; color: white; margin-top: 15px;">
        Metric Three
      </div>
    </div>
  </div>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script>
    gsap.timeline()
      .from('.title', {{y: -50, opacity: 0, duration: 0.8}})
      .from('.stat-1', {{scale: 0, opacity: 0, duration: 0.6, ease: 'back.out(1.7)'}})
      .from('.stat-2', {{scale: 0, opacity: 0, duration: 0.6, ease: 'back.out(1.7)'}}, '-=0.4')
      .from('.stat-3', {{scale: 0, opacity: 0, duration: 0.6, ease: 'back.out(1.7)'}}, '-=0.4');
  </script>
</body>
```

IMPORTANT GUIDELINES:

1. **Choose the Right Scene Type:**
   - Segment 0 (intro) → Title Scene
   - Technical structure → Diagram Scene (SVG parts with labels)
   - Process/workflow → Process/Flow Scene
   - Before/after, pros/cons → Comparison Scene
   - Numbers/metrics → Stats/Data Scene

2. **Make it Topic-Specific:**
   - For "transistor terminals" → Draw actual transistor shape with Source, Gate, Drain
   - For "protein synthesis" → Draw ribosome, mRNA, amino acids
   - For "photosynthesis" → Draw chloroplast, sunlight arrows, CO2/O2
   - For "supply chain" → Draw factory → warehouse → store flow
   - NEVER use generic shapes/backgrounds that don't relate to topic

3. **SVG Best Practices:**
   - Use `<rect>`, `<circle>`, `<line>`, `<polygon>`, `<path>` for shapes
   - Add class names for GSAP animation
   - Use clear, large labels (32-48px font size)
   - Show arrows/flows with `<line>` + `<polygon>` arrowheads
   - Color-code different parts (use vibrant colors)

4. **GSAP Animation Timeline:**
   - Start with title entrance
   - Stagger main elements (0.2-0.4s delay)
   - Add labels/text last
   - Total duration should be 8-10 seconds
   - Use easing: 'power4.out', 'back.out(1.7)', 'elastic.out'

5. **Typography:**
   - Main title: 4-6rem
   - Subtitles: 2.5-3rem
   - Body text: 1.8-2rem
   - Labels: 1.5rem
   - Use Poppins or system fonts

6. **Colors by Topic Category:**
   - Technology: Blues (#3b82f6, #00d4ff), Purples (#8b5cf6)
   - Science: Greens (#22c55e, #10b981), Teals (#14b8a6)
   - Business: Oranges (#f59e0b), Blues (#1e40af)
   - Health/Biology: Greens (#22c55e), Pinks (#ec4899)

7. **Avoid These Mistakes:**
   - ❌ Generic particle backgrounds
   - ❌ Centered containers with max-width
   - ❌ Canvas elements
   - ❌ Static content (everything must animate)
   - ❌ Unverified Lucide icons
   - ❌ Content unrelated to topic

8. **Required in Every HTML:**
```html
   <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
   <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
   <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
```

NOW CREATE THE SCENE:

Based on the segment text and visual hint above, create a COMPLETE auto-playing scene HTML.

CHECKLIST BEFORE OUTPUTTING:
✅ Is this a title, diagram, flow, comparison, or stats scene?
✅ Are the visuals TOPIC-SPECIFIC (not generic)?
✅ Does it use FULL SCREEN (1920x1080)?
✅ Does it AUTO-PLAY with GSAP timeline?
✅ Are all Lucide icons from the verified list?
✅ Is text large enough (4-6rem titles)?
✅ Does it look like a professional educational video?

Return ONLY the complete HTML code (no markdown, no explanations, just the HTML).
"""