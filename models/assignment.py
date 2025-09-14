from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import date, datetime
from typing import Optional

class AssignmentBase(BaseModel):
    course_id: UUID = Field(..., description="Related Course ID")
    title: str = Field(..., example="HW1 – Microservices", description="Assignment title")
    due_date: Optional[date] = Field(None, example="2025-09-14", description="Due date (YYYY-MM-DD)")
    points: Optional[int] = Field(100, ge=0, le=1000, description="Max points")

class AssignmentCreate(AssignmentBase):
    pass  # no id here

class AssignmentUpdate(BaseModel):
    course_id: Optional[UUID] = None
    title: Optional[str] = None
    due_date: Optional[date] = None
    points: Optional[int] = Field(None, ge=0, le=1000)

class AssignmentRead(AssignmentBase):
    id: UUID = Field(default_factory=uuid4, description="Assignment ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
