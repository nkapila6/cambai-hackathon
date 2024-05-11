from helper import cambAI_TTS
import gradio as gr

app = gr.Interface(
    fn=cambAI_TTS,
    inputs=[
        gr.Textbox(label="Enter your sentence"),
        gr.Dropdown(choices=["en", "ar"], label="Language"),
    ],
    outputs=[
        gr.Audio(label="TTS Output from CAMB.AI"),
        gr.Textbox(label="Cleaned Output"),
    ],
)

app.launch()
