from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import auth_controller, user_controller, subscription_controller, image_controller, plan_controller

app = FastAPI(
    title="Image Processing API",
    description="MVC-based FastAPI application for image processing with subscription plans",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(user_controller.router, prefix="/api/v1")
app.include_router(subscription_controller.router, prefix="/api/v1")
app.include_router(image_controller.router, prefix="/api/v1")
app.include_router(plan_controller.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Image Processing API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
