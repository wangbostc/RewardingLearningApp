import uvicorn
from app import create_app

# Create FastAPI application
app = create_app()

if __name__ == '__main__':
    # Run the development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
