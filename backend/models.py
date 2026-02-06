from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# ----------------------------
# USER MODEL
# ----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="business_owner")  # RBAC support
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    businesses = relationship("Business", back_populates="owner")


# ----------------------------
# BUSINESS MODEL
# ----------------------------
class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="businesses")
    financials = relationship("FinancialStatement", back_populates="business")


# ----------------------------
# FINANCIAL STATEMENT MODEL
# ----------------------------
class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))

    revenue = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    assets = Column(Float, nullable=False)
    liabilities = Column(Float, nullable=False)

    receivables = Column(Float, nullable=False)
    payables = Column(Float, nullable=False)
    inventory = Column(Float, nullable=True)
    debt = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="financials")


# ----------------------------
# RISK SCORE MODEL
# ----------------------------
class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    score = Column(Integer)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# INVESTOR READINESS MODEL
# ----------------------------
class InvestorScore(Base):
    __tablename__ = "investor_scores"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    score = Column(Integer)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# FRAUD FLAGS MODEL
# ----------------------------
class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    flag_type = Column(String)
    description = Column(Text)
    severity = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# ESG SCORE MODEL
# ----------------------------
class ESGScore(Base):
    __tablename__ = "esg_scores"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    score = Column(Integer)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# EARLY WARNING MODEL
# ----------------------------
class EarlyWarning(Base):
    __tablename__ = "early_warnings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    warning_type = Column(String)
    message = Column(Text)
    severity = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# BANKING SYNC MODEL
# ----------------------------
class BankSync(Base):
    __tablename__ = "bank_syncs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)

    provider = Column(String, nullable=False)
    account_balance = Column(Float, nullable=False)
    transactions_json = Column(Text, nullable=False)

    last_sync_time = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# GST FILING MODEL
# ----------------------------
class GSTFiling(Base):
    """
    Stores imported GST filing data and compliance metadata per business.
    """

    __tablename__ = "gst_filings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)

    gst_collected = Column(Float, nullable=False)
    gst_paid = Column(Float, nullable=False)
    input_credit = Column(Float, nullable=False)
    output_tax = Column(Float, nullable=False)

    period = Column(String, nullable=True)  # Example: "2025-04"
    tax_metadata = Column(Text, nullable=True)  # ✅ FIXED (was metadata)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# COMPLIANCE ISSUE MODEL
# ----------------------------
class ComplianceIssue(Base):
    __tablename__ = "compliance_issues"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)

    issue_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
