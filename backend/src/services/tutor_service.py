"""
Tutor Service for core tutoring operations.
Handles the business logic of tutoring interactions.
"""

import base64
from typing import Dict, Any, Optional

from .llm_service import LLMService
from src.geometry_tutor.llm_utils import safe_json_parse


class TutorService:
    """
    Service for core tutoring operations.
    Handles image processing, problem parsing, and tutoring interactions.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the tutor service.
        
        Args:
            llm_service: LLM service instance. Creates new instance if None.
        """
        self.llm_service = llm_service or LLMService()
    
    async def process_image_to_text(self, image_b64: str) -> str:
        """
        Process base64 encoded image to extract geometry problem text using LLM.

        Args:
            image_b64: Base64 encoded image (can include data URL prefix or just base64)

        Returns:
            Extracted problem text from image
            
        Raises:
            ValueError: If image processing fails
        """
        try:
            # Validate base64 input
            if not image_b64 or not isinstance(image_b64, str):
                raise ValueError("Invalid base64 image data")

            # Clean up base64 string - remove data URL prefix if present
            if image_b64.startswith("data:image/"):
                # Extract just the base64 part after the comma
                if "," in image_b64:
                    image_b64 = image_b64.split(",", 1)[1]

            # Basic validation - try to decode base64
            try:
                image_data = base64.b64decode(image_b64)
                if len(image_data) == 0:
                    raise ValueError("Empty image data")
            except Exception as decode_error:
                raise ValueError(f"Invalid base64 image: {decode_error}")

            # Create the vision prompt
            prompt = """Bạn là một chuyên gia toán học, hãy phân tích hình ảnh bài toán hình học này và trích xuất thông tin.

Hãy thực hiện các nhiệm vụ sau:
1. Trích xuất toàn bộ văn bản của bài toán (nếu có) trong hình ảnh
2. Mô tả chi tiết hình vẽ/minh họa trong bài toán (nếu có)
3. Xác định xem có hình vẽ/minh họa trong ảnh hay không

Trả về kết quả theo định dạng JSON:
{
    "problem_text": "Văn bản bài toán đầy đủ đã được trích xuất từ hình ảnh",
    "illustration_description": "Mô tả chi tiết hình vẽ nếu có, ngược lại trả về chuỗi rỗng",
    "has_text_in_image": true/false,
    "has_illustration_in_image": true/false
}

Yêu cầu:
- Trích xuất chính xác toàn bộ văn bản trong hình ảnh
- Mô tả chi tiết các yếu tố hình học (điểm, đường, góc, hình dạng, v.v...) nếu có hình vẽ
- Đảm bảo văn bản tiếng Việt chính xác
- Nếu không có văn bản trong hình ảnh, trả về chuỗi rỗng cho problem_text
- Nếu không có hình vẽ minh họa, trả về chuỗi rỗng cho illustration_description và has_illustration_in_image = false
- Đặt has_illustration_in_image = true nếu có bất kỳ hình vẽ, sơ đồ, biểu đồ hình học nào trong ảnh"""

            # Prepare the message with image
            from langchain_core.messages import HumanMessage

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ]
            )

            # Make the LLM call
            try:
                response = self.llm_service.llm.invoke([message])
                response_text = response.content

                # Ensure response_text is a string
                if isinstance(response_text, list):
                    response_text = str(response_text)
                elif not isinstance(response_text, str):
                    response_text = str(response_text)

                # Try to parse JSON response
                result = safe_json_parse(response_text)

                if result and "problem_text" in result:
                    # Use the extracted text from LLM
                    final_text = result["problem_text"]

                    # Add illustration description only if there's actually an illustration in the image
                    if result.get("has_illustration_in_image", False) and result.get(
                        "illustration_description"
                    ):
                        final_text += (
                            f"\n\n[Mô tả hình vẽ: {result['illustration_description']}]"
                        )

                    if final_text.strip():
                        return final_text
                    else:
                        return "Không thể trích xuất thông tin từ hình ảnh. Vui lòng cung cấp văn bản bài toán."

                # If JSON parsing fails, try to extract text directly from response
                elif response_text.strip():
                    return response_text

                # If LLM response is empty
                else:
                    return "Không thể trích xuất thông tin từ hình ảnh. Vui lòng cung cấp văn bản bài toán."

            except Exception as llm_error:
                raise ValueError(f"Failed to process image with LLM: {llm_error}")

        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
    
    def validate_problem_text(self, problem_text: str) -> Dict[str, Any]:
        """
        Validate that problem text is suitable for processing.
        
        Args:
            problem_text: The problem text to validate
            
        Returns:
            Dictionary with validation result
        """
        if not problem_text or not problem_text.strip():
            return {
                "valid": False,
                "error": "Problem text cannot be empty"
            }
        
        # Basic validation - check minimum length
        if len(problem_text.strip()) < 10:
            return {
                "valid": False,
                "error": "Problem text is too short (minimum 10 characters)"
            }
        
        return {
            "valid": True,
            "message": "Problem text is valid"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the tutor service and its dependencies."""
        return {
            "service_available": True,
            "llm_service": self.llm_service.get_model_info()
        }