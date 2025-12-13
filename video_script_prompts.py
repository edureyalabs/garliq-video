# video_script_prompts.py

SCRIPT_WRITER_ROLE = """Expert educational video script writer specializing in visual storytelling"""

SCRIPT_WRITER_GOAL = """Write clear 30-40 word narration segments with highly detailed, scene-specific visual instructions for animators"""

SCRIPT_WRITER_BACKSTORY = """You write scripts for educational explainer videos similar to Kurzgesagt, TED-Ed, and 3Blue1Brown. For each segment, you provide narration (30-40 words) AND detailed visual scene instructions that tell the animator EXACTLY what to show - specific diagrams, SVG elements, layouts, colors, and animations. Your visual hints are so detailed that an animator can create the scene without any guesswork."""

SCRIPT_GENERATION_TASK_TEMPLATE = """Create a video script for: "{topic}" (Category: {category})

REQUIREMENTS:
- {num_segments} segments total
- Each segment: exactly 30-40 words of narration
- Each segment: HIGHLY DETAILED visual scene instructions (100-200 words)

CRITICAL: Visual hints must be SCENE BLUEPRINTS, not vague descriptions!

BAD Visual Hint (vague):
"Show transistor structure with animated elements"

GOOD Visual Hint (detailed blueprint):
"SCENE TYPE: Diagram. LAYOUT: Center large transistor cross-section (1200px wide). LEFT: Purple rectangle labeled 'Source' (200x150px). TOP: Yellow horizontal bar labeled 'Gate' with arrow pointing down showing 'Vgs' voltage (600x30px). RIGHT: Purple rectangle labeled 'Drain' (200x150px). BOTTOM: Gray substrate bar (800x100px). BETWEEN source-drain: Cyan glowing channel region (600x30px, initially transparent). LABELS: White text, 32px font. ANIMATION: Gate appears first (slide down), then Vgs arrow (fade in), then channel glows (opacity 0→0.8). BACKGROUND: Dark blue gradient (#0f172a to #1e293b). DESCRIPTION BOX: Bottom 20%, white text 2rem: 'When gate voltage exceeds threshold, channel forms allowing current flow.'"

VISUAL HINT TEMPLATE STRUCTURE:

Every visual hint MUST include:
1. **SCENE TYPE:** [Title | Diagram | Process-Flow | Comparison | Stats]
2. **LAYOUT:** [Describe positioning and sizes]
3. **ELEMENTS:** [List all visual elements with exact specs]
4. **LABELS/TEXT:** [All text content and sizes]
5. **COLORS:** [Specific color codes]
6. **ANIMATION:** [What moves/appears and how]
7. **BACKGROUND:** [Gradient or style]

SCENE TYPE TEMPLATES:

═══════════════════════════════════════════════════════════════════

1️⃣ TITLE SCENE (Segment 0, introductions):

Visual Hint Format:
"SCENE TYPE: Title. LAYOUT: Centered full-screen. MAIN TITLE: '[Topic Name]' in 6rem bold white font, gradient effect (white to cyan). SUBTITLE: '[Description]' in 2.5rem light font below, rgba(255,255,255,0.9). ICON: [Relevant icon] 80px size, cyan color (#00d4ff), positioned 50px below subtitle. BACKGROUND: Linear gradient 135deg from [color1] to [color2]. ANIMATION: Title scales from 0.5 to 1 with elastic ease (1.2s), subtitle slides up from +50px with fade (0.8s delay), icon pops in with back ease (1.4s delay)."

Example:
"SCENE TYPE: Title. LAYOUT: Centered full-screen. MAIN TITLE: 'HOW TRANSISTORS WORK' in 6rem bold white font with gradient (white to #00d4ff). SUBTITLE: 'The Tiny Switches Powering Modern Electronics' in 2.5rem light font, rgba(255,255,255,0.9). ICON: cpu icon 80px, cyan (#00d4ff), 50px below subtitle. BACKGROUND: Linear gradient 135deg #0f172a to #1e293b. ANIMATION: Title elastic scale 0.5→1 (1.2s), subtitle slide up +50px fade (0.8s delay), icon back-ease pop (1.4s delay)."

═══════════════════════════════════════════════════════════════════

2️⃣ DIAGRAM SCENE (Technical structures, components):

Visual Hint Format:
"SCENE TYPE: Diagram. TITLE: '[Concept]' 4rem white, top 80px centered. SVG DIAGRAM (1200x800px, centered): [List each element with exact position, size, color, shape]. Element 1: [Shape] at x=[X] y=[Y], size=[WxH], fill=[color], label '[text]'. Element 2: [Shape] at x=[X] y=[Y], size=[WxH], fill=[color], label '[text]'. CONNECTIONS: [Lines/arrows between elements]. LABELS: White 32px font, positioned [where]. DESCRIPTION: Bottom 100px, '[text]' in 2rem white, centered, width 80%. BACKGROUND: [Gradient]. ANIMATION: Title fade-in from top (0.8s), elements stagger left-to-right 0.6s each with 0.2s delay, labels fade after elements, description slide up."

Example:
"SCENE TYPE: Diagram. TITLE: 'Three-Terminal Structure' 4rem white top 80px. SVG DIAGRAM (1200x800px centered): LEFT: Rectangle x=200 y=300 200x150px fill=#8b5cf6 label 'Source' (white 32px above). CENTER-TOP: Rectangle x=350 y=200 600x40px fill=#f59e0b label 'Gate (Control)' (white 32px above). RIGHT: Rectangle x=800 y=300 200x150px fill=#8b5cf6 label 'Drain' (white 32px above). BOTTOM: Rectangle x=300 y=500 700x80px fill=#555 label 'Substrate'. ARROWS: Blue arrow from Gate pointing down to substrate (#00d4ff, 6px width). DESCRIPTION: Bottom 100px 'Three terminals control electron flow between source and drain' 2rem white centered 80% width. BACKGROUND: Linear gradient 135deg #1a1a2e to #16213e. ANIMATION: Title top-fade 0.8s, Source slide-left 0.6s, Gate slide-down 0.6s delay 0.2s, Drain slide-right 0.6s delay 0.4s, substrate fade 0.4s delay 0.8s, labels stagger-fade 0.3s each, description slide-up 0.6s."

═══════════════════════════════════════════════════════════════════

3️⃣ PROCESS/FLOW SCENE (Steps, sequences, workflows):

Visual Hint Format:
"SCENE TYPE: Process-Flow. TITLE: '[Process Name]' 4rem white top 80px. LAYOUT: Horizontal step sequence centered vertically. STEP 1: Box 150x150px background=rgba([color],0.2) border=4px solid [color] border-radius=20px, icon '[icon-name]' 60px [color] centered, title '[Step Name]' 1.8rem white below, description '[text]' 1.2rem rgba(255,255,255,0.8). ARROW: Right arrow 3rem [color] between steps. STEP 2: [Same format]. STEP 3: [Same format]. Total steps: [N]. BACKGROUND: [Gradient]. ANIMATION: Title top-fade 0.8s, Step 1 slide-left fade 0.6s, Arrow 1 scale-in 0.3s, Step 2 slide-left fade 0.6s, Arrow 2 scale-in 0.3s, Step 3 slide-left fade 0.6s."

Example:
"SCENE TYPE: Process-Flow. TITLE: 'Transistor Switching Process' 4rem white top 80px. LAYOUT: Horizontal 3-step sequence centered. STEP 1: Box 150x150px background=rgba(34,197,94,0.2) border=4px solid #22c55e radius=20px, icon 'circle' 60px #22c55e, title 'OFF State' 1.8rem white, description 'No gate voltage' 1.2rem rgba(255,255,255,0.8). ARROW: → 3rem #22c55e. STEP 2: Box same style, icon 'zap' 60px #22c55e, title 'Voltage Applied' 1.8rem white, description 'Gate receives signal' 1.2rem. ARROW: → 3rem #22c55e. STEP 3: Box same style, icon 'check-circle' 60px #22c55e, title 'ON State' 1.8rem white, description 'Current flows' 1.2rem. BACKGROUND: Linear gradient 135deg #0a1f0f to #1a3a1f. ANIMATION: Title top-fade 0.8s, Step 1 slide-in 0.6s, Arrow 1 scale 0.3s, Step 2 slide-in 0.6s, Arrow 2 scale 0.3s, Step 3 slide-in 0.6s."

═══════════════════════════════════════════════════════════════════

4️⃣ COMPARISON SCENE (Before/after, pros/cons, alternatives):

Visual Hint Format:
"SCENE TYPE: Comparison. TITLE: '[Topic]' 4rem white top 80px. LAYOUT: Side-by-side 50/50 split. LEFT SIDE: Background=rgba([color],0.2) border=4px solid [color] radius=30px padding=60px, title '[Option A]' 3rem [color], icon '[icon]' 100px [color], bullet list (font 1.5rem white): '• [point 1]', '• [point 2]', '• [point 3]'. CENTER: VS circle 120px diameter background=[color] white text 3rem bold. RIGHT SIDE: [Same format as left]. BACKGROUND: [Gradient]. ANIMATION: Title top-fade 0.8s, left-side slide-left 0.8s, VS circle rotate scale 0.6s delay 0.4s, right-side slide-right 0.8s delay 0.6s."

Example:
"SCENE TYPE: Comparison. TITLE: 'Voltage States Comparison' 4rem white top 80px. LAYOUT: 50/50 split centered. LEFT: Background=rgba(239,68,68,0.2) border=4px solid #ef4444 radius=30px padding=60px, title 'OFF State (Vgs < Vth)' 3rem #ef4444, icon 'x-circle' 100px #ef4444, bullets 1.5rem white: '• No channel formation', '• High resistance', '• Zero current flow'. CENTER: VS circle 120px #f59e0b white '3rem bold. RIGHT: Background=rgba(34,197,94,0.2) border=4px solid #22c55e radius=30px padding=60px, title 'ON State (Vgs > Vth)' 3rem #22c55e, icon 'check-circle' 100px #22c55e, bullets: '✓ Channel forms', '✓ Low resistance', '✓ Current flows'. BACKGROUND: Linear gradient 135deg #1e1e1e to #2d2d2d. ANIMATION: Title top-fade 0.8s, left slide-left 0.8s, VS rotate-scale 0.6s delay 0.4s, right slide-right 0.8s delay 0.6s."

═══════════════════════════════════════════════════════════════════

5️⃣ STATS/DATA SCENE (Numbers, metrics, achievements):

Visual Hint Format:
"SCENE TYPE: Stats. TITLE: '[Topic]' 4rem white top 80px centered. LAYOUT: Grid [NxM] gap=40px width=80% centered. STAT CARD 1: Background=rgba([color],0.2) border=3px solid [color] radius=25px padding=50px text-center, number '[value]' 5rem bold [color], label '[text]' 1.5rem white margin-top=15px. STAT CARD 2: [Same format]. STAT CARD 3: [Same format]. Total cards: [N]. BACKGROUND: [Gradient]. ANIMATION: Title top-fade 0.8s, cards scale-in stagger 0.6s each with back-ease, delay start 0.4s between cards."

Example:
"SCENE TYPE: Stats. TITLE: 'Transistor Performance Metrics' 4rem white top 80px. LAYOUT: Grid 3-column gap=40px 80% width centered. CARD 1: Background=rgba(59,130,246,0.2) border=3px solid #3b82f6 radius=25px padding=50px, number '10nm' 5rem bold #3b82f6, label 'Feature Size' 1.5rem white margin-top=15px. CARD 2: Background=rgba(245,158,11,0.2) border=3px solid #f59e0b radius=25px padding=50px, number '5GHz' 5rem bold #f59e0b, label 'Switching Speed' 1.5rem white. CARD 3: Background=rgba(139,92,246,0.2) border=3px solid #8b5cf6 radius=25px padding=50px, number '1.2V' 5rem bold #8b5cf6, label 'Operating Voltage' 1.5rem white. BACKGROUND: Linear gradient 135deg #0f1419 to #1a2332. ANIMATION: Title top-fade 0.8s, Card 1 scale-in back-ease 0.6s, Card 2 scale-in back-ease 0.6s delay 0.4s, Card 3 scale-in back-ease 0.6s delay 0.8s."

═══════════════════════════════════════════════════════════════════

TOPIC-SPECIFIC VISUAL ELEMENTS:

When writing visual hints, include TOPIC-SPECIFIC shapes/diagrams:

**For Transistors:**
- Rectangles for Source/Drain terminals
- Horizontal bar for Gate
- Substrate layer
- Channel region (glowing effect)
- Voltage arrows (Vgs, Vds)
- Electron flow particles

**For Biological Processes (e.g., Photosynthesis, Protein Synthesis):**
- Chloroplast/Ribosome shapes (ovals, organelles)
- Arrows showing molecule flow
- Labels for ATP, glucose, amino acids, etc.
- Color-coded molecules (green for chlorophyll, red for oxygen)

**For Mechanical Systems (e.g., Engines, Gears):**
- Pistons (rectangles moving up/down)
- Crankshaft (rotating circles with connecting rods)
- Valves (opening/closing rectangles)
- Fuel droplets, exhaust smoke
- Motion arrows

**For Data/Network Flows:**
- Boxes representing servers/databases
- Arrows showing data flow
- Network nodes (circles)
- Packet animations

**For Business/Economics:**
- Bar charts (SVG rectangles)
- Pie charts (SVG paths)
- Trend arrows (up/down)
- Dollar signs, buildings

**For Chemistry:**
- Molecular structures (circles for atoms, lines for bonds)
- Electron clouds
- Reaction arrows
- Beakers, test tubes

═══════════════════════════════════════════════════════════════════

OUTPUT FORMAT (JSON):
[
  {{
    "index": 0,
    "text": "30-40 word narration here",
    "visual_hint": "SCENE TYPE: Title. LAYOUT: Centered... [full detailed blueprint 100-200 words]"
  }},
  ...
]

STRUCTURE:
- Segments 0-2: Introduction (title + overview)
- Segments 3-{middle_start}: Foundation (key concepts with diagrams)
- Segments {middle_start}-{middle_end}: Details (deep explanations with process flows)
- Segments {middle_end}-{conclusion_start}: Applications (examples, comparisons, stats)
- Segments {conclusion_start}-{num_segments}: Conclusion with comprehensive summary

CONCLUSION REQUIREMENTS (Last 2-3 segments):

The conclusion MUST:
1. Explicitly recap main concepts covered
2. List 3-5 key takeaways
3. Reference specific topics discussed
4. Provide forward-looking perspective

Visual hints for conclusion should be STATS or TITLE scenes showing key takeaways.

CRITICAL REMINDERS:
✅ Visual hints are BLUEPRINTS (100-200 words each)
✅ Include exact positions, sizes, colors, animations
✅ Specify SVG elements (rect, circle, line, polygon)
✅ Name specific Lucide icons (from safe list)
✅ Choose correct scene type (Title/Diagram/Flow/Comparison/Stats)
✅ Make visuals TOPIC-SPECIFIC (not generic)
✅ Each text segment: 30-40 words exactly

Generate the script now:
"""

SCRIPT_REGENERATION_TASK_TEMPLATE = """REGENERATION REQUEST

Original: {original_topic}
Category: {category}
Segments: {num_segments}
Error: {error_message}
Attempt: #{retry_count}

FIXES NEEDED:
{critical_fixes}

MANDATORY VISUAL HINT FORMAT:
Each visual hint MUST be a detailed 100-200 word blueprint including:
- SCENE TYPE: [Title/Diagram/Flow/Comparison/Stats]
- LAYOUT: [Exact positioning]
- ELEMENTS: [All shapes with positions, sizes, colors]
- LABELS: [All text content and sizes]
- ANIMATION: [What animates and how]
- BACKGROUND: [Gradient specification]

MANDATORY CONCLUSION:
Last 2-3 segments must provide specific summary with:
- Exact concepts covered (by name)
- 3-5 concrete key takeaways
- Forward-looking perspective
- Visual hints as STATS or TITLE scenes

Return valid JSON array:
- Each text: 30-40 words
- Each visual_hint: 100-200 word detailed blueprint
- NO markdown, NO extra text
- Start with [, end with ]
"""