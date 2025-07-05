"""
UI Components module
Contains custom widgets and UI elements with rich content support
"""

from typing import Optional
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt

from models import ChatMessage
from rich_content import RichTextEdit, create_rich_content_widget


class ChatMessageWidget(QFrame):
    """Custom widget for displaying individual chat messages in a unified conversation style"""

    def __init__(self, message: ChatMessage, show_timestamps: bool = True,
                 font_size: int = 14, dark_mode: bool = True, parent=None):
        super().__init__(parent)
        self.message = message
        self.show_timestamps = show_timestamps
        self.font_size = font_size
        self.dark_mode = dark_mode
        self.setup_ui()
        self.setFrameStyle(QFrame.Shape.NoFrame)

    def setup_ui(self):
        """Setup the message widget UI with unified conversation style"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)

        # Determine alignment and styling based on role
        is_user = self.message.role == 'user'

        # Message container uses full available width
        is_user = self.message.role == 'user'

        # Message container
        message_container = QFrame()
        # Remove width constraint to use full available width
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(2)

        # Header with role and timestamp (for both user and assistant)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 4, 8, 0)

        if is_user:
            # User message header
            header_layout.addStretch()  # Push to right for user messages
            role_label = QLabel("👤 You")
            if self.dark_mode:
                role_label.setStyleSheet("""
                    QLabel {
                        color: #88C0D0;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)
            else:
                role_label.setStyleSheet("""
                    QLabel {
                        color: #2563eb;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)
        else:
            # Assistant message header
            model_info = f" ({self.message.model})" if self.message.model else ""
            role_label = QLabel(f"🤖 Assistant{model_info}")
            if self.dark_mode:
                role_label.setStyleSheet("""
                    QLabel {
                        color: #81A1C1;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)
            else:
                role_label.setStyleSheet("""
                    QLabel {
                        color: #059669;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)

        header_layout.addWidget(role_label)

        if not is_user:
            header_layout.addStretch()  # Push timestamp to right for assistant

        if self.show_timestamps and self.message.timestamp:
            timestamp_label = QLabel(self.message.timestamp.strftime("%H:%M"))
            if self.dark_mode:
                timestamp_label.setStyleSheet("color: #666; font-size: 10px;")
            else:
                timestamp_label.setStyleSheet("color: #9ca3af; font-size: 10px;")
            header_layout.addWidget(timestamp_label)

        message_layout.addLayout(header_layout)

        # Content bubble with rich content support
        content_area = create_rich_content_widget(self.message.content, 'markdown')

        # Let the content area expand to its full size without constraints
        content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # Style based on role
        if is_user:
            # User bubble styling - blue/right aligned
            if self.dark_mode:
                content_area.setStyleSheet(f"""
                    QTextBrowser {{
                        background-color: #5E81AC;
                        border: none;
                        border-radius: 15px;
                        padding: 10px 15px;
                        color: white;
                        font-size: {self.font_size}px;
                        line-height: 1.4;
                    }}
                """)
            else:
                content_area.setStyleSheet(f"""
                    QTextBrowser {{
                        background-color: #2563eb;
                        border: none;
                        border-radius: 15px;
                        padding: 10px 15px;
                        color: white;
                        font-size: {self.font_size}px;
                        line-height: 1.4;
                    }}
                """)
            message_layout.addWidget(content_area)
        else:
            # Assistant bubble styling - gray/left aligned
            if self.dark_mode:
                content_area.setStyleSheet(f"""
                    QTextBrowser {{
                        background-color: #3B4252;
                        border: 1px solid #4C566A;
                        border-radius: 15px;
                        padding: 10px 15px;
                        color: #000000;
                        font-size: {self.font_size}px;
                        line-height: 1.4;
                    }}
                """)
            else:
                content_area.setStyleSheet(f"""
                    QTextBrowser {{
                        background-color: #1a5d1a;
                        border: 1px solid #2d7d2d;
                        border-radius: 15px;
                        padding: 10px 15px;
                        color: #ffffff;
                        font-size: {self.font_size}px;
                        line-height: 1.4;
                    }}
                """)
            message_layout.addWidget(content_area)

        main_layout.addWidget(message_container)

        # No additional stretch needed - messages use full width

    def update_content(self, content: str):
        """Update the message content (for streaming)"""
        self.message.content = content
        # Find the rich content area and update it
        for child in self.findChildren(RichTextEdit):
            child.set_rich_content(content, 'markdown')
            # The adjustSize method in RichTextEdit will handle height automatically
            break
