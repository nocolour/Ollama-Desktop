"""
Workers module
Contains QThread worker classes for background operations
"""

import ollama
from typing import List, Dict, Any
from PySide6.QtCore import QThread, Signal

from models import ChatMessage, ModelInfo, APIConfig, ModelConfig


class OllamaWorker(QThread):
    """Worker thread for Ollama chat operations"""

    message_chunk = Signal(str)
    message_complete = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, model: str, messages: List[ChatMessage],
                 api_config: APIConfig, model_config: ModelConfig, options: Dict[str, Any]):
        super().__init__()
        self.model = model
        self.messages = messages
        self.api_config = api_config
        self.model_config = model_config
        self.options = options
        self.is_cancelled = False
        self.full_response = ""
    def run(self):
        """Execute the chat request"""
        try:
            if self.is_cancelled:
                return

            # Create client with remote server support
            client = ollama.Client(host=self.api_config.base_url)

            # Convert messages to ollama format
            ollama_messages = []
            
            # Convert messages to ollama format
            ollama_messages = []
            
            # Convert messages to ollama format
            ollama_messages = []
            
            # Add system prompt if configured
            system_prompt = self.model_config.system_prompt.strip()
            if system_prompt:
                ollama_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            # Add chat messages
            for msg in self.messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Prepare model options from config
            model_options = {
                "temperature": self.model_config.temperature,
                "top_p": self.model_config.top_p,
                "num_predict": self.model_config.num_predict,
                "num_ctx": self.model_config.num_ctx,
                **self.options  # Allow override from passed options
            }

            # Stream the response
            response = client.chat(
                model=self.model,
                messages=ollama_messages,
                stream=True,
                options=model_options
            )

            for chunk in response:
                if self.is_cancelled:
                    break

                content = chunk.get('message', {}).get('content', '')
                if content:
                    self.full_response += content
                    self.message_chunk.emit(content)

                if chunk.get('done', False):
                    self.message_complete.emit(self.full_response)
                    break

        except Exception as e:
            if not self.is_cancelled:
                self.error_occurred.emit(str(e))

    def cancel(self):
        """Cancel the current operation"""
        self.is_cancelled = True


class ModelManager(QThread):
    """Worker thread for model management operations with remote server support"""

    models_loaded = Signal(list)
    model_pulled = Signal(str)
    pull_progress = Signal(int, str)
    error_occurred = Signal(str)

    def __init__(self, api_config: APIConfig):
        super().__init__()
        self.api_config = api_config
        self.operation = None
        self.model_name = None
        self.is_cancelled = False

    def update_api_config(self, config: APIConfig):
        """Update API configuration for remote server"""
        self.api_config = config

    def load_models(self):
        """Start loading available models from remote server"""
        self.operation = "load"
        self.is_cancelled = False
        self.start()

    def pull_model(self, model_name: str):
        """Start downloading a model to remote server"""
        self.operation = "pull"
        self.model_name = model_name
        self.is_cancelled = False
        self.start()

    def cancel_operation(self):
        """Cancel current operation"""
        self.is_cancelled = True

    def run(self):
        """Execute the requested operation"""
        try:
            if self.operation == "load":
                self._load_models()
            elif self.operation == "pull":
                self._pull_model()
        except Exception as e:
            if not self.is_cancelled:
                self.error_occurred.emit(f"Remote server error: {str(e)}")

    def _load_models(self):
        """Load available models from remote Ollama server"""
        try:
            client = ollama.Client(host=self.api_config.base_url)
            response = client.list()
            model_list = []

            # Handle both old dict format and new Model object format
            models_data = response.get('models', []) if isinstance(response, dict) else response.models

            for model in models_data:
                if self.is_cancelled:
                    return

                # Handle both dict and Model object formats
                if hasattr(model, 'model'):  # New Model object format
                    name = str(model.model) if model.model else "Unknown"
                    size = getattr(model, 'size', 0)
                    modified = str(getattr(model, 'modified_at', ''))
                    digest = str(getattr(model, 'digest', ''))
                    details = getattr(model, 'details', {})
                else:  # Old dict format (fallback)
                    name = str(model.get('name', 'Unknown'))
                    size = model.get('size', 0)
                    modified = str(model.get('modified_at', ''))
                    digest = str(model.get('digest', ''))
                    details = model.get('details', {})

                model_info = ModelInfo(
                    name=name,
                    size=self._format_size(size),
                    modified=modified,
                    digest=digest,
                    details=details if isinstance(details, dict) else {}
                )
                model_list.append(model_info)

            if not self.is_cancelled:
                self.models_loaded.emit(model_list)

        except Exception as e:
            if not self.is_cancelled:
                self.error_occurred.emit(f"Failed to connect to remote server {self.api_config.base_url}: {str(e)}")

    def _pull_model(self):
        """Download a model from Ollama registry to remote server"""
        if not self.model_name:
            self.error_occurred.emit("No model name provided")
            return

        try:
            # Connect to remote server
            client = ollama.Client(host=self.api_config.base_url)
            total_size = 0
            completed_size = 0

            self.pull_progress.emit(-1, f"Starting download of {self.model_name} to remote server...")

            # Stream the download progress
            for progress in client.pull(self.model_name, stream=True):
                if self.is_cancelled:
                    self.pull_progress.emit(0, "Download cancelled")
                    return

                if 'total' in progress:
                    total_size = progress['total']
                if 'completed' in progress:
                    completed_size = progress['completed']

                status = progress.get('status', 'Downloading...')

                if total_size > 0:
                    percentage = int((completed_size / total_size) * 100)
                    self.pull_progress.emit(percentage, f"Downloading to remote server: {status} ({percentage}%)")
                else:
                    self.pull_progress.emit(-1, f"Remote download: {status}")

            if not self.is_cancelled:
                self.model_pulled.emit(self.model_name)

        except Exception as e:
            if not self.is_cancelled:
                self.error_occurred.emit(f"Failed to download to remote server {self.api_config.base_url}: {str(e)}")

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format"""
        if size_bytes == 0:
            return "Unknown"

        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
