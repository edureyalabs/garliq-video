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
- Segments {conclusion_start}-{num_segments}: Conclusion with COMPREHENSIVE SUMMARY

CRITICAL CONCLUSION REQUIREMENTS (Last 2-3 segments):

The conclusion MUST be a proper summary that:
1. Explicitly recaps the main concepts covered in the video
2. Lists 3-5 key takeaways from the entire presentation
3. References specific topics discussed earlier in the video
4. Provides forward-looking perspective or call-to-action
5. Feels like a satisfying ending, not generic filler

DO NOT use generic conclusions like:
- "We've covered the essential concepts of [topic]"
- "Continue exploring to deepen your understanding"
- "Thank you for watching this educational video"

INSTEAD, use specific summaries like:
- "We explored how [specific concept A] works through [specific example], discovered that [specific finding B], and saw real applications in [specific field C]"
- "Remember these key points: [specific takeaway 1], [specific takeaway 2], [specific takeaway 3]"
- "From [opening concept] to [final concept], we've seen how this technology shapes [specific outcome]"

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

Example 5 - GOOD Conclusion (Specific Summary):
{{
  "index": 14,
  "text": "We've journeyed from understanding neural networks and machine learning phases to witnessing AI's real-world impact across healthcare, finance, and transportation sectors.",
  "visual_hint": "Title 'KEY TAKEAWAYS' in 3.5rem bold gold. Below: numbered summary list with star icons: '1. Neural networks learn through layers', '2. ML requires quality data & training', '3. AI adoption grew 275% since 2020', '4. Real applications in healthcare & finance'. Background: warm gold particles (#fbbf24) rising upward."
}}

Example 6 - GOOD Conclusion (Final Call-to-Action):
{{
  "index": 15,
  "text": "As AI continues evolving with breakthrough techniques like transformer models and reinforcement learning, your understanding of these fundamentals positions you at the forefront of innovation.",
  "visual_hint": "Large text 'THE FUTURE STARTS NOW' in 4.5rem bold with gradient (gold to white). Subtitle 'Keep Learning, Keep Growing' in 1.8rem. Background: dynamic particles forming upward arrow pattern, suggesting progress and growth."
}}

BAD Conclusion Example (Do NOT use):
{{
  "index": 14,
  "text": "We've covered the essential concepts of artificial intelligence. Continue exploring to deepen your understanding. Thank you for watching this educational video.",
  "visual_hint": "Generic conclusion scene"
}}

CRITICAL:
- Return ONLY the JSON array
- NO markdown blocks (no ```json)
- NO explanations
- Start with [ end with ]
- Each text: exactly 30-40 words
- Each visual_hint: specific layout instructions (50-100 words)
- Last 2-3 segments MUST contain specific summary of topics covered

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

MANDATORY CONCLUSION REQUIREMENTS:
The last 2-3 segments MUST provide a comprehensive summary that:
- Explicitly mentions specific concepts covered in the video
- Lists 3-5 concrete key takeaways
- References topics by name (not generic statements)
- Provides satisfying closure with forward-looking perspective

Return valid JSON array:
- Each text: 30-40 words
- Each visual_hint: specific text/layout instructions (not abstract)
- Conclusion segments: specific summaries with actual content recap
- NO markdown, NO extra text
- Start with [, end with ]
"""