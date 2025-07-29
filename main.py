from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from bs4 import BeautifulSoup

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str

@app.get("/ping")
async def ping():
    return {"status": "OK"}

@app.post("/analyze")
async def analyze_seo(data: AnalyzeRequest):
    url = data.url

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch page")
                html = await response.text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching page: {str(e)}")

    soup = BeautifulSoup(html, "html.parser")

    # Basic analysis
    score = 100
    issues = []

    title = soup.title.string if soup.title else ""
    if not title:
        score -= 10
        issues.append("Missing title tag")

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if not meta_desc or not meta_desc.get("content"):
        score -= 10
        issues.append("Missing meta description")

    h1 = soup.find("h1")
    if not h1:
        score -= 5
        issues.append("Missing H1 tag")

    images = soup.find_all("img")
    if any("alt" not in img.attrs for img in images):
        score -= 5
        issues.append("Some images are missing alt attributes")

    return {
        "score": score,
        "issues": issues,
        "title": title.strip() if title else "",
        "meta_description": meta_desc.get("content", "") if meta_desc else "",
        "h1": h1.text.strip() if h1 else "",
    }
