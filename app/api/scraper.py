"""
Web scraping API endpoints
Handles LeetCode and other website content scraping
"""
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

from core.scraper.leetcode import LeetCodeScraper
from core.scraper.base_scraper import BaseScraper
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize scrapers
leetcode_scraper = LeetCodeScraper()

# Global state for auto-scraping
auto_scraping_active = False
scraping_task = None

class ScrapeRequest(BaseModel):
    url: str
    platform: str = "leetcode"  # leetcode, codepen, etc.
    selectors: Optional[Dict[str, str]] = None

class AutoScrapeRequest(BaseModel):
    url: str
    interval: int = 10  # seconds
    platform: str = "leetcode"

@router.post("/manual")
async def manual_scrape(request: ScrapeRequest):
    """
    Manually scrape content from a URL
    """
    try:
        if request.platform == "leetcode":
            result = await leetcode_scraper.scrape_playground(request.url)
        else:
            # Use generic scraper for other platforms
            scraper = BaseScraper()
            result = await scraper.scrape(
                url=request.url,
                selectors=request.selectors or {}
            )
        
        return {
            "success": True,
            "platform": request.platform,
            "url": request.url,
            "timestamp": result.get("timestamp"),
            "code": result.get("code", ""),
            "language": result.get("language", ""),
            "problem_title": result.get("problem_title", ""),
            "test_results": result.get("test_results", []),
            "metadata": result.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"Manual scrape error: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/auto/start")
async def start_auto_scraping(request: AutoScrapeRequest, background_tasks: BackgroundTasks):
    """
    Start automatic scraping at specified intervals
    """
    global auto_scraping_active, scraping_task
    
    try:
        if auto_scraping_active:
            raise HTTPException(status_code=400, detail="Auto-scraping is already active")
        
        auto_scraping_active = True
        
        # Start background task
        background_tasks.add_task(
            auto_scrape_task,
            request.url,
            request.interval,
            request.platform
        )
        
        return {
            "success": True,
            "message": "Auto-scraping started",
            "url": request.url,
            "interval": request.interval,
            "platform": request.platform
        }
        
    except Exception as e:
        logger.error(f"Start auto-scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start auto-scraping: {str(e)}")

@router.post("/auto/stop")
async def stop_auto_scraping():
    """
    Stop automatic scraping
    """
    global auto_scraping_active, scraping_task
    
    try:
        auto_scraping_active = False
        
        if scraping_task and not scraping_task.done():
            scraping_task.cancel()
        
        return {
            "success": True,
            "message": "Auto-scraping stopped"
        }
        
    except Exception as e:
        logger.error(f"Stop auto-scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop auto-scraping: {str(e)}")

@router.get("/auto/status")
async def get_auto_scraping_status():
    """
    Get current auto-scraping status
    """
    return {
        "active": auto_scraping_active,
        "task_running": scraping_task is not None and not scraping_task.done() if scraping_task else False
    }

@router.get("/platforms")
async def get_supported_platforms():
    """
    Get list of supported scraping platforms
    """
    return {
        "platforms": [
            {
                "id": "leetcode",
                "name": "LeetCode",
                "description": "LeetCode problem solving platform",
                "supported_features": ["code", "test_results", "problem_info"]
            },
            {
                "id": "codepen",
                "name": "CodePen",
                "description": "Frontend code playground",
                "supported_features": ["code", "live_preview"]
            },
            {
                "id": "generic",
                "name": "Generic Web Scraper",
                "description": "Generic scraper for any website",
                "supported_features": ["custom_selectors"]
            }
        ]
    }

@router.post("/test-selectors")
async def test_selectors(url: str, selectors: Dict[str, str]):
    """
    Test CSS selectors on a given URL
    """
    try:
        scraper = BaseScraper()
        result = await scraper.test_selectors(url, selectors)
        
        return {
            "success": True,
            "url": url,
            "results": result
        }
        
    except Exception as e:
        logger.error(f"Test selectors error: {e}")
        raise HTTPException(status_code=500, detail=f"Testing selectors failed: {str(e)}")

async def auto_scrape_task(url: str, interval: int, platform: str):
    """
    Background task for automatic scraping
    """
    global auto_scraping_active
    
    logger.info(f"Starting auto-scraping for {url} every {interval} seconds")
    
    try:
        while auto_scraping_active:
            try:
                if platform == "leetcode":
                    result = await leetcode_scraper.scrape_playground(url)
                else:
                    scraper = BaseScraper()
                    result = await scraper.scrape(url)
                
                logger.info(f"Auto-scraped content from {url}")
                
                # Here you could emit the result via WebSocket
                # or store it in a database for the frontend to poll
                
            except Exception as e:
                logger.error(f"Auto-scraping error: {e}")
            
            # Wait for the specified interval
            await asyncio.sleep(interval)
            
    except asyncio.CancelledError:
        logger.info("Auto-scraping task cancelled")
    finally:
        auto_scraping_active = False
        logger.info("Auto-scraping task ended")

@router.get("/leetcode/problem-info")
async def get_leetcode_problem_info(url: str):
    """
    Get LeetCode problem information
    """
    try:
        info = await leetcode_scraper.get_problem_info(url)
        
        return {
            "success": True,
            "problem_info": info
        }
        
    except Exception as e:
        logger.error(f"Get problem info error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get problem info: {str(e)}")

@router.get("/status")
async def get_scraper_status():
    """
    Get scraper service status
    """
    return {
        "leetcode_available": await leetcode_scraper.is_available(),
        "auto_scraping_active": auto_scraping_active,
        "default_interval": settings.scraping_interval,
        "headless_mode": settings.headless_mode
    } 