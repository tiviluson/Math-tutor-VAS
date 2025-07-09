prompt_gen_asymptote = """
        You are a master of Asymptote: The Vector Graphics Language, who creates visualizations to solve the given geometry problem. 
        The below is a geometry problem, and its solution. Use your expertise to generate an Asymptote code that visualizes the solution.
        Requirements:
            - The output should be a valid Asymptote code that can be rendered to visualize the problem and solution.
            - Do not include any redundant text, just the Asymptote code.
            - Use the `geometry_reasoning` to identify the key points, lines, and other geometric elements that need to be visualized.
            - Utilize the `drawing_steps` to accurately depict the geometric construction.
            - If the problem can be drawn by Asymptote functions without actual coordinates, just use the Asymptote functions to draw the geometric construction.
            - Start the answer with: import olympiad; import settings; size(600, 600);

        Example:
        Key Objects:
        {{
        "key_objects": [
            {{
            "object": "A",
            "description": "coordinates of point A in the triangle ABC"
            }},
            {{
            "object": "B",
            "description": "coordinates of point B in the triangle ABC"
            }},
            {{
            "object": "C",
            "description": "coordinates of point C in the triangle ABC"
            }},
            {{
            "object": "line AB",
            "description": "line segment connecting points A and B"
            }},
            {{
            "object": "line BC",
            "description": "line segment connecting points B and C"
            }},
            {{
            "object": "line AC",
            "description": "line segment connecting points A and C"
            }},
            {{
            "object": "triangle ABC",
            "description": "isosceles triangle, AB = CB, angle ABC = 36 degrees"
            }},
            {{
            "object": "angle ABC",
            "description": "36 degrees"
            }},
            {{
            "object": "angle BAC",
            "description": "72 degrees"
            }},
            {{
            "object": "angle BCA",
            "description": "72 degrees"
            }},
            {{
            "object": "O",
            "description": "coordinates of point O, the center of the circumcircle of triangle ABC"
            }},
            {{
            "object": "line OA",
            "description": "line segment connecting point O and point A"
            }},
            {{
            "object": "line OB",
            "description": "line segment connecting point O and point B"
            }},
            {{
            "object": "line OC",
            "description": "line segment connecting point O and point C"
            }},
            {{
            "object": "angle BOC",
            "description": "144 degrees, angle at the center O subtended by arc BC"
            }},
            {{
            "object": "OA = OB = OC",
            "description": "radii of the circumcircle, all equal in length"
            }}
        ]
        }}

        Geometry Reasoning:
        {{
        "geometry_reasoning": [
            {{
            "object": "Point B",
            "description": "The starting point of drawing triangle ABC, (0, 0)."
            }},
            {{
            "object": "Point A",
            "description": "The second point of the triangle ABC, such that the length of AB is not fixed."
            }},
            {{
            "object": "Point C",
            "description": "The third point of the triangle ABC, depends on points A and B to ensure that BC = AB and angle ABC = 36 degrees."
            }},
            {{
            "object": "Triangle ABC",
            "description": "is a isosceles triangle at B, defined by points A, B, and C, with AB = CB and angle ABC = 36 degrees."
            }},
            {{
            "object": "Circumcircle of triangle ABC",
            "description": "The circle goes through points A, B, and C."
            }},
            {{
            "object": "Point O",
            "description": "Center of the circumcircle of triangle ABC, depends on the circumcircle."
            }},
            {{
            "object": "Line segment OB",
            "description": "Defined by points O and B, depends on points O and B."
            }},
            {{
            "object": "Line segment OC",
            "description": "Defined by points O and C, depends on points O and C."
            }},
            {{
            "object": "Line segment OA",
            "description": "Defined by points O and A, depends on points O and A."
            }},
            {{
            "object": "Angle BOC",
            "description": "The angle at point O between lines OB and OC, which is 144 degrees."
            }},
            {{
            "object": "Angle ABC",
            "description": "The angle at point B between lines AB and BC, which is 36 degrees."
            }},
            {{
            "object": "Angle BAC",
            "description": "The angle at point A between lines AB and AC, which is 72 degrees."
            }},
            {{
            "object": "Angle BCA",
            "description": "The angle at point C between lines BC and AC, which is 72 degrees."
            }}
        ]
        }}

        Drawing Steps:
        {{
        "drawing_steps": [
            "Step 1": "Define point B at coordinate (0,0).",
            "Step 2": "Define point A such that the length of segment AB is a chosen value. A is independent of B.",
            "Step 3": "Define point C such that BC = AB and angle ABC = 36 degrees. C is dependent on A and B.",
            "Step 4": "Construct the circumcircle of triangle ABC.",
            "Step 5": "Locate the center O of the circumcircle.",
            "Step 6": "Draw line segment OB in dashed style.",
            "Step 7": "Draw line segment OC in dashed style.",
            "Step 7": "Draw line segment OA in dashed style.",
            "Step 8": "Label "point A, B, C, O with their coordinates.",
            "Step 9": "Label angles ABC at the point B between line AB and line BC, value 36 degrees",
            "Step 10": "Label angle BAC at the point A between line AB and line AC, value 72 degrees",
            "Step 11": "Label angle BCA at the point C between line BC and line AC, value 72 degrees",
            "Step 12": "Label angle BOC at the point O between line OB and line OC, value 144 degrees",
        ]
        }}

        Return:
        import olympiad; import settings; size(600, 600);
        pair B = (0,0);
        pair A = (1,0);
        pair C = rotate(36)*(A);
        path circ = circumcircle(A,B,C);
        pair O = circumcenter(A,B,C);

        draw(A--B--C--cycle);
        draw(circ);
        draw(O--B, dashed);
        draw(O--C, dashed);
        draw(O--A, dashed);

        label("$A$",A,SE);
        label("$B$",B,SW);
        label("$C$",C,N);
        label("$O$",O,S);
        label("$36^\circ$",B, E);
        label("$72^\circ$",A, NW);
        label("$72^\circ$",C, S);
        label("$144^\circ$",O, NW);

        Key Objects: {key_objects}
        Geometry_Reasoning: {geometry_reasoning}
        Drawing_Steps: {drawing_steps}
        Return:
        """

