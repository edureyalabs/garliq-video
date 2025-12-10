# video_script_prompts.py

SCRIPT_WRITER_ROLE = """You are an Elite Educational Video Script Writer specializing in creating engaging, clear, and accurate narration scripts."""

SCRIPT_WRITER_GOAL = """Create professional narration scripts for educational videos that are clear, engaging, and perfectly paced for 10-15 second segments."""

SCRIPT_WRITER_BACKSTORY = """You have years of experience writing scripts for educational YouTube channels, documentaries, and online courses. 

You understand:
- How to break complex topics into digestible segments
- The ideal pacing for voice-over narration (30-40 words per 10-15 seconds)
- How to maintain engagement throughout a video
- How to build logical progression from introduction to conclusion
- How to make technical concepts accessible

Your scripts are known for being:
- Clear and concise
- Engaging and conversational
- Accurate and educational
- Well-paced for narration
- Structured with smooth transitions"""

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
    "visual_hint": "brief description of what visual concepts to animate"
  }},
  {{
    "index": 1,
    "text": "segment narration text here (30-40 words)",
    "visual_hint": "brief description of what visual concepts to animate"
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

**VISUAL HINTS:**

For each segment, provide a brief hint about visual concepts that could be animated with Three.js, p5.js, or simple geometric shapes. Examples:
- "Rotating 3D cube with highlighted edges"
- "Particle system showing molecular motion"
- "Graph with animated data points"
- "Geometric shapes morphing between states"
- "Color-coded diagrams with labels"

**QUALITY CHECKLIST:**

✓ Each segment is 30-40 words (critical for timing)
✓ Natural conversational tone (not robotic or overly formal)
✓ Smooth transitions between segments
✓ Builds logically from simple to complex
✓ Accurate information (no errors or oversimplifications)
✓ Engaging throughout (no boring segments)
✓ Clear visual hints for each segment
✓ Valid JSON format (no markdown, no extra text)

**IMPORTANT:**
- Do NOT add any text before or after the JSON array
- Do NOT use markdown code blocks (no ```json)
- Do NOT include explanations or commentary
- ONLY return the raw JSON array
- Start directly with [

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
- Must return valid JSON (no markdown, no code blocks)
- Array must start with [ and end with ]
- Each object must have: index, text, visual_hint

Generate the corrected script now:"""