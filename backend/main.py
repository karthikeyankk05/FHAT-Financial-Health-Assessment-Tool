from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from database import Base, engine

# Import all route modules
from routes.upload import router as upload_router
from routes.pdf_upload import router as pdf_upload_router
from routes.analysis import router as analysis_router
from routes.risk import router as risk_router
from routes.investor import router as investor_router
from routes.esg import router as esg_router
from routes.fraud import router as fraud_router
from routes.banking import router as banking_router
from routes.gst import router as gst_router
from routes.forecasting import router as forecasting_router
from routes.report import router as report_router

# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------

app = FastAPI(
    title="FHAT - Financial Health Assessment Tool",
    description="AI-powered SME Financial Intelligence Platform",
    version="1.0.0"
)

# --------------------------------------------------
# Enable CORS (VERY IMPORTANT for React frontend)
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds basic security headers to all responses.
    Intended as a starting point for production hardening.
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        return response


class RateLimitingSkeletonMiddleware(BaseHTTPMiddleware):
    """
    Minimal, in-memory rate limiting skeleton.

    For real deployments, plug in Redis or an API gateway.
    Currently only annotates responses; does not block traffic aggressively.
    """

    async def dispatch(self, request: Request, call_next):
        # Placeholder: production impl would track counts per-IP/per-route.
        response: Response = await call_next(request)
        response.headers.setdefault("X-RateLimit-Policy", "prototype")
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitingSkeletonMiddleware)

# --------------------------------------------------
# Create database tables
# --------------------------------------------------

Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# Include routers
# --------------------------------------------------

app.include_router(upload_router, tags=["Upload"])
app.include_router(pdf_upload_router, tags=["Upload"])
app.include_router(analysis_router, tags=["Analysis"])
app.include_router(risk_router, tags=["Risk"])
app.include_router(investor_router, tags=["Investor"])
app.include_router(esg_router, tags=["ESG"])
app.include_router(fraud_router, tags=["Fraud"])
app.include_router(banking_router, tags=["Banking"])
app.include_router(gst_router, tags=["GST"])
app.include_router(forecasting_router, tags=["Forecasting"])
app.include_router(report_router, tags=["Reports"])

# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "FHAT Backend Running 🚀",
        "status": "healthy"
    }

# --------------------------------------------------
# Health check endpoint
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "OK"}
