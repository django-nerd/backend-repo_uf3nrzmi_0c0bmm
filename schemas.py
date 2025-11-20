"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ---------------- Living Trust & NGO Management Schemas ----------------

class Trust(BaseModel):
    name: str = Field(..., description="Trust name")
    purpose: Optional[str] = Field(None, description="Purpose and mission of the trust")
    inception_date: Optional[date] = Field(None, description="Date the trust was established")
    registration_number: Optional[str] = Field(None, description="Official registration or EIN")

class Beneficiary(BaseModel):
    full_name: str = Field(..., description="Beneficiary full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    relation: Optional[str] = Field(None, description="Relationship to grantor")
    allocation_percent: Optional[float] = Field(None, ge=0, le=100, description="Allocation percentage")
    notes: Optional[str] = Field(None, description="Additional details")

class Trustee(BaseModel):
    full_name: str = Field(..., description="Trustee full name")
    role: str = Field(..., description="Role (Primary, Co-Trustee, Successor)")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")

class Asset(BaseModel):
    title: str = Field(..., description="Asset title")
    category: str = Field(..., description="Category (Real Estate, Cash, Investment, Vehicle, Other)")
    value: Optional[float] = Field(None, ge=0, description="Estimated value")
    owner: Optional[str] = Field(None, description="Titled owner (Trust / Individual)")
    notes: Optional[str] = Field(None, description="Notes about the asset")

class Distribution(BaseModel):
    beneficiary_name: str = Field(..., description="Beneficiary receiving the distribution")
    amount: float = Field(..., ge=0, description="Amount to distribute")
    schedule: str = Field(..., description="Schedule (One-time, Monthly, Quarterly, Yearly)")
    purpose: Optional[str] = Field(None, description="Purpose or conditions")

class NGO(BaseModel):
    name: str = Field(..., description="NGO name")
    registration_id: Optional[str] = Field(None, description="NGO registration ID")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    focus_areas: Optional[List[str]] = Field(None, description="Focus areas e.g., Education, Health")

class Donation(BaseModel):
    ngo_name: str = Field(..., description="Recipient NGO name")
    amount: float = Field(..., ge=0, description="Donation amount")
    date_given: Optional[date] = Field(None, description="Date of donation")
    source_asset: Optional[str] = Field(None, description="Source asset for funds")
    notes: Optional[str] = Field(None, description="Notes or restrictions")

class ComplianceDocument(BaseModel):
    title: str = Field(..., description="Document name")
    doc_type: str = Field(..., description="Type (Annual Report, Tax Filing, Meeting Minutes, Policy)")
    status: str = Field(..., description="Status (Draft, Submitted, Approved, Expired)")
    due_date: Optional[date] = Field(None, description="Due date if applicable")
    link: Optional[str] = Field(None, description="Link or storage reference")

# ---------------- Example Schemas kept for reference (not used by UI) ----------------

class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

# Notes:
# - Each Pydantic model corresponds to a collection with the lowercase class name.
# - The Flames database viewer can introspect these models.
