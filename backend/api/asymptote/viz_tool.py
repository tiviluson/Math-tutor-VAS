import os, subprocess, base64
import google.generativeai as genai
from viz_prompts import (
    prompt_gen_asymptote,
    # prompt_get_key_objects,
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

        self.drawing_guides = None
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
            problem=self.init_problem,
            student_drawing_steps=self.student_drawing_steps)

        self.drawing_guides = model.generate_content(self.drawing_steps_prompt).text

    def get_geometry_reasoning(self):
        self.geometry_reasoning_prompt = prompt_get_geometry_reasoning.format(
            problem=self.init_problem,
            student_drawing_steps=self.drawing_guides,
            asymptote_drawing_steps=self.drawing_guides,
        )
        self.geometry_reasoning = model.generate_content(
            self.geometry_reasoning_prompt
        ).text

    def gen_asymptote_code(self):
        self.asymptote_code_prompt = prompt_gen_asymptote.format(
            problem=self.init_problem,
            student_drawing_steps=self.drawing_guides,
            asymptote_drawing_steps=self.drawing_guides,
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

    return {
        "session_id": VizS.session_id,
        "keyobjects": VizS.keyobjects,
        "drawing_guides": VizS.drawing_guides,
        "geometry_reasoning": VizS.geometry_reasoning,
        "keyobjects_prompt": VizS.keyobjects_prompt,
        "drawing_steps_prompt": VizS.drawing_steps_prompt,
        "geometry_reasoning_prompt": VizS.geometry_reasoning_prompt,
        "asymptote_code_prompt": VizS.asymptote_code_prompt,
        "asymptote_code": VizS.asymptote_code,
        "b64_string_viz": VizS.b64_string_viz,
        "asym_err": VizS.code_err,
        "llm_err": VizS.err,
    }


if __name__ == "__main__":
    # Example usage
    session_id = "123"
    problem = """Từ một điểm A nằm ngoài đường tròn (O;R) với OA = 2R, kẻ hai tiếp tuyến\nAB, AC đến đường tròn (B,C là các tiếp điểm). Vẽ đường kính BD của đường tròn (O). Gọi E\nlà giao điểm thứ hai của đường thẳng AD với (O). Đường thẳng BC và AO cắt nhau tại H.\n\na) Chứng minh rằng tam giác BED vuông và ABHE là tứ giác nội tiếp."""
    student_drawing_steps = {"illustration_steps": [
        "Vẽ đường tròn tâm O bán kính R.",
        "Vẽ điểm A nằm ngoài đường tròn sao cho OA = 2R.",
        "Vẽ hai tiếp tuyến AB và AC đến đường tròn (O) với B và C là các tiếp điểm.",
        "Vẽ đường kính BD của đường tròn (O).",
        "Vẽ đường thẳng AD cắt đường tròn (O) tại E (E khác D).",
        "Vẽ đường thẳng BC cắt AO tại H.",
        "Nối các điểm B, E, D để tạo thành tam giác BED.",
        "Nối các điểm A, B, H, E để tạo thành tứ giác ABHE.",
        "Nối các điểm D, H, E để tạo thành tam giác DHE."
    ]}

    result = get_visualization(session_id, problem, student_drawing_steps)
    # print(result)
