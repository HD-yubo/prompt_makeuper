"""
Format instruction generator for different output types.

This module provides format-specific instructions that are injected
into the LLM's system prompt to control the output structure.
"""


def get_format_instructions(output_type: str) -> str:
    """
    Get format-specific instructions for LLM output.

    Args:
        output_type: The desired output format ('markdown' or 'xml')

    Returns:
        Format instruction string to append to system prompt
    """
    if output_type == "xml":
        return """
**OUTPUT FORMAT REQUIREMENT - XML:**
You MUST output the optimized prompt as valid XML with the following structure:

```xml
<prompt>
  <system_role>[Define the AI's role and expertise]</system_role>
  <goal>[Clearly state the objective]</goal>
  <instructions>
    <item>[Step 1]</item>
    <item>[Step 2]</item>
    <item>[Step 3]</item>
  </instructions>
  <context>[Relevant background information and constraints]</context>
  <examples>
    <good>[Positive example]</good>
    <bad>[What to avoid]</bad>
  </examples>
  <constraints>[Specific limitations and requirements]</constraints>
  <output_format>[Expected structure and format of the output]</output_format>
</prompt>
```

CRITICAL XML REQUIREMENTS:
- Output ONLY the XML, nothing else
- Use CDATA sections if content contains special characters
- Properly escape XML special characters: < > & " '
- Use <item> tags for list items within <instructions>
- Maintain hierarchical structure with proper nesting
- DO NOT include markdown code blocks (```xml) - output raw XML only
"""
    else:  # markdown (default)
        return """
**OUTPUT FORMAT REQUIREMENT - MARKDOWN:**
You MUST output the optimized prompt as valid Markdown with:
- ## Headers for main sections
- ### Headers for subsections
- Bullet points for lists
- **Bold** for emphasis
- Clear visual hierarchy

Output ONLY the markdown, nothing else.
"""
