from pydantic import BaseModel, Field


class Persona(BaseModel):
    """Base persona model for all agents."""
    name: str = Field(..., description="Name of the persona")
    background: str = Field(..., description="Background of the persona")


class Personas(BaseModel):
    """List of personas."""
    personas: list[Persona] = Field(
        default_factory=list, description="List of personas"
    )
