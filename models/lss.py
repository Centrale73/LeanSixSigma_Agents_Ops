from pydantic import BaseModel, Field

class LSSResponse(BaseModel):
    """
    The LSS Governance Layer structure. 
    Every cognitive action must map to this DMAIC workflow.
    """
    define: str = Field(
        ..., 
        description="Define the User's core goal clearly. What is the problem statement?"
    )
    measure: str = Field(
        ..., 
        description="The 'Definition of Done'. What quantitative or qualitative success criteria are we measuring against?"
    )
    analyze: str = Field(
        ..., 
        description="Root cause analysis or the core research content derived from Perplexity tools."
    )
    improve: str = Field(
        ..., 
        description="The actionable solution, report content, or code generated to address the problem."
    )
    control: int = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Confidence Score (0-100). How well does the 'Improve' output meet the 'Measure' criteria?"
    )