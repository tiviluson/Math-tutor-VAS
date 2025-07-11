import os, subprocess, base64
import google.generativeai as genai
from .viz_prompts import (
    prompt_gen_asymptote,
    prompt_get_drawing_steps,
    prompt_get_geometry_reasoning,
)

GEMINI_MODEL = "gemini-2.0-flash"

# genai.configure(api_key=GOOGLE_API_KEY)
config = {
    "temperature": 0.0,
    "top_p": 0.5,
    "top_k": 40,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(GEMINI_MODEL, generation_config=config)


class VizSolver:
    def __init__(self, session_id, init_problem, student_drawing_steps):
        self.session_id = session_id
        self.init_problem = init_problem
        self.student_drawing_steps = student_drawing_steps

        self.keyobjects = None
        self.keyobjects_prompt = None

        self.asymptote_drawing_steps = None
        self.drawing_steps_prompt = None

        self.geometry_reasoning = None
        self.geometry_reasoning_prompt = None

        self.asymptote_code = None
        self.asymptote_code_prompt = None

        self.b64_string_viz = None

        self.code_err = None
        self.err = None

    def clean_asy(self, asy_code):
        return asy_code.removeprefix("```asy").removesuffix("```")

    def create_drawing_steps(self):
        self.drawing_steps_prompt = prompt_get_drawing_steps.format(
            # problem=self.init_problem,
            student_drawing_steps=self.student_drawing_steps
        )

        self.asymptote_drawing_steps = model.generate_content(
            self.drawing_steps_prompt
        ).text

    def get_geometry_reasoning(self):
        self.geometry_reasoning_prompt = prompt_get_geometry_reasoning.format(
            # problem=self.init_problem,
            student_drawing_steps=self.student_drawing_steps,
            asymptote_drawing_steps=self.asymptote_drawing_steps,
        )
        self.geometry_reasoning = model.generate_content(
            self.geometry_reasoning_prompt
        ).text

    def gen_asymptote_code(self):
        self.asymptote_code_prompt = prompt_gen_asymptote.format(
            # problem=self.init_problem,
            student_drawing_steps=self.student_drawing_steps,
            asymptote_drawing_steps=self.asymptote_drawing_steps,
            geometry_reasoning=self.geometry_reasoning,
        )
        self.asymptote_code = model.generate_content(self.asymptote_code_prompt).text

    def problem_to_viz_code(self):
        try:
            self.create_drawing_steps()
            self.get_geometry_reasoning()
            self.gen_asymptote_code()
        except Exception as e:
            print("Error generating Asymptote code:", e)
            self.err = str(e)

        if not self.asymptote_code:
            self.err = "Failed to generate Asymptote code."
            print(self.err)
            return
        else:
            self.exec_asymptote()
            print(self.asymptote_code)
            # pass

    def exec_asymptote(self):
        if not self.asymptote_code:
            print("No Asymptote code generated.")
            return

        code_asy = self.clean_asy(self.asymptote_code)

        with open("asymptote.asy", "w") as f:
            f.write(code_asy)

        # Run the Asymptote command to generate a JPG
        try:
            result = subprocess.run(
                ["asy", "-f", "jpg", "asymptote.asy"], capture_output=True, text=True
            )
            with open("asymptote.jpg", "rb") as img_file:
                self.b64_string_viz = base64.b64encode(img_file.read()).decode("utf-8")
        except Exception as e:
            self.code_err = str(e)
            print("Error running Asymptote command:", self.code_err)
            return

        # Convert the generated JPG to base64
        with open("asymptote.jpg", "rb") as img_file:
            self.b64_string_viz = base64.b64encode(img_file.read()).decode("utf-8")

        if result.returncode == 0:
            pass
        else:
            self.code_err = result.stderr
            print("Error:", result.stderr)
            return

        if os.path.exists("asymptote.asy"):
            # os.remove("asymptote.asy")
            pass
        # Delete the generated JPG after encoding
        if os.path.exists("asymptote.jpg"):
            # os.remove("asymptote.jpg")
            pass


# Function to API
def get_visualization(session_id, problem, student_drawing_steps):
    VizS = VizSolver(
        session_id=session_id,
        init_problem=problem,
        student_drawing_steps=student_drawing_steps,
    )

    # Asymptote Image Generation by LLM
    VizS.problem_to_viz_code()

    return VizS.b64_string_viz
