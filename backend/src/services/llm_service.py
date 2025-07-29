"""
LLM Service for managing language model initialization and operations.
Centralizes all LLM-related functionality and configuration.
"""

from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.geometry_tutor.llm_utils import (
    initialize_llm,
    setup_environment,
    ParsedProblem,
    ReasoningStep,
    ValidationResult,
    InputClassification,
    QuestionExtraction,
)
from src.geometry_tutor.prompts import prompt_templates


class LLMService:
    """
    Service for managing LLM operations and chain creation.
    Provides centralized access to language model functionality.
    """
    
    _instance: Optional['LLMService'] = None
    _llm: Optional[ChatGoogleGenerativeAI] = None
    
    def __new__(cls) -> 'LLMService':
        """Singleton pattern to ensure only one LLM service instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the LLM service."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._setup_llm()
    
    def _setup_llm(self) -> None:
        """Setup the LLM instance with environment validation."""
        if not setup_environment():
            raise RuntimeError(
                "Environment setup failed. Please check your GOOGLE_API_KEY configuration."
            )
        
        self._llm = initialize_llm()
        if not self._llm:
            raise RuntimeError("Failed to initialize LLM instance.")
    
    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        """Get the LLM instance."""
        if not self._llm:
            raise RuntimeError("LLM not properly initialized")
        return self._llm
    
    def create_parsing_chain(self):
        """Create a chain for parsing geometry problems."""
        parser = PydanticOutputParser(pydantic_object=ParsedProblem)
        
        prompt = PromptTemplate(
            template=prompt_templates.get_parsing_prompt(),
            input_variables=["problem"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        return prompt | self.llm | parser
    
    def create_reasoning_chain(self):
        """Create a chain for reasoning steps."""
        parser = PydanticOutputParser(pydantic_object=ReasoningStep)
        
        prompt = PromptTemplate(
            template=prompt_templates.get_reasoning_prompt(),
            input_variables=["solver_prompt"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        return prompt | self.llm | parser
    
    def create_validation_chain(self):
        """Create a chain for validation."""
        parser = PydanticOutputParser(pydantic_object=ValidationResult)
        
        prompt = PromptTemplate(
            template=prompt_templates.get_validation_prompt(),
            input_variables=["validation_prompt"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        return prompt | self.llm | parser
    
    def create_input_classification_chain(self):
        """Create a chain for classifying user input type."""
        parser = PydanticOutputParser(pydantic_object=InputClassification)
        
        prompt = PromptTemplate(
            template="{classification_prompt}\n{format_instructions}",
            input_variables=["classification_prompt"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        return prompt | self.llm | parser
    
    def create_question_extraction_chain(self):
        """Create a chain for extracting facts and steps from question text."""
        parser = PydanticOutputParser(pydantic_object=QuestionExtraction)
        
        prompt = PromptTemplate(
            template=prompt_templates.get_question_extraction_prompt(),
            input_variables=["question", "known_facts", "illustration_steps"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        return prompt | self.llm | parser
    
    def generate_simple_response(self, prompt: str) -> str:
        """Generate a simple text response from a prompt."""
        try:
            response = self.llm.invoke(prompt)
            
            # Handle response content properly based on type
            if hasattr(response, "content"):
                if isinstance(response.content, str):
                    return response.content.strip()
                else:
                    return str(response.content)
            else:
                return str(response)
        except Exception as e:
            raise RuntimeError(f"Failed to generate LLM response: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the LLM service is available and properly configured."""
        return self._llm is not None
    
    def get_model_info(self) -> dict:
        """Get information about the current LLM model."""
        if not self._llm:
            return {"available": False, "error": "LLM not initialized"}
        
        return {
            "available": True,
            "model_name": getattr(self._llm, 'model_name', 'unknown'),
            "temperature": getattr(self._llm, 'temperature', 'unknown'),
            "max_output_tokens": getattr(self._llm, 'max_output_tokens', 'unknown'),
        }