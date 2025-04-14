import gradio as gr
import animation_gen
from summary import summarize_text
from mindmap import generate_mindmap, clean_mermaid_code, render_mermaid
from llm_loader import llm

# Modified Mindmap Pipeline that returns summary, status, and the image.
def run_mindmap_pipeline(doc_text):
    if not doc_text.strip():
        return "No document text available. Please enter text first.", "No mindmap generated.", None
    
    # Generate the summary using the summary function.
    summary = summarize_text(doc_text, llm)
    
    # Generate the Mermaid mindmap code via LLM.
    raw_mindmap_code = generate_mindmap(doc_text, llm)
    # Clean the code to remove markdown fences or extraneous formatting.
    cleaned_code = clean_mermaid_code(raw_mindmap_code)
    
    # Render the Mermaid code to an SVG file.
    try:
        svg_filepath = render_mermaid(cleaned_code)
        status = "Mindmap generated successfully."
    except Exception as e:
        status = f"Error generating mindmap: {str(e)}"
        svg_filepath = None

    return summary, status, svg_filepath

def run_animation_pipeline_wrapper(topic_text: str):
    logs = ""
    for message in animation_gen.generate_animation_pipeline(topic_text):
        logs += message + "\n"
        if "Final video available at:" in message:
            video_path = message.split("Final video available at:")[-1].strip()
            yield logs, video_path
        else:
            yield logs, None

with gr.Blocks() as demo:
    gr.Markdown("# EduVision – Concepts in Motion")
    
    # Common input text box
    input_text = gr.Textbox(
        label="Enter the document/topic text", 
        lines=10, 
        placeholder="Enter or paste text here"
    )
    
    with gr.Tabs():
        # ----- Mindmap Tab (with Summary) -----
        with gr.Tab("Mindmap"):
            gr.Markdown("### Mindmap and Summary Generation")
            mindmap_run_btn = gr.Button("Run Mindmap Pipeline")
            mindmap_summary = gr.Textbox(label="Summary", interactive=False, lines=5)
            mindmap_status = gr.Textbox(label="Mindmap Status", interactive=False)
            
            mindmap_image = gr.Image(
                label="Mindmap",
                interactive=False,
                height=700
            )
            mindmap_run_btn.click(
                fn=run_mindmap_pipeline, 
                inputs=input_text, 
                outputs=[mindmap_summary, mindmap_status, mindmap_image]
            )
        
        # ----- Animation Tab -----
        with gr.Tab("Animation"):
            gr.Markdown("### Animation Generation")
            animation_run_btn = gr.Button("Run Animation Pipeline")
            animation_log = gr.Textbox(label="Animation Log", interactive=False, lines=15)
            animation_video = gr.Video(label="Animation Video", visible=True)
            animation_run_btn.click(
                fn=run_animation_pipeline_wrapper, 
                inputs=input_text, 
                outputs=[animation_log, animation_video]
            )

demo.launch()
