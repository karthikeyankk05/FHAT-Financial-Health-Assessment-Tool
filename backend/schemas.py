from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ----------------------------
# USER SCHEMAS
# ----------------------------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# BUSINESS SCHEMAS
# ----------------------------

class BusinessCreate(BaseModel):
    name: str
    industry: str


class BusinessResponse(BaseModel):
    id: int
    name: str
    industry: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# FINANCIAL INPUT SCHEMA
# ----------------------------

class FinancialInput(BaseModel):
    revenue: float = Field(..., gt=0)
    expenses: float = Field(..., ge=0)
    assets: float = Field(..., ge=0)
    liabilities: float = Field(..., ge=0)
    receivables: float = Field(..., ge=0)
    payables: float = Field(..., ge=0)
    inventory: Optional[float] = 0
    debt: Optional[float] = 0


# ----------------------------
# METRICS RESPONSE
# ----------------------------

class FinancialMetricsResponse(BaseModel):
    gross_margin: float
    current_ratio: float
    debt_to_equity: float
    working_capital: float


# ----------------------------
# RISK RESPONSE
# ----------------------------

class RiskResponse(BaseModel):
    score: int
    category: str


# ----------------------------
# INVESTOR RESPONSE
# ----------------------------

class InvestorResponse(BaseModel):
    score: int
    category: str


# ----------------------------
# FRAUD RESPONSE
# ----------------------------

class FraudResponse(BaseModel):
    flags: List[str]


# ----------------------------
# ESG RESPONSE
# ----------------------------

class ESGResponse(BaseModel):
    score: int
    category: str


# ----------------------------
# EARLY WARNING RESPONSE
# ----------------------------

class WarningResponse(BaseModel):
    warnings: List[str]


# ----------------------------
# FULL ANALYSIS RESPONSE
# ----------------------------

class FullAnalysisResponse(BaseModel):
    metrics: FinancialMetricsResponse
    risk: RiskResponse
    investor: InvestorResponse
    fraud: FraudResponse
    esg: ESGResponse
    warnings: WarningResponse
    ai_summary: str
