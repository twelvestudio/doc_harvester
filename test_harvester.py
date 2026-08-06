import unittest
from harvester import DocHarvester

class TestDocHarvester(unittest.TestCase):

    def setUp(self):
        self.harvester = DocHarvester()

    def test_clean_and_extract(self):
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Documentation Page</title>
            <style>body { color: red; }</style>
            <script>console.log("script");</script>
        </head>
        <body>
            <nav class="navbar">Nav link 1 | Nav link 2</nav>
            <header>Header content</header>
            <main>
                <h1>Welcome to DocHarvester</h1>
                <p>This is the main body paragraph containing useful knowledge for LLMs.</p>
            </main>
            <aside class="sidebar">
                <div class="menu">
                    <span class="nav-item">Sidebar nested link</span>
                </div>
            </aside>
            <footer>Footer copyright 2026</footer>
        </body>
        </html>
        """
        title, cleaned_html = self.harvester.clean_and_extract(sample_html)
        
        self.assertEqual(title, "Test Documentation Page")
        self.assertIn("Welcome to DocHarvester", cleaned_html)
        self.assertIn("This is the main body paragraph", cleaned_html)
        
        # Verify unwanted tags were removed
        self.assertNotIn("console.log", cleaned_html)
        self.assertNotIn("color: red", cleaned_html)
        self.assertNotIn("Nav link 1", cleaned_html)
        self.assertNotIn("Footer copyright", cleaned_html)

    def test_convert_html_to_md(self):
        html_input = "<h1>Title</h1><p>Here is a <a href='https://example.com'>link</a> and <strong>bold text</strong>.</p>"
        markdown_output = self.harvester.convert_html_to_md(html_input)

        self.assertIn("# Title", markdown_output)
        self.assertIn("[link](https://example.com)", markdown_output)
        self.assertIn("**bold text**", markdown_output)

    def test_extract_sublinks(self):
        base_url = "https://docs.example.com/guide/index.html"
        sample_html = """
        <html>
        <body>
            <a href="/guide/page1.html">Page 1</a>
            <a href="page2.html">Page 2</a>
            <a href="https://docs.example.com/guide/page3.html#section">Page 3 Section</a>
            <a href="https://otherdomain.com/blog">External Domain</a>
            <a href="/guide/document.pdf">PDF File</a>
        </body>
        </html>
        """
        sublinks = self.harvester.extract_sublinks(base_url, sample_html)

        self.assertIn("https://docs.example.com/guide/page1.html", sublinks)
        self.assertIn("https://docs.example.com/guide/page2.html", sublinks)
        self.assertIn("https://docs.example.com/guide/page3.html", sublinks)
        
        # External domain and PDF files should be excluded
        self.assertNotIn("https://otherdomain.com/blog", sublinks)
        self.assertNotIn("https://docs.example.com/guide/document.pdf", sublinks)

    def test_build_combined_markdown(self):
        scraped_pages = [
            {
                "url": "https://example.com/page1",
                "title": "Page 1 Title",
                "markdown": "# Page 1 Content\nSome paragraph text.",
                "char_count": 50,
                "status": "Success"
            },
            {
                "url": "https://example.com/page2",
                "title": "Page 2 Title",
                "markdown": "# Page 2 Content\nAnother paragraph text.",
                "char_count": 55,
                "status": "Success"
            }
        ]
        
        combined_md = DocHarvester.build_combined_markdown(scraped_pages, document_title="Test Project Docs")
        
        self.assertIn("# 🌾 Test Project Docs", combined_md)
        self.assertIn("## 📋 Table of Contents", combined_md)
        self.assertIn("[Page 1 Title](#page-1)", combined_md)
        self.assertIn("[Page 2 Title](#page-2)", combined_md)
        self.assertIn("## 1. Page 1 Title", combined_md)
        self.assertIn("## 2. Page 2 Title", combined_md)

    def test_build_combined_markdown_without_toc_and_metadata(self):
        scraped_pages = [
            {
                "url": "https://example.com/page1",
                "title": "Page 1 Title",
                "markdown": "# Page 1 Content\nSome paragraph text.",
                "char_count": 50,
                "status": "Success"
            }
        ]
        
        combined_md = DocHarvester.build_combined_markdown(
            scraped_pages, 
            document_title="Clean Body Only Docs",
            include_toc=False,
            include_metadata=False
        )
        
        self.assertIn("# 🌾 Clean Body Only Docs", combined_md)
        self.assertNotIn("Table of Contents", combined_md)
        self.assertNotIn("Source URL", combined_md)
        self.assertIn("# Page 1 Content", combined_md)

    def test_check_crawlability_invalid_url(self):
        result = self.harvester.check_crawlability("https://invalid-non-existent-domain-12345.org")
        self.assertFalse(result["is_scrapable"])
        self.assertIn("접속 실패", result["reason"])

    def test_quick_scan_sublinks_structure(self):
        # Scan attempt structure test
        result = self.harvester.quick_scan_sublinks("https://invalid-non-existent-domain-12345.org")
        self.assertIn("total_count", result)
        self.assertIn("sublinks", result)
        self.assertIn("base_domain", result)
        self.assertEqual(result["total_count"], 0)

if __name__ == "__main__":
    unittest.main()
