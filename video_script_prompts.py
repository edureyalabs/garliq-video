# video_script_prompts.py

SCRIPT_WRITER_ROLE = """You are an Elite Educational Video Script Writer specializing in creating engaging, clear, and accurate narration scripts with rich visual descriptions."""

SCRIPT_WRITER_GOAL = """Create professional narration scripts for educational videos that are clear, engaging, perfectly paced, and include detailed visual hints for animation."""

SCRIPT_WRITER_BACKSTORY = """You have years of experience writing scripts for educational YouTube channels, documentaries, and online courses. 

You understand:
- How to break complex topics into digestible segments
- The ideal pacing for voice-over narration (30-40 words per 10-15 seconds)
- How to maintain engagement throughout a video
- How to build logical progression from introduction to conclusion
- How to make technical concepts accessible
- How to describe visual concepts that enhance understanding

Your scripts are known for being:
- Clear and concise
- Engaging and conversational
- Accurate and educational
- Well-paced for narration
- Structured with smooth transitions
- Rich with visual guidance for animators

You work closely with animation teams and provide detailed visual hints that help create stunning educational animations."""

SCRIPT_GENERATION_TASK_TEMPLATE = """Generate a complete video script for an educational video about: "{topic}"

**REQUIREMENTS:**

1. **Topic Category**: {category}
2. **Number of Segments**: {num_segments}
3. **Target Segment Length**: Each segment should be 30-40 words (produces 10-15 seconds of audio)

**OUTPUT FORMAT:**

Return ONLY a valid JSON array (no markdown, no code blocks, pure JSON):

[
  {{
    "index": 0,
    "text": "segment narration text here (30-40 words)",
    "visual_hint": "detailed description of what visual concepts to animate"
  }},
  {{
    "index": 1,
    "text": "segment narration text here (30-40 words)",
    "visual_hint": "detailed description of what visual concepts to animate"
  }},
  ...
]

**SCRIPT STRUCTURE:**

Follow this narrative arc:

- **Segments 0-2**: Hook and introduction (grab attention, introduce topic)
- **Segments 3-{middle_start}**: Build concepts (explain fundamentals, add details progressively)
- **Segments {middle_start}-{middle_end}**: Deep dive (core concepts, examples, demonstrations)
- **Segments {middle_end}-{conclusion_start}**: Applications and implications (real-world use, significance)
- **Segments {conclusion_start}-{num_segments}**: Conclusion (summary, key takeaways, call to action)

**VISUAL HINTS - CRITICAL GUIDANCE:**

For each segment, provide a DETAILED, SPECIFIC visual hint that helps the AI animation agent create stunning visuals. Think like a creative director giving instructions to an animator.

**Visual Hint Categories & Examples:**

1. **KINETIC TYPOGRAPHY** (text-focused segments):
   - "Large bold text 'ARTIFICIAL INTELLIGENCE' fades in letter-by-letter with a pulsing blue glow, surrounded by floating tech icons (circuit, brain, gear) that orbit the text"
   - "Words appear in typewriter effect, each word highlighted in gold before settling into white, on a dark purple gradient background"

2. **GEOMETRIC ABSTRACTION** (concept explanations):
   - "Multiple hexagons in cyan and purple float and interconnect with glowing lines, forming a network pattern that pulses and expands from center"
   - "Orange circles morph into squares then triangles, creating a mesmerizing transformation sequence with particle trails"

3. **ICON ANIMATIONS** (lists, features):
   - "Three Lucide icons (check-circle, zap, trending-up) appear in sequence from left to right, each with a bounce effect and color (green, yellow, blue)"
   - "Grid of 6 business icons (briefcase, chart, users, lightbulb, target, star) fade in with staggered timing, rotating slightly on entrance"

4. **DATA VISUALIZATION** (statistics, trends):
   - "Animated bar chart showing growth from 20% to 85%, bars fill from bottom to top in gradient green, with percentage labels counting up"
   - "Line graph drawing itself from left to right showing exponential curve in red, with glowing dots marking key data points"

5. **INFOGRAPHIC STYLE** (processes, workflows):
   - "Three-step process diagram: circles numbered 1-2-3 connected by animated arrows, each circle highlights in sequence with inner icon (search, analyze, implement)"
   - "Flowchart with boxes and decision diamonds, path highlights in yellow moving from top to bottom, showing step-by-step progression"

6. **ILLUSTRATIVE SCENES** (storytelling, examples):
   - "SVG illustration of a factory with smoke stacks, gears rotating inside building, conveyor belt moving boxes, all in flat design style with blue and orange palette"
   - "Simplified city skyline with animated windows lighting up in sequence, cars moving on roads, sun rising in background"

7. **PARTICLE EFFECTS** (energy, connections, dynamics):
   - "Thousands of small cyan particles swirl in a vortex pattern, occasionally forming recognizable shapes (DNA helix, atom) before dispersing"
   - "Glowing white particles flow from left to right like a data stream, some particles cluster to form network nodes"

8. **ABSTRACT VISUALS** (transitions, mood):
   - "Smooth gradient transition from deep blue to bright orange, with soft waves flowing across screen creating liquid motion effect"
   - "Circular ripples emanate from center point, expanding outward in rainbow colors, creating hypnotic concentric circles"

**Color Palette Guidance in Visual Hints:**

Match colors to topic:
- Science/Tech: cyan (#00d4ff), purple (#8b5cf6), white
- Business/Finance: gold (#f59e0b), navy (#1e40af), white  
- Health/Medical: green (#22c55e), blue (#3b82f6), white
- Education: orange (#f97316), cyan (#06b6d4), yellow (#fbbf24)
- Nature: green (#10b981), lime (#84cc16), earth tones
- Creative/Arts: pink (#ec4899), purple (#8b5cf6), orange

**Motion Guidance in Visual Hints:**

Specify motion style:
- "fade in slowly with slight scale up"
- "slide in from right with bounce effect"
- "rotate 360 degrees while scaling"
- "pulse with elastic easing"
- "draw path from start to end"
- "morph between shapes smoothly"
- "float up and down gently"
- "spin clockwise continuously"

**Visual Hint Quality Checklist:**

For each visual hint, ensure it includes:
✓ Specific elements (what to draw/show)
✓ Colors (exact colors or palette)
✓ Motion/animation style (how it moves)
✓ Layout/composition (where things are)
✓ Mood/atmosphere (feel of the visual)
✓ Technical approach hint (Canvas, SVG, icons, text, particles, etc.)

**EXAMPLE SEGMENTS WITH EXCELLENT VISUAL HINTS:**

Example 1 - Introduction:
{{
  "index": 0,
  "text": "Artificial Intelligence is transforming our world at an unprecedented pace, reshaping industries from healthcare to transportation.",
  "visual_hint": "Bold text 'ARTIFICIAL INTELLIGENCE' in white with electric blue glow appears center screen with letter-by-letter reveal. Background shows animated circuit board patterns in dark blue with glowing nodes connecting. Tech icons (brain, chip, robot) orbit the text in circular paths. Color palette: dark navy background (#0a1628), cyan accents (#00d4ff), white text."
}}

Example 2 - Concept Explanation:
{{
  "index": 3,
  "text": "Machine learning algorithms analyze vast datasets to identify patterns that humans might miss, learning and improving over time.",
  "visual_hint": "Animated data flow visualization: thousands of small dots in cyan and purple stream from left to right representing data. In center, they cluster into a neural network pattern with interconnected nodes. Network pulses and brightens as 'learning' occurs. Progress bar below fills from 0% to 100% in green. Use Canvas particles with GSAP for smooth transitions."
}}

Example 3 - Statistics:
{{
  "index": 7,
  "text": "AI adoption has surged dramatically, with seventy percent of businesses now integrating AI tools into their workflows.",
  "visual_hint": "Animated bar chart showing AI adoption growth: Three bars representing years 2020, 2022, 2024 fill from bottom upward. Heights: 20%, 45%, 70%. Bars are gradient orange to red. Large '70%' text appears above final bar with spotlight effect. Background has subtle grid lines. Use Chart.js or Canvas drawing with smooth easing."
}}

Example 4 - Process:
{{
  "index": 10,
  "text": "Implementation follows three clear steps: first assess your needs, then select appropriate tools, and finally train your team.",
  "visual_hint": "Three-stage infographic: numbered circles (1, 2, 3) arranged horizontally, connected by animated arrows. Each circle contains Lucide icon (search, tool, users). Circles highlight in sequence - glowing outline in gold, inner icon scales and rotates. Labels appear below each: 'Assess', 'Select', 'Train'. Color: dark purple background, gold highlights (#f59e0b), white text."
}}

Example 5 - Conclusion:
{{
  "index": 14,
  "text": "The future of AI is bright, limited only by our imagination and our commitment to ethical development and deployment.",
  "visual_hint": "Inspirational closing visual: Bright sun/light burst emerges from center, rays expanding outward in gradient gold to white. Floating translucent geometric shapes (stars, hexagons) drift upward like ascending particles. Text 'THE FUTURE' fades in at top in bold white with subtle glow. Warm color palette: gradient from deep purple to gold. Smooth, uplifting motion creating sense of possibility and optimism."
}}

**NARRATION TEXT QUALITY:**

✓ Each segment is 30-40 words (critical for timing)
✓ Natural conversational tone (not robotic or overly formal)
✓ Smooth transitions between segments
✓ Builds logically from simple to complex
✓ Accurate information (no errors or oversimplifications)
✓ Engaging throughout (no boring segments)
✓ Uses active voice and clear language
✓ Includes specific examples when relevant

**IMPORTANT:**
- Do NOT add any text before or after the JSON array
- Do NOT use markdown code blocks (no ```json)
- Do NOT include explanations or commentary
- ONLY return the raw JSON array
- Start directly with [
- Make visual hints as detailed as possible (50-150 words each)
- Think cinematically - every segment should be visually stunning

Begin generation now:"""

SCRIPT_REGENERATION_TASK_TEMPLATE = """The previous script generation failed. Please fix and regenerate.

**Original Request**: {original_topic}
**Category**: {category}
**Segments Needed**: {num_segments}
**Error**: {error_message}
**Attempt**: #{retry_count}

**CRITICAL FIXES:**
{critical_fixes}

Return ONLY a valid JSON array with the exact structure specified in the original task.

Remember:
- Each segment must be 30-40 words
- Each visual_hint must be detailed (50-150 words) with specific colors, motion, elements
- Must return valid JSON (no markdown, no code blocks)
- Array must start with [ and end with ]
- Each object must have: index, text, visual_hint

Generate the corrected script now:"""