prompt_get_key_objects = """
    You are an expert in geometry problem solving. Given the following geometry problem and its solution,
    identify and extract the key objects, objects that are essential for understanding and solving the problem.
    Requirements:
    - The output should be all the key geometric components mentioned in the problem and solution, each described in a clear and concise manner.
    - Return answer in JSON format instead of human language, showing the programming logically.
    - Just focus on the key objects and return only key objects.
    - No markdown marks at return.

    Example:
    Problem: In the triangle ABC, sides AB and CB have equal lengths and the measure of angle $angle ABC$ is equal to 36 degrees. What is the measure of angle $angle BOC$ where O is the center of the circle goes through A, B, and C?
    Solution: 
    **Bài toán:** Tính số đo góc BOC.
    **Lời giải:**
    **Bước 1: Xác định các góc trong tam giác ABC**
    *   **Lý luận:** Tam giác ABC là tam giác cân tại B vì AB = CB (theo giả thiết). Trong một tam giác cân, hai góc ở đáy bằng nhau. Do đó, góc BAC bằng góc BCA. Tổng các góc trong một tam giác là 180 độ. Ta có thể sử dụng thông tin này để tìm góc BAC và BCA.
    *   **Tính toán:**
        *   Góc ABC = 36 độ (theo giả thiết).
        *   Tổng góc BAC và góc BCA là: 180 độ - 36 độ = 144 độ.
        *   Vì góc BAC = góc BCA, nên góc BAC = góc BCA = 144 độ / 2 = 72 độ.
    *   **Kết luận:** Góc BAC = Góc BCA = 72 độ.
    **Bước 2: Tính số đo góc BOC**
    *   **Lý luận:** Vì O là tâm đường tròn đi qua A, B, và C, nên OA = OB = OC (đều là bán kính của đường tròn). Góc BOC là góc ở tâm chắn cung BC. Góc BAC là góc nội tiếp chắn cung BC. Theo định lý góc ở tâm, góc ở tâm bằng hai lần góc nội tiếp cùng chắn một cung. Do đó, góc BOC = 2 * góc BAC.
    *   **Tính toán:**
        *   Góc BAC = 72 độ (đã tính ở bước 1).
        *   Góc BOC = 2 * 72 độ = 144 độ.
    *   **Kết luận:** Góc BOC = 144 độ.
    **Kết luận cuối cùng:** Số đo góc BOC là 144 độ.

    Return:
    {{
    "key_objects": [
        {{
        "object": "A",
        "description": "coordinates of point A in the triangle ABC"
        }},
        {{
        "object": "B",
        "description": "coordinates of point B in the triangle ABC"
        }},
        {{
        "object": "C",
        "description": "coordinates of point C in the triangle ABC"
        }},
        {{
        "object": "line AB",
        "description": "line segment connecting points A and B"
        }},
        {{
        "object": "line BC",
        "description": "line segment connecting points B and C"
        }},
        {{
        "object": "line AC",
        "description": "line segment connecting points A and C"
        }},
        {{
        "object": "triangle ABC",
        "description": "isosceles triangle, AB = CB, angle ABC = 36 degrees"
        }},
        {{
        "object": "angle ABC",
        "description": "36 degrees"
        }},
        {{
        "object": "angle BAC",
        "description": "72 degrees"
        }},
        {{
        "object": "angle BCA",
        "description": "72 degrees"
        }},
        {{
        "object": "O",
        "description": "coordinates of point O, the center of the circumcircle of triangle ABC"
        }},
        {{
        "object": "line OA",
        "description": "line segment connecting point O and point A"
        }},
        {{
        "object": "line OB",
        "description": "line segment connecting point O and point B"
        }},
        {{
        "object": "line OC",
        "description": "line segment connecting point O and point C"
        }},
        {{
        "object": "angle BOC",
        "description": "144 degrees, angle at the center O subtended by arc BC"
        }},
        {{
        "object": "OA = OB = OC",
        "description": "radii of the circumcircle, all equal in length"
        }}
    ]
    }}

    Problem: {init_problem}
    Solution: {tutor_solution}
    Return:
"""

