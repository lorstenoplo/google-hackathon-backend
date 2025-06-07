from app.models.schemas import AccessibilityRequest, AccessibilityResponse
from fastapi import APIRouter, HTTPException

from app.services.accessibility_service import AccessibilityService

router = APIRouter(
    prefix="/web-accessibility",
    tags=["Web Accessibility"]
)

# Initialize service
accessibility_service = AccessibilityService()


@router.post("/check-accessibility", response_model=AccessibilityResponse)
async def check_accessibility(request: AccessibilityRequest):
    """
    Check accessibility violations for a given URL

    - **url**: The website URL to check
    - **summarize**: Whether to generate an AI summary of violations (default: True)
    """
    try:
        # ✅ Await the async method
        result = await accessibility_service.run_accessibility_check(str(request.url))

        if not result:
            raise HTTPException(status_code=400, detail="Failed to generate accessibility report")

        violations = result.get("violations", [])

        # ✅ Await the summary generation if needed
        summary = None
        if request.summarize:
            summary = await accessibility_service.generate_summary(violations)

        return AccessibilityResponse(
            url=str(request.url),
            violations=violations,
            summary=summary,
            total_violations=len(violations)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
