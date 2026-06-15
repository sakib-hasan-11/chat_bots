from typing import List

from pydantic import BaseModel, Field


class FactMemory(BaseModel):
    career_goals: List[str] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    current_focus: List[str] = Field(default_factory=list)
    version:int=1
