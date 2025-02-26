import logging
import re
from pathlib import Path

class SignatureAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger("eyewitness2.signature")
        self.signatures = []
        self.categories = []
        self._load_signatures_and_categories()
    
    def _load_signatures_and_categories(self):
        base_dir = Path(__file__).parent.parent.absolute()
        signatures_file = base_dir / "data" / "signatures.txt"
        categories_file = base_dir / "data" / "categories.txt"
        
        try:
            if signatures_file.exists():
                with open(signatures_file, 'r', encoding='utf-8', errors='replace') as f:
                    self.signatures = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                self.logger.info(f"loaded {len(self.signatures)} signature entries")
            else:
                self.logger.warning(f"signatures file not found at {signatures_file}")
        except Exception as e:
            self.logger.error(f"error loading signatures: {str(e)}")
            
        try:
            if categories_file.exists():
                with open(categories_file, 'r', encoding='utf-8', errors='replace') as f:
                    self.categories = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                self.logger.info(f"loaded {len(self.categories)} category entries")
            else:
                self.logger.warning(f"categories file not found at {categories_file}")
        except Exception as e:
            self.logger.error(f"error loading categories: {str(e)}")
    
    async def analyze(self, page):
        self.logger.info("analyzing {page.title()} against signatures and categories")
        
        result = {
            "identified_applications": [],
            "default_credentials": [],
            "category": None
        }
        
        try:
            content = await page.content()
            page_title = await page.title()
            
            for sig in self.signatures:
                try:
                    sig_parts = sig.split('|')
                    if len(sig_parts) < 2:
                        continue
                        
                    patterns = sig_parts[0].split(';')
                    cred_info = sig_parts[1].strip()
                    
                    if all(pattern.lower() in content.lower() for pattern in patterns):
                        app_name = None
                        app_match = re.match(r'\((.*?)\)(.*)', cred_info)
                        if app_match:
                            app_name = app_match.group(1).strip()
                        else:
                            app_name = patterns[0]
                            
                        result["identified_applications"].append({
                            "name": app_name,
                            "patterns": patterns,
                            "credentials": cred_info
                        })
                        
                        if cred_info not in result["default_credentials"]:
                            result["default_credentials"].append(cred_info)
                except Exception as e:
                    self.logger.error(f"Error processing signature {sig}: {str(e)}")
            
            for cat in self.categories:
                try:
                    cat_parts = cat.split('|')
                    if len(cat_parts) < 2:
                        continue
                        
                    patterns = cat_parts[0].split(';')
                    cat_name = cat_parts[1].strip()
                    
                    if all(pattern.lower() in content.lower() for pattern in patterns):
                        result["category"] = cat_name
                        break  # Stop at the first matching category
                except Exception as e:
                    self.logger.error(f"Error processing category {cat}: {str(e)}")
            
            if not result["category"] and page_title:
                if '403 Forbidden' in page_title or '401 Unauthorized' in page_title:
                    result["category"] = 'unauth'
                elif ('Index of /' in page_title or 
                      'Directory Listing For /' in page_title or 
                      'Directory of /' in page_title):
                    result["category"] = 'dirlist'
                elif '404 Not Found' in page_title:
                    result["category"] = 'notfound'
            
            self.logger.info(f"Identified {len(result['identified_applications'])} applications, category: {result['category']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing signatures: {str(e)}")
            return result
