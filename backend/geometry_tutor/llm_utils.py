"""
LLM integration and utility functions for the AI Geometry Tutor system.
"""

import os
import json
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from .prompts import prompt_templates


def initialize_llm(
    model_name: str = "gemini-2.0-flash-exp", temperature=0.1, max_output_token=2048
) -> Optional[ChatGoogleGenerativeAI]:
    """Initialize the Google Gemini LLM with appropriate settings."""
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_output_token,
        )
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        print("Please make sure you have set the GOOGLE_API_KEY environment variable")
        return None


# Pydantic models for structured outputs
class ParsedProblem(BaseModel):
    """Model for parsed geometry problem structure."""

    problem_statement_only: str = Field(
        description="Problem statement without any questions"
    )
    points: List[str] = Field(
        default_factory=list, description="List of geometric points"
    )
    lines: List[str] = Field(
        default_factory=list, description="List of geometric lines"
    )
    shapes: List[str] = Field(
        default_factory=list, description="List of geometric shapes"
    )
    given_facts: List[str] = Field(
        default_factory=list, description="List of given facts in Vietnamese"
    )
    questions: List[str] = Field(
        default_factory=list, description="List of questions in Vietnamese"
    )
    illustration_steps: List[str] = Field(
        default_factory=list, description="List of illustration steps in Vietnamese"
    )


class ReasoningStep(BaseModel):
    """Model for reasoning step structure."""

    thought: str = Field(
        default="Không thể phân tích bước này",
        description="Thought process for this step",
    )
    conclusion: str = Field(default="", description="Conclusion reached in this step")
    is_goal_reached: bool = Field(
        default=False, description="Whether the goal has been reached"
    )


class ValidationResult(BaseModel):
    """Model for validation result structure."""

    is_correct: bool = Field(
        default=False, description="Whether the solution is correct"
    )
    feedback: str = Field(
        default="Không thể đánh giá lời giải", description="Feedback on the solution"
    )
    score: int = Field(default=0, description="Score from 0-100")
    additional_illustration_steps: List[str] = Field(
        default_factory=list, description="Additional illustration steps if needed"
    )


class ExtractedText(BaseModel):
    """Model for extracted text from images."""

    problem_text: str = Field(description="Extracted problem text")
    illustration_description: Optional[str] = Field(
        default=None, description="Description of any illustrations"
    )


class InputClassification(BaseModel):
    """Model for classifying user input type."""
    
    input_type: str = Field(
        description="Type of input: question, complete_solution, partial_solution, statement, unclear"
    )
    confidence: int = Field(
        default=0, description="Confidence level 0-100"
    )
    explanation: str = Field(
        default="", description="Brief explanation of the classification"
    )


class QuestionExtraction(BaseModel):
    """Model for extracting new facts and illustration steps from question text."""

    new_facts: List[str] = Field(
        default_factory=list, description="New facts mentioned in the question"
    )
    new_illustration_steps: List[str] = Field(
        default_factory=list, description="New illustration steps mentioned in the question. If there are new illustration steps, they should be added to the existing ones coherently."
    )


def create_parsing_chain(llm):
    """Create a chain for parsing geometry problems."""
    parser = PydanticOutputParser(pydantic_object=ParsedProblem)

    prompt = PromptTemplate(
        template=prompt_templates.get_parsing_prompt(),
        input_variables=["problem"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def create_reasoning_chain(llm):
    """Create a chain for reasoning steps."""
    parser = PydanticOutputParser(pydantic_object=ReasoningStep)

    prompt = PromptTemplate(
        template=prompt_templates.get_reasoning_prompt(),
        input_variables=["solver_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def create_validation_chain(llm):
    """Create a chain for validation."""
    parser = PydanticOutputParser(pydantic_object=ValidationResult)

    prompt = PromptTemplate(
        template=prompt_templates.get_validation_prompt(),
        input_variables=["validation_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def create_text_extraction_chain(llm):
    """Create a chain for text extraction from images."""
    parser = PydanticOutputParser(pydantic_object=ExtractedText)

    prompt = PromptTemplate(
        template=prompt_templates.get_text_extraction_prompt(),
        input_variables=["extraction_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def create_vision_extraction_chain(llm):
    """Create a chain specifically for vision-based text extraction that handles HumanMessage."""
    parser = PydanticOutputParser(pydantic_object=ExtractedText)

    # For vision models, we need a different approach since we pass HumanMessage directly
    class VisionChain:
        def __init__(self, llm, parser):
            self.llm = llm
            self.parser = parser

        def invoke(self, message_with_image):
            """Process image with LLM and parse the response."""
            # Add format instructions to the text part of the message
            if hasattr(message_with_image, "content") and isinstance(
                message_with_image.content, list
            ):
                # Find the text content and replace it with the formatted prompt
                for item in message_with_image.content:
                    if item.get("type") == "text":
                        # Use the image analysis prompt template
                        item[
                            "text"
                        ] = prompt_templates.get_image_analysis_prompt().format(
                            format_instructions=self.parser.get_format_instructions()
                        )
                        break

            response = self.llm.invoke([message_with_image])
            return self.parser.parse(response.content)

    return VisionChain(llm, parser)


def create_input_classification_chain(llm):
    """Create a chain for classifying user input type."""
    parser = PydanticOutputParser(pydantic_object=InputClassification)

    prompt = PromptTemplate(
        template="{classification_prompt}\n{format_instructions}",
        input_variables=["classification_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def create_question_extraction_chain(llm):
    """Create a chain for extracting facts and steps from question text."""
    parser = PydanticOutputParser(pydantic_object=QuestionExtraction)

    prompt = PromptTemplate(
        template=prompt_templates.get_question_extraction_prompt(),
        input_variables=["question", "known_facts", "illustration_steps"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def safe_json_parse(text: str, default: Optional[dict] = None) -> dict:
    """Safely parse JSON from LLM output, handling common formatting issues."""
    if default is None:
        default = {}

    try:
        # Try to find JSON in the text
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx != -1 and end_idx != 0:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            return default
    except json.JSONDecodeError:
        return default


def setup_environment():
    """Setup environment variables and configuration."""
    from dotenv import load_dotenv

    # Load environment variables from .env file if it exists
    load_dotenv()

    # Check if Google API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it using: export GOOGLE_API_KEY='your-api-key'")
        print("Or create a .env file with: GOOGLE_API_KEY=your-api-key")
        return False

    return True
