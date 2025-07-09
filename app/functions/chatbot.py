from dash import html, dcc
import google.generativeai as genai
import dash_mantine_components as dmc

class LLMCall:
    def __init__(self, GEMINI_API_KEY, GEMINI_MODEL="gemini-1.5-flash"):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL

    def __call__(self, input_dict):
        prompt = input_dict.get("input", "")
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return {"output": response.text}

def generate_user_bubble(text):
    return dmc.Text(
        html.Span(["Student: ", html.Br(), dcc.Markdown(text)]),
        align="right",
        style={
            "backgroundColor": "#e6f7ff",
            "padding": "10px",
            "borderRadius": "15px 15px 0 15px",
            "margin": "5px",
            "maxWidth": "80%",
            "alignSelf": "flex-end",
            "wordBreak": "break-word"
        }
    )

def generate_ai_bubble(text):
    return dmc.Text(
        html.Span(["Tutor: ", html.Br(), dcc.Markdown(text)]),
        align="left",
        style={
            "backgroundColor": "#f0f0f0",
            "padding": "10px",
            "borderRadius": "15px 15px 15px 0",
            "margin": "5px",
            "maxWidth": "80%",
            "alignSelf": "flex-start",
            "wordBreak": "break-word"
        }
    )