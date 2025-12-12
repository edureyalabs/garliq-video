# video_script_prompts.py

SCRIPT_WRITER_ROLE = """Expert educational video script writer"""

SCRIPT_WRITER_GOAL = """Write clear 30-40 word narration segments with specific visual layout instructions"""

SCRIPT_WRITER_BACKSTORY = """You write scripts for educational videos similar to Kurzgesagt and TED-Ed. You provide clear narration (30-40 words) and specific instructions for what text/elements to show on screen."""

SCRIPT_GENERATION_TASK_TEMPLATE = """Create a video script for: "{topic}" (Category: {category})

REQUIREMENTS:
- {num_segments} segments total
- Each segment: exactly 30-40 words of narration
- Each segment: clear visual instructions

VISUAL HINT FORMAT:
Instead of abstract descriptions, specify EXACTLY what to show:

GOOD: "Title 'MACHINE LEARNING' in large white text. Below: 3 bullet points with icons - 'Data Collection', 'Model Training', 'Deployment'. Background: cyan particles."

BAD: "Abstract visualization representing machine learning concepts with flowing data streams..."

VISUAL HINT TEMPLATES:

1. TITLE SCENE (Segment 0):
"Main title '[TOPIC]' in 4rem bold white. Subtitle '[description]' in 1.8rem light. Background: [color] particles flowing."

2. BULLET POINTS (List/Steps):
"Title '[Concept]' at top. Below: bullet list with 3-4 points using check-circle icons:
- Point 1 text
- Point 2 text  
- Point 3 text
Background: geometric shapes."

3. STATS/NUMBERS:
"Title '[Topic]' at top. Below: stat cards showing:
- Card 1: Number '[X]' with label '[Label]'
- Card 2: Number '[Y]' with label '[Label]'
Background: animated chart or gradient."

4. CONTENT (General):
"Title '[Concept]' in 3rem. Description paragraph: '[1-2 sentences]'. Optional bullet points if needed. Background: particles or gradient."

OUTPUT FORMAT (JSON):
[
  {{
    "index": 0,
    "text": "30-40 word narration here",
    "visual_hint": "Specific layout: Title 'X' in large text. Bullet points: A, B, C. Background: particles."
  }},
  ...
]

STRUCTURE:
- Segments 0-2: Introduction (title + overview)
- Segments 3-{middle_start}: Foundation (concepts with bullets)
- Segments {middle_start}-{middle_end}: Details (explanations with visuals)
- Segments {middle_end}-{conclusion_start}: Applications (examples, stats)
- Segments {conclusion_start}-{num_segments}: Conclusion (summary)

EXAMPLES:

Example 1 - Intro:
{{
  "index": 0,
  "text": "Welcome to this guide on artificial intelligence. Today we explore how AI is transforming industries from healthcare to transportation.",
  "visual_hint": "Main title 'ARTIFICIAL INTELLIGENCE' in 4rem bold white with gradient (white to cyan). Subtitle 'Transforming Industries' in 1.8rem light below. Background: 100 cyan particles (#00d4ff) moving randomly. Dark blue background (#0a0e27)."
}}

Example 2 - Bullets:
{{
  "index": 3,
  "text": "Machine learning has three core phases: data collection and preparation, model training and optimization, and finally deployment into real applications.",
  "visual_hint": "Title 'Machine Learning Phases' in 3rem bold. Below: bullet points with check-circle icons: '1. Data Collection & Preparation', '2. Model Training & Optimization', '3. Deployment & Monitoring'. Background: rotating hexagons in purple (#8b5cf6) with low opacity."
}}

Example 3 - Stats:
{{
  "index": 5,
  "text": "AI adoption has surged dramatically, with implementation rates jumping from twenty percent in 2020 to seventy-five percent in 2024.",
  "visual_hint": "Title 'AI Adoption Growth' in 3rem centered. Below: 3 stat cards side by side - Card 1: '20%' with '2020', Card 2: '75%' with '2024', Card 3: '275%' with 'Growth'. Numbers in cyan (#00d4ff), 3rem bold. Background: animated line graph showing upward trend."
}}

Example 4 - Content:
{{
  "index": 8,
  "text": "Neural networks consist of interconnected layers that process information, with each layer learning increasingly complex features from the data.",
  "visual_hint": "Title 'Neural Networks' in 3rem bold. Description: 'Layers of interconnected nodes processing information' in 1.2rem. Below: simple diagram showing 3 connected circles labeled 'Input → Hidden → Output'. Background: flowing particles connecting like neural pathways."
}}

Example 5 - Conclusion:
{{
  "index": 14,
  "text": "The future of AI holds limitless possibilities. Continue exploring this transformative technology and be part of shaping tomorrow's innovations.",
  "visual_hint": "Large text 'THE FUTURE IS HERE' in 4.5rem bold with gold gradient (#fbbf24 to white). Subtitle 'Continue Exploring' in 1.8rem light. Background: warm particles rising upward in gold/yellow colors, creating uplifting mood."
}}

CRITICAL:
- Return ONLY the JSON array
- NO markdown blocks (no ```json)
- NO explanations
- Start with [ end with ]
- Each text: exactly 30-40 words
- Each visual_hint: specific layout instructions (50-100 words)

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

Return valid JSON array:
- Each text: 30-40 words
- Each visual_hint: specific text/layout instructions (not abstract)
- NO markdown, NO extra text
- Start with [, end with ]
"""