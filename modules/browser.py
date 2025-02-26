import logging
from playwright.async_api import async_playwright

class BrowserHandler:
    def __init__(self):
        self.logger = logging.getLogger("eyewitness2.browser")
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def navigate_to_url(self, url):
        self.logger.info(f"navigating to {url}")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3",
            ignore_https_errors=True
        )
        
        page = await self.context.new_page()
        
        try:
            page.set_default_timeout(30000)

            response = await page.goto(url)
            
            if not response:
                self.logger.error(f"failed to navigate to {url}")
                raise Exception(f"failed to navigate to {url}")
                
            if response.status >= 400:
                self.logger.warning(
                    f"bad HTTP {response.status} for {url}")
            
            await page.wait_for_load_state("networkidle")
            
            return page
            
        except Exception as e:
            self.logger.error(f"error during navigation to {url}: {str(e)}")
            await self.close()
            raise
    
    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
