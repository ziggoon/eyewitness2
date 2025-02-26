import logging
from pathlib import Path
import jinja2
import base64
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger("eyewitness2.reporter")
        
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def generate_reports(self, results, output_dir):
        self.logger.info(f"generating HTML reports in {output_dir}")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "total_urls": len(results),
            "errors": 0,
            "categories": {},
            "apps_identified": {},
            "default_creds_found": 0,
            "reports": []
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                stats["errors"] += 1
                continue
                
            report_filename = f"report_{i}.html"
            report_path = output_dir / report_filename
            
            if "screenshot" in result and Path(result["screenshot"]).exists():
                try:
                    with open(result["screenshot"], "rb") as f:
                        img_data = base64.b64encode(f.read()).decode('utf-8')
                        result["screenshot_data"] = img_data
                except Exception as e:
                    self.logger.error(f"error processing screenshot: {str(e)}")
                    result["screenshot_data"] = None
            
            report_stats = {
                "url": result["url"],
                "timestamp": result["timestamp"],
                "report_url": report_filename,
                "title": result.get("headers", {}).get("metadata", {}).get("title", "Unknown"),
                "category": result.get("signatures", {}).get("category", "Unknown"),
                "apps_count": len(result.get("signatures", {}).get("identified_applications", [])),
                "has_default_creds": len(result.get("signatures", {}).get("default_credentials", [])) > 0,
                "screenshot": result.get("screenshot", None),
                "error": result.get("error", None)
            }
            
            stats["reports"].append(report_stats)
            
            category = report_stats["category"] or "Unknown"
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1
            
            for app in result.get("signatures", {}).get("identified_applications", []):
                app_name = app.get("name", "Unknown")
                if app_name not in stats["apps_identified"]:
                    stats["apps_identified"][app_name] = 0
                stats["apps_identified"][app_name] += 1
            
            if report_stats["has_default_creds"]:
                stats["default_creds_found"] += 1
            
            self._generate_single_report(result, report_path)
            
        self._generate_index_page(stats, output_dir / "index.html")
        
        self.logger.info(f"generated reports for {len(stats['reports'])} URLs")
        return output_dir / "index.html"
    
    def _generate_single_report(self, result, output_path):
        try:
            template = self._get_template("report_template.html")
            
            html_content = template.render(
                result=result,
                title=f"Report - {result['url']}"
            )
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            self.logger.info(f"report generated successfully at {output_path}")
            
        except Exception as e:
            self.logger.error(f"error generating single report: {str(e)}")
    
    def _generate_index_page(self, stats, output_path):
        try:
            template = self._get_template("index_template.html")
            
            html_content = template.render(
                stats=stats,
                title="Eyewitness2 Dashboard",
                timestamp=datetime.now().isoformat()
            )
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            self.logger.info(f"index page generated successfully at {output_path}")
            
        except Exception as e:
            self.logger.error(f"error generating index page: {str(e)}")
    
    def _get_template(self, template_name):
        try:
            return self.jinja_env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            if template_name == "report_template.html":
                self._create_default_report_template()
            elif template_name == "index_template.html":
                self._create_default_index_template()
            return self.jinja_env.get_template(template_name)

    def _create_default_report_template(self):
        self.logger.info("creating default report template")
        
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        template_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }}</title>
        <style>
            :root {
                --primary-color: #4361ee;
                --secondary-color: #3f37c9;
                --success-color: #4cc9f0;
                --danger-color: #f72585;
                --warning-color: #f8961e;
                --text-color: #212529;
                --light-gray: #f8f9fa;
                --border-color: #dee2e6;
                --box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                color: var(--text-color);
                background-color: #f9fafb;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .site-report {
                margin-bottom: 3rem;
                border-radius: 10px;
                padding: 2rem;
                box-shadow: var(--box-shadow);
                background-color: white;
                overflow: hidden;
            }
            
            h1, h2, h3, h4 {
                color: var(--secondary-color);
                font-weight: 600;
            }
            
            h1 {
                font-size: 2rem;
                margin-top: 0;
            }
            
            h2 {
                font-size: 1.6rem;
                border-bottom: 2px solid var(--light-gray);
                padding-bottom: 0.8rem;
                margin-top: 2rem;
            }
            
            h3 {
                font-size: 1.3rem;
                margin-top: 1.5rem;
            }
            
            .screenshot {
                max-width: 100%;
                height: auto;
                border-radius: 6px;
                box-shadow: var(--box-shadow);
                margin: 1.5rem 0;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1.5rem 0;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            
            th, td {
                padding: 0.8rem 1rem;
                border: 1px solid var(--border-color);
                text-align: left;
            }
            
            th {
                background-color: var(--light-gray);
                font-weight: 600;
            }
            
            tr:nth-child(even) {
                background-color: rgba(0,0,0,0.01);
            }
            
            tr:hover {
                background-color: rgba(67, 97, 238, 0.05);
            }
            
            .missing {
                color: var(--danger-color);
                font-weight: 500;
            }
            
            .present {
                color: #2ecc71;
                font-weight: 500;
            }
            
            .error {
                background-color: #fff5f7;
                padding: 1.5rem;
                border-radius: 6px;
                border-left: 4px solid var(--danger-color);
                margin: 1.5rem 0;
            }
            
            .alert {
                padding: 1.2rem;
                margin: 1.5rem 0;
                border-radius: 6px;
                border-left: 4px solid transparent;
            }
            
            .alert-warning {
                color: #7d5700;
                background-color: #fff8e6;
                border-color: var(--warning-color);
            }
            
            .navigation {
                margin-bottom: 1.5rem;
            }
            
            .navigation a {
                display: inline-block;
                text-decoration: none;
                color: var(--primary-color);
                font-weight: 500;
                padding: 0.5rem 0;
                transition: all 0.2s;
            }
            
            .navigation a:hover {
                color: var(--secondary-color);
                transform: translateX(-3px);
            }
            
            footer {
                text-align: center;
                margin-top: 3rem;
                padding: 1.5rem;
                color: #6c757d;
                font-size: 0.875rem;
                border-top: 1px solid var(--border-color);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="navigation">
                <a href="index.html">&larr; Back to Dashboard</a>
            </div>
            
            <h1>{{ title }}</h1>
            
            <div class="site-report">
                {% if result is mapping %}
                    <h2>{{ result.url }}</h2>
                    <p>Scanned at: {{ result.timestamp }}</p>
                    
                    {% if result.error is defined %}
                        <div class="error">
                            <h3>Error</h3>
                            <p>{{ result.error }}</p>
                        </div>
                    {% else %}
                        {% if result.screenshot_data %}
                            <h3>Screenshot</h3>
                            <img src="data:image/png;base64,{{ result.screenshot_data }}" 
                                 alt="Screenshot of {{ result.url }}" 
                                 class="screenshot">
                        {% endif %}
                        
                        {% if result.signatures %}
                            <h3>Website Identification</h3>
                            
                            {% if result.signatures.category %}
                                <p><strong>Category:</strong> {{ result.signatures.category }}</p>
                            {% endif %}
                            
                            {% if result.signatures.identified_applications %}
                                <h4>Identified Applications</h4>
                                <table>
                                    <tr>
                                        <th>Application</th>
                                        <th>Default Credentials</th>
                                    </tr>
                                    {% for app in result.signatures.identified_applications %}
                                        <tr>
                                            <td>{{ app.name }}</td>
                                            <td>{{ app.credentials }}</td>
                                        </tr>
                                    {% endfor %}
                                </table>
                            {% endif %}
                            
                            {% if result.signatures.default_credentials %}
                                <div class="alert alert-warning">
                                    <h4>Default Credentials</h4>
                                    <p><strong>Warning:</strong> The following default credentials were identified:</p>
                                    <ul>
                                        {% for cred in result.signatures.default_credentials %}
                                            <li>{{ cred }}</li>
                                        {% endfor %}
                                    </ul>
                                    <p>These should be changed immediately if not already done.</p>
                                </div>
                            {% endif %}
                        {% endif %}
                        
                        {% if result.headers %}
                            <h3>HTTP Headers</h3>
                            <table>
                                <tr>
                                    <th>Header</th>
                                    <th>Value</th>
                                </tr>
                                {% for key, value in result.headers.http_headers.items() %}
                                    <tr>
                                        <td>{{ key }}</td>
                                        <td>{{ value }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                            
                            <h3>Security Headers</h3>
                            <table>
                                <tr>
                                    <th>Header</th>
                                    <th>Status</th>
                                    <th>Value</th>
                                </tr>
                                {% for key, value in result.headers.security_headers.items() %}
                                    <tr>
                                        <td>{{ key }}</td>
                                        <td>
                                            {% if value == "Not set" %}
                                                <span class="missing">Missing</span>
                                            {% else %}
                                                <span class="present">Present</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ value }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                            
                            <h3>Metadata</h3>
                            <p><strong>Title:</strong> {{ result.headers.metadata.title }}</p>
                            
                            <h4>Meta Tags</h4>
                            <table>
                                <tr>
                                    <th>Name</th>
                                    <th>Content</th>
                                </tr>
                                {% for key, value in result.headers.metadata.meta_tags.items() %}
                                    <tr>
                                        <td>{{ key }}</td>
                                        <td>{{ value }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                            
                        {% endif %}
                    {% endif %}
                {% else %}
                    <div class="error">
                        <h3>Error Processing URL</h3>
                        <p>{{ result }}</p>
                    </div>
                {% endif %}
            </div>
            
            <footer>
                <p>Report generated at {{ result.timestamp if result is mapping else now() }}</p>
            </footer>
        </div>
    </body>
    </html>"""
        
        template_path = template_dir / "report_template.html"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)


    def _create_default_index_template(self):
        """Create a default HTML template for the index/dashboard page"""
        self.logger.info("Creating default index template")
        
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        template_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }}</title>
        <style>
            :root {
                --primary-color: #4361ee;
                --secondary-color: #3f37c9;
                --success-color: #38b000;
                --danger-color: #f72585;
                --warning-color: #fb8500;
                --text-color: #212529;
                --light-gray: #f8f9fa;
                --border-color: #dee2e6;
                --bg-color: #f9fafb;
                --box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                color: var(--text-color);
                background-color: var(--bg-color);
            }
            
            .container {
                max-width: 1300px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            header {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                padding: 2rem;
                margin-bottom: 2rem;
                border-radius: 10px;
                box-shadow: var(--box-shadow);
            }
            
            h1, h2, h3 {
                color: var(--secondary-color);
                font-weight: 600;
            }
            
            header h1 {
                color: white;
                margin: 0;
                font-size: 2.2rem;
            }
            
            header p {
                margin: 0.5rem 0 0;
                opacity: 0.9;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: var(--box-shadow);
                text-align: center;
                transition: transform 0.2s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-card h3 {
                margin-top: 0;
                color: #6c757d;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .stat-card .number {
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--secondary-color);
                margin: 0.8rem 0;
                line-height: 1;
            }
            
            .stat-card .number.danger {
                color: var(--danger-color);
            }
            
            .stat-card .number.success {
                color: var(--success-color);
            }
            
            .stat-card .number.warning {
                color: var(--warning-color);
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1.5rem 0;
                background: white;
                box-shadow: var(--box-shadow);
                border-radius: 10px;
                overflow: hidden;
            }
            
            th, td {
                padding: 1rem 1.2rem;
                text-align: left;
                border-bottom: 1px solid var(--border-color);
            }
            
            th {
                background-color: var(--light-gray);
                font-weight: 600;
                color: #495057;
                position: sticky;
                top: 0;
            }
            
            tr:hover {
                background-color: rgba(67, 97, 238, 0.03);
            }
            
            tr:last-child td {
                border-bottom: none;
            }
            
            .url-col {
                max-width: 300px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
            .thumbnail {
                width: 100px;
                height: 60px;
                object-fit: cover;
                border-radius: 4px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .filters {
                display: flex;
                justify-content: space-between;
                margin-bottom: 1.5rem;
                flex-wrap: wrap;
                gap: 1rem;
            }
            
            .filters input {
                padding: 0.75rem 1rem;
                border: 1px solid var(--border-color);
                border-radius: 6px;
                width: 300px;
                font-family: inherit;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: all 0.2s;
            }
            
            .filters input:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
            }
            
            .filters select {
                padding: 0.75rem 1rem;
                border: 1px solid var(--border-color);
                border-radius: 6px;
                background-color: white;
                font-family: inherit;
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23495057' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 1rem center;
                padding-right: 2.5rem;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: all 0.2s;
            }
            
            .filters select:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
            }
            
            .chart-container {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: var(--box-shadow);
                margin-bottom: 2rem;
            }
            
            .chart-container h2 {
                margin-top: 0;
                font-size: 1.5rem;
            }

                    footer {
                text-align: center;
                margin-top: 3rem;
                padding: 1.5rem;
                color: #6c757d;
                font-size: 0.9rem;
                border-top: 1px solid var(--border-color);
            }
            
            .badge {
                display: inline-block;
                padding: 0.35em 0.65em;
                font-size: 0.75em;
                font-weight: 600;
                line-height: 1;
                color: #fff;
                text-align: center;
                white-space: nowrap;
                vertical-align: baseline;
                border-radius: 50rem;
            }
            
            .badge-warning {
                background-color: var(--warning-color);
            }
            
            .badge-danger {
                background-color: var(--danger-color);
            }
            
            .badge-success {
                background-color: var(--success-color);
            }
            
            .badge-info {
                background-color: var(--primary-color);
            }
            
            a.btn {
                display: inline-block;
                text-decoration: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-weight: 500;
                transition: all 0.2s;
                color: white;
                background-color: var(--primary-color);
            }
            
            a.btn:hover {
                background-color: var(--secondary-color);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .container {
                    padding: 1rem;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
                
                .filters {
                    flex-direction: column;
                }
                
                .filters input, .filters select {
                    width: 100%;
                }
                
                .stat-card .number {
                    font-size: 2rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{{ title }}</h1>
                <p>Report generated at {{ timestamp }}</p>
            </header>
            
            <div class="dashboard-grid">
                <div class="stat-card">
                    <h3>Total URLs Scanned</h3>
                    <div class="number">{{ stats.total_urls }}</div>
                </div>
                
                <div class="stat-card">
                    <h3>Errors</h3>
                    <div class="number {% if stats.errors > 0 %}danger{% else %}success{% endif %}">
                        {{ stats.errors }}
                    </div>
                </div>
                
                <div class="stat-card">
                    <h3>Applications Identified</h3>
                    <div class="number">{{ stats.apps_identified|length }}</div>
                </div>
                
                <div class="stat-card">
                    <h3>Default Credentials Found</h3>
                    <div class="number {% if stats.default_creds_found > 0 %}warning{% else %}success{% endif %}">
                        {{ stats.default_creds_found }}
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>Categories Overview</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                    {% for category, count in stats.categories.items() %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>{{ count }}</td>
                        <td>{{ (count / stats.total_urls * 100)|round(1) }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            {% if stats.apps_identified %}
            <div class="chart-container">
                <h2>Identified Applications</h2>
                <table>
                    <tr>
                        <th>Application</th>
                        <th>Count</th>
                    </tr>
                    {% for app, count in stats.apps_identified.items() %}
                    <tr>
                        <td>{{ app }}</td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% endif %}
            
            <h2>Scan Results</h2>
            
            <div class="filters">
                <input type="text" id="urlFilter" placeholder="Filter by URL...">
                <select id="categoryFilter">
                    <option value="">All Categories</option>
                    {% for category in stats.categories.keys() %}
                    <option value="{{ category }}">{{ category }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <table id="resultsTable">
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Title</th>
                        <th>Category</th>
                        <th>Apps</th>
                        <th>Default Creds</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for report in stats.reports %}
                    <tr data-category="{{ report.category }}">
                        <td class="url-col">{{ report.url }}</td>
                        <td>{{ report.title }}</td>
                        <td>{{ report.category }}</td>
                        <td>{{ report.apps_count }}</td>
                        <td>
                            {% if report.has_default_creds %}
                            <span class="badge badge-warning">Yes</span>
                            {% else %}
                            <span>No</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if report.error %}
                            <span class="badge badge-danger">Error</span>
                            {% else %}
                            <span class="badge badge-success">Success</span>
                            {% endif %}
                        </td>
                        <td>
                            <a href="{{ report.report_url }}" class="btn">View Report</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <footer>
                <p>Eyewitness2</p>
            </footer>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const urlFilter = document.getElementById('urlFilter');
                const categoryFilter = document.getElementById('categoryFilter');
                const table = document.getElementById('resultsTable');
                const rows = table.querySelectorAll('tbody tr');
                
                function applyFilters() {
                    const urlValue = urlFilter.value.toLowerCase();
                    const categoryValue = categoryFilter.value;
                    
                    rows.forEach(row => {
                        const url = row.querySelector('td:first-child').textContent.toLowerCase();
                        const category = row.getAttribute('data-category');
                        
                        const urlMatch = url.includes(urlValue);
                        const categoryMatch = !categoryValue || category === categoryValue;
                        
                        if (urlMatch && categoryMatch) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                }
                
                urlFilter.addEventListener('input', applyFilters);
                categoryFilter.addEventListener('change', applyFilters);
                
                urlFilter.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        urlFilter.value = '';
                        applyFilters();
                    }
                });
            });
        </script>
    </body>
    </html>"""
        
        template_path = template_dir / "index_template.html"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)