prompt_get_drawing_steps = """
    You are an expert in geometry problem solving. Given the following geometry's solution, key points,
    create a series of steps to draw the geometric construction described in the solution.
    Requirements:
    - The output includes steps, each describing a specific action to take in order to recreate the construction.
    - Each step should be clear and concise, focusing on the geometric construction.
    - Return answer in JSON format instead of human language, showing the programming logically.
    - No markdown marks or redundant text.

    Example:
    Problem: In the triangle ABC, sides AB and CB have equal lengths and the measure of angle $angle ABC$ is equal to 36 degrees. What is the measure of angle $angle BOC$ where O is the center of the circle goes through A, B, and C?
    Solution: 
    **Bài toán:** Tính số đo góc BOC.
    **Lời giải:**
    **Bước 1: Xác định các góc trong tam giác ABC**
    *   **Lý luận:** Tam giác ABC là tam giác cân tại B vì AB = CB (theo giả thiết). Trong một tam giác cân, hai góc ở đáy bằng nhau. Do đó, góc BAC bằng góc BCA. Tổng các góc trong một tam giác là 180 độ. Ta có thể sử dụng thông tin này để tìm góc BAC và BCA.
    *   **Tính toán:**
        *   Góc ABC = 36 độ (theo giả thiết).
        *   Tổng góc BAC và góc BCA là: 180 độ - 36 độ = 144 độ.
        *   Vì góc BAC = góc BCA, nên góc BAC = góc BCA = 144 độ / 2 = 72 độ.
    *   **Kết luận:** Góc BAC = Góc BCA = 72 độ.
    **Bước 2: Tính số đo góc BOC**
    *   **Lý luận:** Vì O là tâm đường tròn đi qua A, B, và C, nên OA = OB = OC (đều là bán kính của đường tròn). Góc BOC là góc ở tâm chắn cung BC. Góc BAC là góc nội tiếp chắn cung BC. Theo định lý góc ở tâm, góc ở tâm bằng hai lần góc nội tiếp cùng chắn một cung. Do đó, góc BOC = 2 * góc BAC.
    *   **Tính toán:**
        *   Góc BAC = 72 độ (đã tính ở bước 1).
        *   Góc BOC = 2 * 72 độ = 144 độ.
    *   **Kết luận:** Góc BOC = 144 độ.
    **Kết luận cuối cùng:** Số đo góc BOC là 144 độ.

    Key Objects:
    {{
    "key_objects": [
        {{
        "object": "A",
        "description": "coordinates of point A in the triangle ABC"
        }},
        {{
        "object": "B",
        "description": "coordinates of point B in the triangle ABC"
        }},
        {{
        "object": "C",
        "description": "coordinates of point C in the triangle ABC"
        }},
        {{
        "object": "line AB",
        "description": "line segment connecting points A and B"
        }},
        {{
        "object": "line BC",
        "description": "line segment connecting points B and C"
        }},
        {{
        "object": "line AC",
        "description": "line segment connecting points A and C"
        }},
        {{
        "object": "triangle ABC",
        "description": "isosceles triangle, AB = CB, angle ABC = 36 degrees"
        }},
        {{
        "object": "angle ABC",
        "description": "36 degrees"
        }},
        {{
        "object": "angle BAC",
        "description": "72 degrees"
        }},
        {{
        "object": "angle BCA",
        "description": "72 degrees"
        }},
        {{
        "object": "O",
        "description": "coordinates of point O, the center of the circumcircle of triangle ABC"
        }},
        {{
        "object": "line OA",
        "description": "line segment connecting point O and point A"
        }},
        {{
        "object": "line OB",
        "description": "line segment connecting point O and point B"
        }},
        {{
        "object": "line OC",
        "description": "line segment connecting point O and point C"
        }},
        {{
        "object": "angle BOC",
        "description": "144 degrees, angle at the center O subtended by arc BC"
        }},
        {{
        "object": "OA = OB = OC",
        "description": "radii of the circumcircle, all equal in length"
        }}
    ]
    }}

    Return:
    {{
    "drawing_steps": [
        "Step 1": "Define point B at coordinate (0,0).",
        "Step 2": "Define point A such that the length of segment AB is a chosen value. A is independent of B.",
        "Step 3": "Define point C such that BC = AB and angle ABC = 36 degrees. C is dependent on A and B.",
        "Step 4": "Construct the circumcircle of triangle ABC.",
        "Step 5": "Locate the center O of the circumcircle.",
        "Step 6": "Draw line segment OB in dashed style.",
        "Step 7": "Draw line segment OC in dashed style.",
        "Step 7": "Draw line segment OA in dashed style.",
        "Step 8": "Label "point A, B, C, O with their coordinates.",
        "Step 9": "Label angles ABC at the point B between line AB and line BC, value 36 degrees",
        "Step 10": "Label angle BAC at the point A between line AB and line AC, value 72 degrees",
        "Step 11": "Label angle BCA at the point C between line BC and line AC, value 72 degrees",
        "Step 12": "Label angle BOC at the point O between line OB and line OC, value 144 degrees",
    ]
    }}

    Problem: {init_problem}
    Solution: {tutor_solution}
    Key Objects: {key_objects}
    Return:
    """

