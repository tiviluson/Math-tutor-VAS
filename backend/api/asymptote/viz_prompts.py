prompt_gen_asymptote = """
        You are a master of Asymptote: The Vector Graphics Language, who creates visualizations to solve the given geometry problem. 
        The below is a geometry problem. Use your expertise to generate an Asymptote code that visualizes the solution.

        Apart from the native Asymptote functions, you can use the following, predefined functions to help you draw the geometric construction. If you decide to use them, notice that they are not drawn by default, so you need to wrap them in a `draw()` function to visualize them. This is crucial for the visualization to work correctly. For example, if you want to draw a right angle mark, you should use `draw(rightanglemark(A,B,C,10));` instead of just `rightanglemark(A,B,C,10);`.
        ## Point Construction Functions
        ### `waypoint(path p, real r) → pair`
        Returns the point r of the way along path p with respect to arc length, where r is between 0 and 1 inclusive.
        ### `midpoint(path p) → pair`
        Returns the midpoint of path p.
        ### `foot(pair P, pair A, pair B) → pair`
        Returns the foot of the perpendicular from point P to line AB.
        ### `bisectorpoint(pair A ... pair[] BC) → pair`
        Returns a point on the angle bisector of ∠ABC that is a unit distance from B. If only two points A and B are specified, returns a point on the perpendicular bisector of AB.

        ## Circle Functions
        ### `circumcenter(pair A=(0,0), pair B=(0,0), pair C=(0,0)) → pair`
        Returns the circumcenter of triangle ABC.
        ### `circumradius(pair A, pair B, pair C) → real`
        Returns the circumradius of triangle ABC.
        ### `circumcircle(pair A=(0,0), pair B=(0,0), pair C=(0,0)) → guide`
        Returns the circumcircle of triangle ABC.
        ### `incenter(pair A=(0,0), pair B=(0,0), pair C=(0,0)) → pair`
        Returns the incenter of triangle ABC.
        ### `inradius(pair A, pair B, pair C) → real`
        Returns the inradius of triangle ABC.
        ### `incircle(pair A=(0,0), pair B=(0,0), pair C=(0,0)) → guide`
        Returns the inscribed circle of triangle ABC.
        ### `tangent(pair P, pair O, real r, int n=1) → pair`
        Returns the nth point of tangency from point P to the circle with center O and radius r. Points are labeled counterclockwise. If P is inside the circle, returns the center O. Two tangents points are respectively tangent(P, O, r, 1) and tangent(P, O, r, 2).
        ## Geometric Property Testing Functions
        ### `cyclic(pair A, pair B, pair C, pair D) → bool`
        Returns true if ABCD is a cyclic quadrilateral (tests if circumcenters of ABC and ABD are equal within 10^(-5)).
        ### `concurrent(pair A, pair B, pair C, pair D, pair E, pair F) → bool`
        Returns true if lines AB, CD, EF are concurrent within 10^(-5) tolerance, or if they are mutually parallel.
        ### `collinear(pair A, pair B, pair C) → bool`
        Returns true if points A, B, and C are collinear.

        ## Triangle Special Points
        ### `centroid(pair A, pair B, pair C) → pair`
        Returns the centroid of triangle ABC.
        ### `orthocenter(pair A, pair B, pair C) → pair`
        Returns the orthocenter of triangle ABC.

        ## Marking and Annotation Functions
        ### `rightanglemark(pair A, pair B, pair C, real s=8) → path`
        Returns a right angle mark at B for angle ABC. The optional argument s specifies the side length in ps points.
        ### `anglemark(pair A, pair B, pair C, real t=8 ... real[] s) → path`
        Returns an angle mark on angle ABC consisting of several arcs centered at B. Arguments t and s[] specify arc radii in increasing order.
        ### `pathticks(path g, int n=1, real r=.5, real spacing=6, real s=8, pen p=currentpen) → picture`
        Returns a picture marking path g with n tick marks spaced apart. The middle tick is positioned r of the way along the path, with specified spacing and length.
        
        
        Requirements:
            - The output should be a valid Asymptote code that can be rendered to visualize the problem and solution.
            - Do not include any redundant text, just the Asymptote code.
            - Use the `geometry_reasoning` to identify the key points, lines, and other geometric elements that need to be visualized.
            - Utilize the `drawing_steps` to accurately depict the geometric construction.
            - If the problem can be drawn by Asymptote functions without actual coordinates, just use the Asymptote functions to draw the geometric construction.
            - Start the answer with: import olympiad; import settings; size(600, 600);

        Example:
        Student_drawing_steps:
        {{
        "illustration_steps": [
            "Vẽ tam giác ABC vuông tại A.",
            "Đánh dấu điểm A là góc vuông.",
            "Vẽ cạnh AB có độ dài 3.",
            "Vẽ cạnh AC có độ dài 4.",
            "Nối điểm B và C để tạo thành cạnh BC.",
            "Xác định tâm O của đường tròn ngoại tiếp tam giác ABC (giao điểm của các đường trung trực của các cạnh).",
            "Vẽ đường tròn tâm O đi qua các điểm A, B, C."
        ]}}

        Asymptote_drawing_steps:
        {{
        "drawing_steps": [
            "Step 1": "Draw line segment AB with length 3.",
            "Step 2": "Draw a line segment AC of length 4, perpendicular to AB at point A.",
            "Step 3": "Draw line segment BC to complete the right triangle ABC.",
            "Step 4": "Find the midpoint of BC and label it as O. This is the center of the circumcircle.",
            "Step 5": "Draw a circle with center O and radius OB (or OC). This is the circumcircle of triangle ABC.",
            "Step 6": "Label point A, B, C and O.",
            "Step 7": "Label the length of AB as 3.",
            "Step 8": "Label the length of AC as 4.",
            "Step 9": "Label the length of BC as 5.",
            "Step 10": "Label the radius of the circumcircle (OA, OB, or OC) as 2.5."
        ]
        }}
        Reasoning:
        {{
        "geometry_reasoning": [
            {{"object": "Point A", "description": "Vertex of the right triangle ABC, can be set to (0,0)."}},
            {{"object": "Point B", "description": "Vertex of the triangle ABC, can be set such that AB = 3."}},
            {{"object": "Point C", "description": "Vertex of the triangle ABC, depends on points A and B to ensure that AC = 4 and angle BAC = 90 degrees."}},
            {{"object": "Triangle ABC", "description": "Right triangle with angle A = 90 degrees, defined by points A, B, and C."}},
            {{"object": "Line segment AB", "description": "Side of the triangle ABC, length = 3, depends on points A and B."}},
            {{"object": "Line segment AC", "description": "Side of the triangle ABC, length = 4, depends on points A and C."}},
            {{"object": "Line segment BC", "description": "Hypotenuse of the triangle ABC, length = 5, depends on points B and C."}},
            {{"object": "Point O", "description": "Center of the circumcircle of triangle ABC, depends on the midpoint of BC."}},
            {{"object": "Circumcircle", "description": "Circle passing through points A, B, and C, depends on points A, B, and C."}},
            {{"object": "Radius R", "description": "Radius of the circumcircle, R = 2.5, depends on the length of BC."}}
        ]
        }}

        Return:
        ```asy
        import olympiad; import settings; size(600, 600);
        pair A = (0,0);
        pair B = (3,0);
        pair C = (0,4);
        pair O = midpoint(B--C);

        path circ = circumcircle(A,B,C);

        draw(A--B--C--cycle);
        draw(circ);

        label("$A$",A,SW);
        label("$B$",B,SE);
        label("$C$",C,N);
        label("$O$",O,NE);

        label("$3$", midpoint(A--B), S);
        label("$4$", midpoint(A--C), W);
        label("$5$", midpoint(B--C), NE);
        label("$2.5$", midpoint(O--C), E);

        draw(rightanglemark(B,A,C,10));
        ```

        Student_drawing_steps: {student_drawing_steps}
        Asymptote_drawing_steps: {asymptote_drawing_steps}
        Reasoning: {geometry_reasoning}
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
    Student_drawing_steps:
    {{
        "illustration_steps": [
            "Vẽ tam giác ABC với AB = CB.",
            "Vẽ góc ABC bằng 36 độ.",
            "Vẽ đường tròn đi qua ba điểm A, B, C.",
            "Xác định tâm O của đường tròn.",
            "Nối các điểm O với B và O với C để tạo thành góc BOC."
    ]}}

    Return:
    {{
    "asymptote_drawing_steps": [
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
    ]
    }}

    Student_drawing_steps: {student_drawing_steps}
    Return:
    """

prompt_get_geometry_reasoning = """
    You are an expert in geometry problem solving. Given the following geometry problem and its solution.
    From a mathematical perspective, answer what are the objects whose coordinates can be randomly generated in the solution.
    And what are the objects that depend on the others when drawing the geometric construction.
    With the random objects, always generate coordinates for the points in the solution.
    With the dependent objects, dont give any coordinates, just describe them and its relationship with the random objects.
    Requirements:
    - Just focus on the objects and return only objects.
    - The output should be a list of objects, each described in a clear and concise manner.
    - Return answer in JSON format instead of human language, showing the programming logically.
    - No markdown marks or redundant text.

    

    Example:
    Student_drawing_steps:
    {{
        "illustration_steps": [
            "Vẽ tam giác ABC với AB = CB.",
            "Vẽ góc ABC bằng 36 độ.",
            "Vẽ đường tròn đi qua ba điểm A, B, C.",
            "Xác định tâm O của đường tròn.",
            "Nối các điểm O với B và O với C để tạo thành góc BOC."
    ]}}

    Asymptote_drawing_steps:
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
        }}
    ]
    }}
    
    Student_drawing_steps: {student_drawing_steps}
    Asymptote_drawing_steps: {asymptote_drawing_steps}
    Return:
"""
