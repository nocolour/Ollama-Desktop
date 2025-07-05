"""
Rich Content Module
Provides rich text rendering and markdown support for the Ollama Desktop chat interface.
"""

import re
from PySide6.QtWidgets import QTextBrowser
from PySide6.QtCore import Qt


class RichContentRenderer:
    """Handles rendering of rich content including markdown to HTML conversion"""

    @staticmethod
    def render_markdown_to_html(markdown_text: str) -> str:
        """Convert markdown to HTML for rich rendering"""
        html = markdown_text

        # Headers
        html = re.sub(r'^#{3}\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{2}\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{1}\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', html)
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        html = re.sub(r'_([^_]+)_', r'<em>\1</em>', html)

        # Strikethrough
        html = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', html)

        # Code blocks
        html = re.sub(r'```(\w+)?\n(.*?)\n```',
                     lambda m: f'<pre><code class="{m.group(1) or ""}">{m.group(2)}</code></pre>',
                     html, flags=re.DOTALL)

        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

        # Lists
        html = re.sub(r'^[\s]*[-*+]\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^[\s]*\d+\.\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Blockquotes
        html = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # Line breaks
        html = html.replace('\n', '<br>')

        return html


class RichTextEdit(QTextBrowser):
    """Read-only text widget for chat messages with rich content and no scroll bars"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWordWrapMode(self.wordWrapMode())
        self.document().documentLayout().documentSizeChanged.connect(self.adjustSize)
        self.setup_styles()

    def adjustSize(self):
        """Resize widget to fit content height"""
        doc_size = self.document().size()
        self.setFixedHeight(max(50, int(doc_size.height() + 20)))

    def setup_styles(self):
        """Setup styles with complete scroll bar removal"""
        self.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                padding: 10px;
                color: #ECEFF4;
                font-size: 14px;
                line-height: 1.4;
            }
            QTextBrowser QScrollBar, QTextBrowser QScrollBar::handle,
            QTextBrowser QScrollBar::add-line, QTextBrowser QScrollBar::sub-line,
            QTextBrowser QScrollBar::add-page, QTextBrowser QScrollBar::sub-page {
                width: 0px; height: 0px; background: transparent; border: none;
            }
        """)

    def set_rich_content(self, content: str, content_type: str = 'markdown'):
        """Set and render content, then resize widget"""
        if content_type == 'markdown':
            html_content = RichContentRenderer.render_markdown_to_html(content)
            self.setHtml(self._wrap_in_css(html_content))
        elif content_type == 'html':
            self.setHtml(self._wrap_in_css(content))
        else:
            self.setPlainText(content)
        self.adjustSize()

    def _wrap_in_css(self, html_content: str) -> str:
        """Wrap HTML content with CSS for consistent styling"""
        css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: #ECEFF4; background: transparent; line-height: 1.6; margin: 0; padding: 0;
            }
            h1, h2, h3 { color: #8FBCBB; margin: 10px 0; }
            h1 { font-size: 1.5em; } h2 { font-size: 1.3em; } h3 { font-size: 1.1em; }
            strong { color: #FFF; font-weight: bold; }
            em { color: #E5E9F0; font-style: italic; }
            code {
                background: #3C4048; color: #E6E6E6; padding: 2px 4px; border-radius: 3px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
            }
            pre {
                background: #282C34; color: #ABB2BF; padding: 12px; border-radius: 8px;
                border-left: 4px solid #5E81AC; margin: 10px 0;
                white-space: pre-wrap; word-wrap: break-word;
            }
            pre code { background: transparent; padding: 0; color: inherit; }
            blockquote {
                border-left: 4px solid #5E81AC; padding-left: 12px; margin: 10px 0;
                color: #D8DEE9; background: #2D3139; border-radius: 0 4px 4px 0;
            }
            ul, ol { padding-left: 20px; margin: 10px 0; }
            li { margin: 4px 0; color: #E5E9F0; }
            a { color: #88C0D0; text-decoration: none; }
            a:hover { color: #8FBCBB; text-decoration: underline; }
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            th, td { border: 1px solid #4C566A; padding: 8px; text-align: left; }
            th { background: #3B4252; color: #8FBCBB; font-weight: bold; }
        </style>
        """
        return f"<html><head>{css}</head><body>{html_content}</body></html>"


def create_rich_content_widget(content: str, content_type: str = 'markdown') -> RichTextEdit:
    """Create a rich content widget sized to its content"""
    widget = RichTextEdit()
    widget.set_rich_content(content, content_type)
    widget.adjustSize()
    return widget
