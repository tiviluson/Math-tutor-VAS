import google.generativeai as genai
GOOGLE_API_KEY=""
GEMINI_MODEL="gemini-2.0-flash"

genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
    "temperature": 0.0,
    "top_p": 0.5,
    "top_k": 40,
    "max_output_tokens": 2048,
}
model = genai.GenerativeModel(GEMINI_MODEL, generation_config=generation_config)

def clean_code(code_content):
    # Check if the first line starts with "```python", remove it if it does. Also, last line is "```"
    if code_content.startswith("```python"):
        code_content = code_content[10:]  # Remove the first line
    if code_content.endswith("```"):
        code_content = code_content[:-3]  # Remove the last line
    return code_content

def clean_asy(asy_code):
    # Check if the first line starts with "```asy", remove it if it does. Also, last line is "```"
    if asy_code.startswith("```asy"):
        asy_code = asy_code[7:]  # Remove the first line
    if asy_code.endswith("```"):
        asy_code = asy_code[:-3]  # Remove the last line
    return asy_code