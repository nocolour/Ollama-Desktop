"""
Data models for Ollama Desktop Application
Contains all data structures and message formats
"""

import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ChatMessage:
    """Represents a chat message with role, content, and metadata"""
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: Optional[datetime.datetime] = None
    model: str = ""
    tokens: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()


@dataclass
class ModelInfo:
    """Information about an available Ollama model"""
    name: str
    size: str
    modified: str
    digest: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class APIConfig:
    """Ollama API configuration"""
    host: str = "localhost"
    port: int = 11434
    timeout: int = 60

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass
class ModelConfig:
    """Model generation parameters"""
    temperature: float = 0.7
    top_p: float = 0.9
    num_predict: int = 2048
    num_ctx: int = 4096
    system_prompt: str = ""


@dataclass
class UIConfig:
    """User interface configuration"""
    dark_mode: bool = True
    auto_scroll: bool = True
    show_timestamps: bool = True
    font_size: int = 14


@dataclass
class AvailableModel:
    """Model available for download"""
    name: str
    description: str
    size: str
    category: str
