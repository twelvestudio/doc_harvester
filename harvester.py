import re
import time
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Callable
from urllib.parse import urlparse, urljoin, urlunparse

import requests
from bs4 import BeautifulSoup
import html2text

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 DocHarvester/1.0"
)

# Unwanted elements to decompose
REMOVE_TAGS = [
    "script", "style", "nav", "footer", "header", "aside", 
    "iframe", "noscript", "form", "svg", "button", "input"
]

REMOVE_CLASSES = [
    "sidebar", "nav", "navbar", "footer", "header", "menu",
    "cookie-banner", "advertisement", "ad-container", "social-share"
]

MAIN_CONTENT_SELECTORS = [
    "main",
    "article",
    '[role="main"]',
    "#content",
    ".content",
    ".main-content",
    ".documentation",
    ".markdown-body",
    ".docs-content",
    "#main-content"
]

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".css", ".js", ".json", ".xml"
}


class DocHarvester:
    """Core Web Scraper & Markdown Converter for DocHarvester."""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, timeout: int = 15, delay: float = 0.5):
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch_page(self, url: str) -> Tuple[Optional[str], int, Optional[str]]:
        """Fetch raw HTML content from a target URL.
        
        Returns:
            (html_content, status_code, error_message)
        """
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # UTF-8 decoding priority
            if response.encoding is None or response.encoding.lower() == 'iso-8859-1':
                response.encoding = response.apparent_encoding or 'utf-8'
                
            return response.text, response.status_code, None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else 0
            return None, status_code, f"HTTP Error {status_code}: {e}"
        except requests.exceptions.Timeout:
            return None, 408, "Request timed out"
        except requests.exceptions.SSLError:
            return None, 0, "SSL Certificate Verification Failed"
        except requests.exceptions.RequestException as e:
            return None, 0, f"Network Error: {str(e)}"
        except Exception as e:
            return None, 0, f"Unexpected Error: {str(e)}"

    def check_crawlability(self, url: str) -> Dict:
        """Diagnose a target URL to check whether it is scrapable and return reason if failed.
        
        Returns:
            {
                "is_scrapable": bool,
                "status_code": int,
                "reason": str,
                "title": str,
                "content_type": str,
                "html_length": int
            }
        """
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            status_code = response.status_code
            content_type = response.headers.get("Content-Type", "").lower()

            # Check HTTP Status Code
            if status_code == 403 or status_code == 429:
                server_hdr = response.headers.get("Server", "").lower()
                is_cf = "cloudflare" in server_hdr or "cf-ray" in response.headers
                reason = "403/429 Forbidden (Cloudflare/WAF 보안 봇 방화벽에 의해 차단됨)" if is_cf else f"HTTP {status_code} Access Denied (접근 거부됨)"
                return {
                    "is_scrapable": False,
                    "status_code": status_code,
                    "reason": reason,
                    "title": "",
                    "content_type": content_type,
                    "html_length": 0
                }
            elif status_code == 404:
                return {
                    "is_scrapable": False,
                    "status_code": 404,
                    "reason": "404 Not Found (존재하지 않는 페이지 주소)",
                    "title": "",
                    "content_type": content_type,
                    "html_length": 0
                }
            elif status_code >= 400:
                return {
                    "is_scrapable": False,
                    "status_code": status_code,
                    "reason": f"HTTP {status_code} 오류 발생",
                    "title": "",
                    "content_type": content_type,
                    "html_length": 0
                }

            # Check Content Type
            if not any(t in content_type for t in ["html", "text", "xml"]):
                return {
                    "is_scrapable": False,
                    "status_code": status_code,
                    "reason": f"비 HTML 파일 형식입니다 ({content_type}). 본문 텍스트 스크래핑에 적합하지 않습니다.",
                    "title": "",
                    "content_type": content_type,
                    "html_length": len(response.content)
                }

            # Title extraction test
            soup = BeautifulSoup(response.text, "html.parser")
            title = "Untitled Page"
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.h1 and soup.h1.get_text():
                title = soup.h1.get_text().strip()

            return {
                "is_scrapable": True,
                "status_code": 200,
                "reason": "🟢 정상 수집 가능 (HTTP 200 OK)",
                "title": title,
                "content_type": content_type,
                "html_length": len(response.text)
            }

        except requests.exceptions.Timeout:
            return {
                "is_scrapable": False,
                "status_code": 408,
                "reason": "요청 시간 초과 (서버 응답 지연 또는 방화벽 차단)",
                "title": "",
                "content_type": "",
                "html_length": 0
            }
        except requests.exceptions.SSLError:
            return {
                "is_scrapable": False,
                "status_code": 0,
                "reason": "SSL/TLS 보안 인증서 오류 (해당 사이트의 보안 설정 문제)",
                "title": "",
                "content_type": "",
                "html_length": 0
            }
        except requests.exceptions.RequestException as e:
            return {
                "is_scrapable": False,
                "status_code": 0,
                "reason": f"네트워크 접속 실패: {str(e)}",
                "title": "",
                "content_type": "",
                "html_length": 0
            }
        except Exception as e:
            return {
                "is_scrapable": False,
                "status_code": 0,
                "reason": f"알 수 없는 오류: {str(e)}",
                "title": "",
                "content_type": "",
                "html_length": 0
            }

    def quick_scan_sublinks(self, base_url: str) -> Dict:
        """Scan a base URL to discover available internal sublinks count before full crawling.
        
        Returns:
            {
                "total_count": int,
                "sublinks": List[str],
                "base_domain": str,
                "status_code": int,
                "error": Optional[str]
            }
        """
        base_url = base_url.strip()
        if not base_url.startswith(("http://", "https://")):
            base_url = "https://" + base_url

        html, status_code, error = self.fetch_page(base_url)
        if error or not html:
            return {
                "total_count": 0,
                "sublinks": [],
                "base_domain": urlparse(base_url).netloc,
                "status_code": status_code,
                "error": error
            }

        sublinks = self.extract_sublinks(base_url, html)
        return {
            "total_count": len(sublinks),
            "sublinks": sublinks,
            "base_domain": urlparse(base_url).netloc,
            "status_code": status_code,
            "error": None
        }

    def clean_and_extract(self, html: str, base_url: str = "") -> Tuple[str, str]:
        """Clean unwanted tags from HTML and extract main body content & page title.
        
        Returns:
            (page_title, cleaned_html_string)
        """
        soup = BeautifulSoup(html, "html.parser")

        # 1. Extract Page Title
        title = "Untitled Page"
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.h1 and soup.h1.get_text():
            title = soup.h1.get_text().strip()

        # 2. Decompose unwanted tags
        for tag_name in REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Decompose elements with unwanted classes safely
        for tag in list(soup.find_all(True)):
            if not hasattr(tag, "attrs") or tag.attrs is None:
                continue
            classes = tag.attrs.get("class")
            if not classes:
                continue

            if isinstance(classes, list):
                classes_str = " ".join(classes).lower()
            else:
                classes_str = str(classes).lower()
            
            if any(rem in classes_str for rem in REMOVE_CLASSES):
                tag.decompose()

        # 3. Locate Main Content Area
        main_content = None
        for selector in MAIN_CONTENT_SELECTORS:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 50:
                main_content = element
                break

        if not main_content:
            main_content = soup.body or soup

        return title, str(main_content)

    def convert_html_to_md(self, html_str: str, base_url: str = "") -> str:
        """Convert HTML string to clean Markdown text using html2text."""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.ignore_tables = False
        h.body_width = 0  # Do not wrap lines automatically
        h.protect_links = False

        if base_url:
            h.baseurl = base_url

        markdown_text = h.handle(html_str)
        
        # Clean up excessive blank lines (more than 2 consecutive newlines)
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        return markdown_text.strip()

    def extract_sublinks(self, base_url: str, html: str) -> List[str]:
        """Extract all internal links within the same domain and sub-path prefix."""
        soup = BeautifulSoup(html, "html.parser")
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc.lower()
        
        # Normalize base path to keep sub-path restrictiveness
        base_path = parsed_base.path
        if not base_path.endswith('/'):
            # e.g., /docs/guide -> /docs/
            base_dir = base_path.rsplit('/', 1)[0] + '/'
        else:
            base_dir = base_path

        valid_links = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)

            # Check domain match
            if parsed_url.netloc.lower() != base_domain:
                continue

            # Check scheme
            if parsed_url.scheme not in ("http", "https"):
                continue

            # Check file extensions
            path_lower = parsed_url.path.lower()
            if any(path_lower.endswith(ext) for ext in IGNORED_EXTENSIONS):
                continue

            # Remove fragment/query string for URL normalization
            clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
            
            # Make sure clean_url is not just trailing slash difference
            clean_url = clean_url.rstrip('/')
            
            valid_links.add(clean_url)

        return sorted(list(valid_links))

    def harvest_single(self, url: str) -> Dict:
        """Harvest a single URL and return structured result dictionary."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        html, status_code, error = self.fetch_page(url)
        if error or not html:
            return {
                "url": url,
                "title": "Failed Page",
                "markdown": "",
                "char_count": 0,
                "status": "Failed",
                "status_code": status_code,
                "error": error
            }

        title, cleaned_html = self.clean_and_extract(html, base_url=url)
        markdown = self.convert_html_to_md(cleaned_html, base_url=url)

        return {
            "url": url,
            "title": title,
            "markdown": markdown,
            "char_count": len(markdown),
            "status": "Success",
            "status_code": status_code,
            "error": None
        }

    def harvest_multi(
        self, 
        urls: List[str], 
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict]:
        """Harvest a list of URLs sequentially."""
        results = []
        total = len(urls)

        for idx, url in enumerate(urls, 1):
            if progress_callback:
                progress_callback(idx, total, f"Scraping ({idx}/{total}): {url}")

            res = self.harvest_single(url)
            results.append(res)
            time.sleep(self.delay)

        return results

    def harvest_depth(
        self, 
        start_url: str, 
        max_depth: int = 1, 
        max_pages: int = 20,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict]:
        """Harvest starting from start_url and explore sublinks up to max_depth using BFS."""
        start_url = start_url.strip()
        if not start_url.startswith(("http://", "https://")):
            start_url = "https://" + start_url

        start_clean = urlunparse(urlparse(start_url)._replace(fragment="")).rstrip('/')
        
        visited: Set[str] = set()
        results: List[Dict] = []
        queue = deque([(start_clean, 0)]) # (url, current_depth)
        visited.add(start_clean)

        processed_count = 0

        while queue and processed_count < max_pages:
            current_url, current_depth = queue.popleft()
            processed_count += 1

            if progress_callback:
                progress_callback(
                    processed_count, 
                    max_pages, 
                    f"[Depth {current_depth}] Scraping ({processed_count}/{max_pages}): {current_url}"
                )

            # Fetch page
            html, status_code, error = self.fetch_page(current_url)
            if error or not html:
                results.append({
                    "url": current_url,
                    "title": "Failed Page",
                    "markdown": "",
                    "char_count": 0,
                    "status": "Failed",
                    "status_code": status_code,
                    "error": error,
                    "depth": current_depth
                })
                time.sleep(self.delay)
                continue

            title, cleaned_html = self.clean_and_extract(html, base_url=current_url)
            markdown = self.convert_html_to_md(cleaned_html, base_url=current_url)

            results.append({
                "url": current_url,
                "title": title,
                "markdown": markdown,
                "char_count": len(markdown),
                "status": "Success",
                "status_code": status_code,
                "error": None,
                "depth": current_depth
            })

            # Find sublinks if depth allows
            if current_depth < max_depth:
                sublinks = self.extract_sublinks(current_url, html)
                for link in sublinks:
                    if link not in visited and len(visited) < max_pages * 3:
                        visited.add(link)
                        queue.append((link, current_depth + 1))

            time.sleep(self.delay)

        return results

    @staticmethod
    def build_combined_markdown(scraped_pages: List[Dict], document_title: str = "DocHarvester Collection") -> str:
        """Combine multiple scraped page results into a single structured Markdown file."""
        successful_pages = [p for p in scraped_pages if p["status"] == "Success"]
        
        if not successful_pages:
            return f"# {document_title}\n\n*No pages were successfully harvested.*"

        lines = [
            f"# 🌾 {document_title}",
            "",
            "> Created by DocHarvester - Web-to-Markdown Knowledge Builder",
            f"> Total Harvested Pages: {len(successful_pages)}",
            "",
            "## 📋 Table of Contents",
            ""
        ]

        # Table of contents
        for idx, page in enumerate(successful_pages, 1):
            clean_title = page["title"].replace("[", "\\[").replace("]", "\\]")
            lines.append(f"{idx}. [{clean_title}](#page-{idx})")

        lines.append("\n---\n")

        # Page sections
        for idx, page in enumerate(successful_pages, 1):
            lines.append(f"<a id='page-{idx}'></a>")
            lines.append(f"## {idx}. {page['title']}")
            lines.append(f"**Source URL**: [{page['url']}]({page['url']})")
            if "depth" in page:
                lines.append(f"**Crawl Depth**: {page['depth']}")
            lines.append("")
            lines.append(page["markdown"])
            lines.append("\n---\n")

        return "\n".join(lines)
