"""
Database Schemas for Construction Company Website

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import date

class Lead(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = None
    project_location: Optional[str] = None
    project_type: Optional[Literal[
        "Residential", "Commercial", "Industrial", "Infrastructure", "Renovation", "Civil Works", "Other"
    ]] = None
    budget_estimate: Optional[str] = None
    desired_start_date: Optional[str] = None
    message: Optional[str] = Field(None, max_length=2000)
    newsletter_optin: bool = False
    attachment_url: Optional[str] = Field(None, description="Uploaded file URL if stored externally")

class Service(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = Field(None, description="Icon name for UI (lucide)")
    blurb: Optional[str] = None
    scope: Optional[List[str]] = None
    process: Optional[List[str]] = None
    deliverables: Optional[List[str]] = None

class Project(BaseModel):
    title: str
    slug: str
    category: Literal["Residential", "Commercial", "Industrial", "Infrastructure"]
    client: Optional[str] = None
    location: Optional[str] = None
    year: Optional[int] = None
    contract_value: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    gallery: Optional[List[str]] = None
    challenges: Optional[str] = None
    solutions: Optional[str] = None
    technologies: Optional[List[str]] = None
    testimonial: Optional[str] = None

class Post(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    published_at: Optional[date] = None
