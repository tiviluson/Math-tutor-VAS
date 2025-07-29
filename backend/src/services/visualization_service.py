"""
Visualization Service for Asymptote geometric diagram generation.
Handles the creation of geometric visualizations from problem data.
"""

from typing import Dict, Any, Optional

from src.api.asymptote.viz_tool import get_visualization


class VisualizationService:
    """
    Service for generating geometric visualizations using Asymptote.
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        self.available = True
        try:
            # Test if visualization tools are available
            # This could be expanded to check for Asymptote installation
            pass
        except Exception:
            self.available = False
    
    def generate_illustration(
        self, 
        session_id: str, 
        problem: str, 
        illustration_steps: list
    ) -> Dict[str, Any]:
        """
        Generate a geometric illustration for the given problem.
        
        Args:
            session_id: Unique session identifier
            problem: The original problem text
            illustration_steps: List of illustration steps
            
        Returns:
            Dictionary with visualization result
        """
        if not self.available:
            return {
                "success": False,
                "error": "Visualization service is not available",
                "b64_string_viz": None
            }
        
        try:
            # Format illustration steps for the visualization function
            student_drawing_steps = {"illustration_steps": illustration_steps}
            
            # Call the get_visualization function
            b64_string_viz = get_visualization(
                session_id=session_id,
                problem=problem,
                student_drawing_steps=student_drawing_steps,
            )
            
            if b64_string_viz:
                return {
                    "success": True,
                    "message": "Illustration generated successfully",
                    "b64_string_viz": b64_string_viz,
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to generate illustration",
                    "b64_string_viz": None,
                    "error": "Visualization generation returned empty result",
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Failed to generate illustration",
                "b64_string_viz": None,
                "error": str(e),
            }
    
    def is_available(self) -> bool:
        """Check if the visualization service is available."""
        return self.available
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the visualization service."""
        return {
            "available": self.available,
            "service_type": "asymptote",
            "supported_formats": ["jpg", "png", "svg"] if self.available else []
        }