from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class CourseBase(BaseModel):
    code: str = Field(..., example="COMS4153", description="Course code")
    title: str = Field(..., example="Cloud Computing", description="Course title")
    instructor: str = Field(..., example="Prof. Ferguson", description="Instructor name")
    semester: str = Field(..., example="Fall 2025", description="Semester/term")

# Removed id from here
class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    instructor: Optional[str] = None
    semester: Optional[str] = None

# id now belongs only in the "read" model
class CourseRead(CourseBase):
    id: UUID = Field(default_factory=uuid4, description="Course ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