prompt_get_geometry_reasoning = """
    You are an expert in geometry problem solving. Given the following geometry problem and its solution.
    From a mathematical perspective, answer what are the objects whose coordinates can be randomly generated in the solution.
    And what are the objects that depend on the others when drawing the geometric construction.
    With the random objects, always generate coordinates for the points in the solution.
    With the dependency objects, dont give any coordinates, just describe them and its relationship with the random objects.
    Requirements:
    - Just focus on the objects and return only objects.
    - The output should be a list of objects, each described in a clear and concise manner.
    - Return answer in JSON format instead of human language, showing the programming logically.
    - No markdown marks or redundant text.

    Example:
    Problem: In the triangle ABC, sides AB and CB have equal lengths and the measure of angle $angle ABC$ is equal to 36 degrees. What is the measure of angle $angle BOC$ where O is the center of the circle goes through A, B, and C?
    Solution:
    **Bài toán:** Tính số đo góc BOC.
    **Lời giải:**
    **Bước 1: Xác định các góc trong tam giác ABC**
    *   **Lý luận:** Tam giác ABC là tam giác cân tại B vì AB = CB (theo giả thiết). Trong một tam giác cân, hai góc ở đáy bằng nhau. Do đó, góc BAC bằng góc BCA. Tổng các góc trong một tam giác là 180 độ. Ta có thể sử dụng thông tin này để tìm góc BAC và BCA.
    *   **Tính toán:**
        *   Góc ABC = 36 độ (theo giả thiết).
        *   Tổng góc BAC và góc BCA là: 180 độ - 36 độ = 144 độ.
        *   Vì góc BAC = góc BCA, nên góc BAC = góc BCA = 144 độ / 2 = 72 độ.
    *   **Kết luận:** Góc BAC = Góc BCA = 72 độ.
    **Bước 2: Tính số đo góc BOC**
    *   **Lý luận:** Vì O là tâm đường tròn đi qua A, B, và C, nên OA = OB = OC (đều là bán kính của đường tròn). Góc BOC là góc ở tâm chắn cung BC. Góc BAC là góc nội tiếp chắn cung BC. Theo định lý góc ở tâm, góc ở tâm bằng hai lần góc nội tiếp cùng chắn một cung. Do đó, góc BOC = 2 * góc BAC.
    *   **Tính toán:**
        *   Góc BAC = 72 độ (đã tính ở bước 1).
        *   Góc BOC = 2 * 72 độ = 144 độ.
    *   **Kết luận:** Góc BOC = 144 độ.
    **Kết luận cuối cùng:** Số đo góc BOC là 144 độ.

    Key Objects:
    {{
    "key_objects": [
        {{
        "object": "A",
        "description": "coordinates of point A in the triangle ABC"
        }},
        {{
        "object": "B",
        "description": "coordinates of point B in the triangle ABC"
        }},
        {{
        "object": "C",
        "description": "coordinates of point C in the triangle ABC"
        }},
        {{
        "object": "line AB",
        "description": "line segment connecting points A and B"
        }},
        {{
        "object": "line BC",
        "description": "line segment connecting points B and C"
        }},
        {{
        "object": "line AC",
        "description": "line segment connecting points A and C"
        }},
        {{
        "object": "triangle ABC",
        "description": "isosceles triangle, AB = CB, angle ABC = 36 degrees"
        }},
        {{
        "object": "angle ABC",
        "description": "36 degrees"
        }},
        {{
        "object": "angle BAC",
        "description": "72 degrees"
        }},
        {{
        "object": "angle BCA",
        "description": "72 degrees"
        }},
        {{
        "object": "O",
        "description": "coordinates of point O, the center of the circumcircle of triangle ABC"
        }},
        {{
        "object": "line OA",
        "description": "line segment connecting point O and point A"
        }},
        {{
        "object": "line OB",
        "description": "line segment connecting point O and point B"
        }},
        {{
        "object": "line OC",
        "description": "line segment connecting point O and point C"
        }},
        {{
        "object": "angle BOC",
        "description": "144 degrees, angle at the center O subtended by arc BC"
        }},
        {{
        "object": "OA = OB = OC",
        "description": "radii of the circumcircle, all equal in length"
        }}
    ]
    }}


    Drawing Steps:
    {{
    "drawing_steps": [
        "Step 1": "Define point B at coordinate (0,0).",
        "Step 2": "Define point A such that the length of segment AB is a chosen value. A is independent of B.",
        "Step 3": "Define point C such that BC = AB and angle ABC = 36 degrees. C is dependent on A and B.",
        "Step 4": "Construct the circumcircle of triangle ABC.",
        "Step 5": "Locate the center O of the circumcircle.",
        "Step 6": "Draw line segment OB in dashed style.",
        "Step 7": "Draw line segment OC in dashed style.",
        "Step 7": "Draw line segment OA in dashed style.",
        "Step 8": "Label "point A, B, C, O with their coordinates.",
        "Step 9": "Label angles ABC at the point B between line AB and line BC, value 36 degrees",
        "Step 10": "Label angle BAC at the point A between line AB and line AC, value 72 degrees",
        "Step 11": "Label angle BCA at the point C between line BC and line AC, value 72 degrees",
        "Step 12": "Label angle BOC at the point O between line OB and line OC, value 144 degrees",
    ]
    }}

    Return:
    {{
    "geometry_reasoning": [
        {{
        "object": "Point B",
        "description": "The starting point of drawing triangle ABC, (0, 0)."
        }},
        {{
        "object": "Point A",
        "description": "The second point of the triangle ABC, such that the length of AB is not fixed."
        }},
        {{
        "object": "Point C",
        "description": "The third point of the triangle ABC, depends on points A and B to ensure that BC = AB and angle ABC = 36 degrees."
        }},
        {{
        "object": "Triangle ABC",
        "description": "is a isosceles triangle at B, defined by points A, B, and C, with AB = CB and angle ABC = 36 degrees."
        }},
        {{
        "object": "Circumcircle of triangle ABC",
        "description": "The circle goes through points A, B, and C."
        }},
        {{
        "object": "Point O",
        "description": "Center of the circumcircle of triangle ABC, depends on the circumcircle."
        }},
        {{
        "object": "Line segment OB",
        "description": "Defined by points O and B, depends on points O and B."
        }},
        {{
        "object": "Line segment OC",
        "description": "Defined by points O and C, depends on points O and C."
        }},
        {{
        "object": "Line segment OA",
        "description": "Defined by points O and A, depends on points O and A."
        }},
        {{
        "object": "Angle BOC",
        "description": "The angle at point O between lines OB and OC, which is 144 degrees."
        }},
        {{
        "object": "Angle ABC",
        "description": "The angle at point B between lines AB and BC, which is 36 degrees."
        }},
        {{
        "object": "Angle BAC",
        "description": "The angle at point A between lines AB and AC, which is 72 degrees."
        }},
        {{
        "object": "Angle BCA",
        "description": "The angle at point C between lines BC and AC, which is 72 degrees."
        }}
    ]
    }}

    Problem: {init_problem}
    Solution: {tutor_solution}
    Key Objects: {key_objects}
    Drawing Steps: {drawing_steps}
    Return:
"""