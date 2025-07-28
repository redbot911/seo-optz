# backend/analyzer.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import aiohttp

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str

@router.post("/analyze")
async def analyze_seo(data: AnalyzeRequest):
    url = data.url

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch page")
                html = await response.text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching page: {e}")

    soup = BeautifulSoup(html, "html.parser")

    issues = []

    # SEO Checks
    if not soup.title:
        issues.append("Missing <title> tag")
    if not soup.find("meta", attrs={"name": "description"}):
        issues.append("Missing meta description")
    if len(soup.find_all("h1")) != 1:
        issues.append("Page should have exactly one <h1> tag")
    if "alt" not in str(soup.find_all("img")):
        issues.append("Some images may be missing alt tags")

    score = max(0, 100 - len(issues) * 10)

    return {
        "score": score,
        "issues": issues
    }
