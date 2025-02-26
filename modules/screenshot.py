import logging
from pathlib import Path

class ScreenshotTaker:
    def __init__(self):
        self.logger = logging.getLogger("eyewitness2.screenshot")
    
    async def take_screenshot(self, page, output_path):
        self.logger.info(f"taking screenshot and saving to {output_path}")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        await page.screenshot(
            path=str(output_path), 
            full_page=True,
            type="png"
        )
        
        return str(output_path)

