#!/usr/bin/env python3

import asyncio
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

from modules.browser import BrowserHandler
from modules.headers_analyzer import HeadersAnalyzer
from modules.screenshot import ScreenshotTaker
from modules.reporter import ReportGenerator
from modules.signature_analyzer import SignatureAnalyzer

def setup_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / f"eyewitness2_{timestamp}.log"),
            logging.StreamHandler()
        ]
    )

async def process_url(url, output_dir):
    logger = logging.getLogger("eyewitness2")
    logger.info(f"processing: {url}")
    
    url_safe_name = url.replace("://", "_").replace("/", "_").replace(".", "_")
    url_dir = output_dir / url_safe_name
    url_dir.mkdir(exist_ok=True)
    
    results = {"url": url, "timestamp": datetime.now().isoformat()}
    
    browser_handler = BrowserHandler()
    headers_analyzer = HeadersAnalyzer()
    screenshot_taker = ScreenshotTaker()
    signature_analyzer = SignatureAnalyzer()
    
    try:
        page = await browser_handler.navigate_to_url(url)
        
        headers_data = await headers_analyzer.analyze(page, url)
        results["headers"] = headers_data

        signature_data = await signature_analyzer.analyze(page)
        results["signatures"] = signature_data

        screenshot_path = url_dir / "screenshot.png"
        await screenshot_taker.take_screenshot(page, screenshot_path)
        results["screenshot"] = str(screenshot_path)
        
        with open(url_dir / "data.json", "w") as f:
            json.dump(results, f, indent=2)
        
        await browser_handler.close()
        return results
        
    except Exception as e:
        logger.error(f"error processing {url}: {str(e)}")
        results["error"] = str(e)
        return results

async def main():
    parser = argparse.ArgumentParser(description="eyewitness2")
    parser.add_argument(
        "-u", "--urls", nargs="+", required=True,
        help="list of urls to scan"
    )
    parser.add_argument(
        "-o", "--output", default="results",
        help="output directory (default: results)"
    )
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger("eyewitness2")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"scanning {len(args.urls)} URLs")
    
    tasks = [process_url(url, output_dir) for url in args.urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    report_generator = ReportGenerator()
    index_path = report_generator.generate_reports(results, output_dir)
    
    logger.info(f"scans complete. dashboard @ {index_path}")
    
    try:
        import webbrowser
        webbrowser.open(f"file://{index_path.absolute()}")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())
