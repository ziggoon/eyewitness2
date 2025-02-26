import logging

class HeadersAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger("eyewitness2.headers")
    
    async def analyze(self, page, url):
        self.logger.info(f"analyzing headers for {url}")
        
        result = {
            "http_headers": {},
            "metadata": {},
            "security_headers": {},
        }
        
        response = await page.request.fetch(url)
        headers = response.headers
        result["http_headers"] = dict(headers)
        
        security_headers = [
            "Content-Security-Policy",
            "X-XSS-Protection",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Strict-Transport-Security",
            "Referrer-Policy",
            "Feature-Policy",
            "Permissions-Policy"
        ]
        
        for header in security_headers:
            if header.lower() in (key.lower() for key in headers.keys()):
                actual_key = next(key for key in headers.keys() 
                              if key.lower() == header.lower())
                result["security_headers"][header] = headers[actual_key]
            else:
                result["security_headers"][header] = "Not set"
        
        result["metadata"]["title"] = await page.title()
        
        meta_tags = await page.evaluate("""() => {
            const metaTags = document.querySelectorAll('meta');
            const result = {};
            metaTags.forEach(tag => {
                const name = tag.getAttribute('name') || 
                           tag.getAttribute('property');
                const content = tag.getAttribute('content');
                if (name && content) {
                    result[name] = content;
                }
            });
            return result;
        }""")
        
        result["metadata"]["meta_tags"] = meta_tags
        
        return result
