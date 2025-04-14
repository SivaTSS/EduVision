import subprocess
import os

def generate_mindmap(text, llm, max_tokens=500):
    """
    Generate a mind map in Mermaid syntax for the given text using ChatOpenAI.
    There should be exactly one central node (which is not generically labeled as 'root'),
    and all other topics are attached as subtopics of the central node.
    """
    prompt = (
        "Generate a mind map in Mermaid syntax for the following textbook text. "
        "Ensure that there is exactly one central (root) node, which is the only root, and attach all other topics "
        "as subtopics of this central node. Do NOT include a 'root' node with a generic label; instead, use a relevant central topic. "
        "Also, do NOT include any theme directives such as %%{init: {\"theme\": \"default\"}}%%, any parentheses, (, ) or any extraneous formatting. strictly no ( or )"
        "The mind map should be self-explanatory so that by reading it, a user can understand the key content of the text document."
        "Keep the Mermaid syntax minimal so it renders correctly.\n\n"
        f"{text}\n\n"
        "Mermaid Mind Map:"
    )
    result = llm.invoke(prompt, max_tokens=max_tokens)
    mindmap = result.content.strip()
    return mindmap

def clean_mermaid_code(code):
    """
    Remove markdown fences and theme directives from the Mermaid code.
    Ensures that the code is minimal so that it renders correctly.
    """
    lines = code.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        if "%%{init:" in line:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def render_mermaid(mindmap_code, output_filename='mermaid_output.svg', theme='neutral', background_color=None, css_file=None):
    """
    Render a Mermaid diagram as an SVG file using the Mermaid CLI (mmdc).
    
    The process is:
    1. Write the Mermaid code to a temporary file.
    2. Invoke the Mermaid CLI to produce an SVG.
    3. Delete the temporary file.
    
    Returns the path to the generated SVG file.
    """
    # Write the mindmap code to a temporary file.
    temp_file = "temp_mermaid.mmd"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(mindmap_code)
    
    # Build the Mermaid CLI command.
    cmd = ["mmdc", "-i", temp_file, "-o", output_filename, "-t", theme]
    
    if background_color:
        cmd.extend(["-b", background_color])
    
    if css_file:
        cmd.extend(["-c", css_file])
    
    subprocess.run(cmd, check=True)
    
    # Clean up the temporary file.
    os.remove(temp_file)
    
    return output_filename
