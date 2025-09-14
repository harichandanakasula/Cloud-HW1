from __future__ import annotations

import os
import socket
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Path


from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health

# NEW models 
from models.course import CourseCreate, CourseRead, CourseUpdate
from models.assignment import AssignmentCreate, AssignmentRead, AssignmentUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}

# NEW in-memory stores
courses: Dict[UUID, CourseRead] = {}
assignments: Dict[UUID, AssignmentRead] = {}

app = FastAPI(
    title="Person/Address/Health/Course/Assignment API",
    description="Demo FastAPI app using Pydantic v2 models for Person, Address, Health, Course, Assignment",
    version="0.2.0",
)
def make_health(echo: Optional[str], path_echo: Optional[str] = None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo,
    )

@app.get("/health", response_model=Health, tags=["health"])
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health, tags=["health"])
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201, tags=["addresses"])
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead], tags=["addresses"])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead, tags=["addresses"])
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead, tags=["addresses"])
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

@app.post("/persons", response_model=PersonRead, status_code=201, tags=["persons"])
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead], tags=["persons"])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead, tags=["persons"])
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead, tags=["persons"])
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]


@app.post("/courses", response_model=CourseRead, status_code=201, tags=["courses"])
def create_course(course: CourseCreate):
    # simple uniqueness check: (code, semester) 
    if any(c.code == course.code and c.semester == course.semester for c in courses.values()):
        raise HTTPException(status_code=409, detail="Course already exists for this semester")

    data = course.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = data["created_at"]

    record = CourseRead(**data)
    courses[record.id] = record
    return record

@app.get("/courses", response_model=List[CourseRead], tags=["courses"])
def list_courses(
    code: Optional[str] = Query(None, description="Filter by course code"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    instructor: Optional[str] = Query(None, description="Filter by instructor"),
):
    result = list(courses.values())
    if code is not None:
        result = [c for c in result if c.code == code]
    if semester is not None:
        result = [c for c in result if c.semester == semester]
    if instructor is not None:
        result = [c for c in result if c.instructor == instructor]
    return result

@app.get("/courses/{course_id}", response_model=CourseRead, tags=["courses"])
def get_course(course_id: UUID):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    return courses[course_id]

@app.patch("/courses/{course_id}", response_model=CourseRead, tags=["courses"])
def update_course(course_id: UUID, update: CourseUpdate):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    stored = courses[course_id].model_dump()
    newvals = update.model_dump(exclude_unset=True)
    # if code/semester change, check for uniqueness
    new_code = newvals.get("code", stored["code"])
    new_sem = newvals.get("semester", stored["semester"])
    if any(c.id != course_id and c.code == new_code and c.semester == new_sem for c in courses.values()):
        raise HTTPException(status_code=409, detail="Course already exists for this semester")
    stored.update(newvals)
    stored["updated_at"] = datetime.utcnow()
    courses[course_id] = CourseRead(**stored)
    return courses[course_id]

@app.delete("/courses/{course_id}", status_code=204, tags=["courses"])
def delete_course(course_id: UUID):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    # cascade: delete assignments for this course
    for aid in [aid for aid, a in assignments.items() if a.course_id == course_id]:
        del assignments[aid]
    del courses[course_id]


@app.post("/assignments", response_model=AssignmentRead, status_code=201, tags=["assignments"])
def create_assignment(assignment: AssignmentCreate):
    if assignment.course_id not in courses:
        raise HTTPException(status_code=400, detail="course_id must refer to an existing course")
    data = assignment.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = data["created_at"]
    record = AssignmentRead(**data)      # id is generated here
    assignments[record.id] = record      # storing the generated id
    return record

@app.get("/assignments", response_model=List[AssignmentRead], tags=["assignments"])
def list_assignments(course_id: Optional[UUID] = Query(None, description="Filter by course_id")):
    result = list(assignments.values())
    if course_id is not None:
        result = [a for a in result if a.course_id == course_id]
    return result

@app.get("/assignments/{assignment_id}", response_model=AssignmentRead, tags=["assignments"])
def get_assignment(assignment_id: UUID):
    if assignment_id not in assignments:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignments[assignment_id]

@app.patch("/assignments/{assignment_id}", response_model=AssignmentRead, tags=["assignments"])
def update_assignment(assignment_id: UUID, update: AssignmentUpdate):
    if assignment_id not in assignments:
        raise HTTPException(status_code=404, detail="Assignment not found")
    stored = assignments[assignment_id].model_dump()
    newvals = update.model_dump(exclude_unset=True)
    
    if "course_id" in newvals and newvals["course_id"] not in courses:
        raise HTTPException(status_code=400, detail="course_id must refer to an existing course")
    stored.update(newvals)
    stored["updated_at"] = datetime.utcnow()
    assignments[assignment_id] = AssignmentRead(**stored)
    return assignments[assignment_id]

@app.delete("/assignments/{assignment_id}", status_code=204, tags=["assignments"])
def delete_assignment(assignment_id: UUID):
    if assignment_id not in assignments:
        raise HTTPException(status_code=404, detail="Assignment not found")
    del assignments[assignment_id]

@app.get("/", tags=["root"])
def root():
    return {
        "message": "Welcome to the Person/Address/Course/Assignment API. See /docs for OpenAPI UI."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("new_main:app", host="0.0.0.0", port=port, reload=True)
