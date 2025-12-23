"""
TruFindAI Backend - Debug Version
"""
print("=" * 50)
print("STARTING TRUFINDAI BACKEND")
print("=" * 50)

print("\n1. Importing FastAPI...")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
print("✅ FastAPI imported")

print("\n2. Importing config...")
try:
    from app.config import settings
    print(f"✅ Config imported - Environment: {settings.ENVIRONMENT}")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    exit(1)

print("\n3. Importing routes...")

try:
    from app.routes.analysis import router as analysis_router
    print("✅ Analysis route imported")
except Exception as e:
    print(f"❌ Analysis route failed: {e}")
    analysis_router = None

try:
    from app.routes.sara import router as sara_router
    print("✅ Sara route imported")
except Exception as e:
    print(f"❌ Sara route failed: {e}")
    sara_router = None

try:
    from app.routes.history import router as history_router
    print("✅ History route imported")
except Exception as e:
    print(f"❌ History route failed: {e}")
    history_router = None

try:
    from app.routes.recordings import router as recordings_router
    print("✅ Recordings route imported")
except Exception as e:
    print(f"❌ Recordings route failed: {e}")
    recordings_router = None

try:
    from app.routes.webhooks import router as webhooks_router
    print("✅ Webhooks route imported")
except Exception as e:
    print(f"❌ Webhooks route failed: {e}")
    webhooks_router = None

print("\n4. Creating FastAPI app...")
app = FastAPI(
    title="TruFindAI API",
    description="AI-powered website analysis and sales automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
print("✅ App created")

print("\n5. Adding middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("✅ Middleware added")

print("\n6. Creating base routes...")

@app.get("/")
async def root():
    return {
        "message": "TruFindAI API",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

print("✅ Base routes created")

print("\n7. Including routers...")

if analysis_router:
    app.include_router(
        analysis_router,
        prefix=f"{settings.API_V1_PREFIX}/analysis",
        tags=["Analysis"]
    )
    print("✅ Analysis router included")

if sara_router:
    app.include_router(
        sara_router,
        prefix=f"{settings.API_V1_PREFIX}/sara",
        tags=["Sara Agent"]
    )
    print("✅ Sara router included")

if history_router:
    app.include_router(
        history_router,
        prefix=f"{settings.API_V1_PREFIX}/history",
        tags=["History"]
    )
    print("✅ History router included")

if recordings_router:
    app.include_router(
        recordings_router,
        prefix=f"{settings.API_V1_PREFIX}/recordings",
        tags=["Recordings"]
    )
    print("✅ Recordings router included")

if webhooks_router:
    app.include_router(
        webhooks_router,
        prefix=f"{settings.API_V1_PREFIX}/webhooks",
        tags=["Webhooks"]
    )
    print("✅ Webhooks router included")

print("\n" + "=" * 50)
print("✅ BACKEND INITIALIZATION COMPLETE!")
print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)