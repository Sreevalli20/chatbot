from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pathlib import Path
from app.api.routes import router


# Get the project root directory (app/main.py -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="InvoiceAI",
    description="Turn customer requests into review-ready invoices in seconds.",
    version="1.0.0"
)

# Include API routes
app.include_router(router)

# Mount static files and templates with absolute paths
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "templates" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
