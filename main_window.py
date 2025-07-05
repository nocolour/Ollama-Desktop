"""
Main Window Implementation for Ollama Desktop
Handles the primary application window, chat interface, and model management
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit,
    QLineEdit, QPushButton, QComboBox, QLabel, QSplitter,
    QMenuBar, QStatusBar, QMessageBox, QScrollArea, QFrame, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, QSettings, QTimer
from PySide6.QtGui import QFont, QTextCursor, QKeySequence, QShortcut

from models import ChatMessage, ModelInfo, APIConfig, ModelConfig, UIConfig
from workers import OllamaWorker, ModelManager
from ui_components import ChatMessageWidget
from dialogs import SettingsDialog, ModelDownloadDialog


class OllamaDesktopApp(QMainWindow):
    """Main application window for Ollama Desktop"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama Desktop Chat")
        self.setMinimumSize(1100, 700)

        # Initialize settings with proper organization and application name for persistence
        self.settings = QSettings("OllamaDesktop", "OllamaDesktopChat")

        # Helper functions for type-safe settings retrieval
        def get_int_setting(key: str, default: int) -> int:
            try:
                value = self.settings.value(key, default)
                if isinstance(value, int):
                    return value
                return int(str(value)) if value is not None else default
            except (ValueError, TypeError):
                return default

        def get_float_setting(key: str, default: float) -> float:
            try:
                value = self.settings.value(key, default)
                if isinstance(value, float):
                    return value
                return float(str(value)) if value is not None else default
            except (ValueError, TypeError):
                return default

        def get_bool_setting(key: str, default: bool) -> bool:
            try:
                value = self.settings.value(key, default)
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes', 'on')
            except (ValueError, TypeError):
                return default

        def get_str_setting(key: str, default: str) -> str:
            try:
                value = self.settings.value(key, default)
                return str(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        # Initialize configurations
        self.api_config = APIConfig(
            host=get_str_setting("api/host", "localhost"),
            port=get_int_setting("api/port", 11434),
            timeout=get_int_setting("api/timeout", 30)
        )
        self.model_config = ModelConfig(
            temperature=get_float_setting("model/temperature", 0.7),
            top_p=get_float_setting("model/top_p", 0.9),
            num_predict=get_int_setting("model/num_predict", 512),
            num_ctx=get_int_setting("model/num_ctx", 2048),
            system_prompt=get_str_setting("model/system_prompt", "")
        )
        self.ui_config = UIConfig(
            font_size=get_int_setting("ui/font_size", 12),
            dark_mode=get_bool_setting("ui/dark_mode", True)
        )

        # Load default model setting
        self.default_model = get_str_setting("app/default_model", "")

        # Initialize worker threads
        self.ollama_worker = None
        self.model_manager = None

        # Message history
        self.message_history = []

        # Initialize UI components
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()

        # Load initial data - only load installed models
        self.load_installed_models()

        # Apply theme
        self.apply_theme()

    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top toolbar
        self.setup_toolbar(main_layout)

        # Chat area (expanded to take most space)
        self.setup_chat_area(main_layout)

        # Input area
        self.setup_input_area(main_layout)

        # Status bar
        self.setup_status_bar()

        # Menu bar
        self.setup_menu_bar()

    def setup_toolbar(self, parent_layout):
        """Setup the top toolbar with model selection and controls"""
        toolbar_layout = QHBoxLayout()

        # Set Default button (for easy access - placed before model selection)
        self.set_default_btn = QPushButton("⭐ Set Default")
        self.set_default_btn.clicked.connect(self.set_current_as_default)
        self.set_default_btn.setToolTip("Set current model as default model (will be auto-selected on app restart)")
        self.set_default_btn.setStyleSheet("QPushButton { background-color: #FF6B35; color: white; font-weight: bold; }")

        # Model selection
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.model_combo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.model_combo.customContextMenuRequested.connect(self.show_model_context_menu)

        # Download button
        self.download_btn = QPushButton("Download Models")
        self.download_btn.clicked.connect(self.show_download_dialog)

        # Settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.show_settings_dialog)

        # Clear chat button
        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.clicked.connect(self.clear_chat)

        # New chat button (to start fresh with current system prompt)
        self.new_chat_btn = QPushButton("New Chat")
        self.new_chat_btn.clicked.connect(self.new_chat)
        self.new_chat_btn.setToolTip("Start a new conversation with the current system prompt")

        toolbar_layout.addWidget(self.set_default_btn)
        toolbar_layout.addWidget(model_label)
        toolbar_layout.addWidget(self.model_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.download_btn)
        toolbar_layout.addWidget(self.settings_btn)
        toolbar_layout.addWidget(self.new_chat_btn)
        toolbar_layout.addWidget(self.clear_btn)

        parent_layout.addLayout(toolbar_layout)

    def setup_chat_area(self, parent_layout):
        """Setup the unified chat area with modern bubble styling"""
        # Create scroll area for chat messages
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Chat container widget
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chat_container")  # Set object name for styling
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.chat_scroll_area.setWidget(self.chat_container)

        # Give chat area maximum space
        parent_layout.addWidget(self.chat_scroll_area, 1)

    def setup_input_area(self, parent_layout):
        """Setup the input area with expandable text box"""
        input_layout = QHBoxLayout()

        # Input text box (expandable)
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(120)
        self.input_text.setMinimumHeight(40)
        self.input_text.setPlaceholderText("Type your message here... (Press Enter to send, Shift+Enter for new line)")
        self.input_text.textChanged.connect(self.adjust_input_height)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(80)
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_text)
        input_layout.addWidget(self.send_btn)

        parent_layout.addLayout(input_layout)

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Chat", self.new_chat)
        file_menu.addAction("Clear Chat", self.clear_chat)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Download Models", self.show_download_dialog)
        tools_menu.addAction("Settings", self.show_settings_dialog)
        tools_menu.addSeparator()
        
        # Default model submenu - will be updated dynamically
        self.default_model_menu = tools_menu.addMenu("Default Model")
        self.update_default_model_menu()

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)

    def setup_connections(self):
        """Setup signal connections"""
        # Model manager signals will be connected when created
        pass

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Send message shortcut
        self.send_shortcut = QShortcut(QKeySequence("Return"), self.input_text)
        self.send_shortcut.activated.connect(self.send_message)

        # New chat shortcut
        self.new_chat_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_chat_shortcut.activated.connect(self.new_chat)

        # Clear chat shortcut
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.clear_shortcut.activated.connect(self.clear_chat)

    def load_available_models(self):
        """Load available models from Ollama API with filtering"""
        if not self.model_manager:
            self.model_manager = ModelManager(self.api_config)
            self.model_manager.models_loaded.connect(self.on_available_models_loaded)
            self.model_manager.error_occurred.connect(self.on_error)

        # Load models from API
        self.model_manager.load_models()

    def load_installed_models(self):
        """Load installed models from Ollama"""
        if not self.model_manager:
            self.model_manager = ModelManager(self.api_config)
            self.model_manager.models_loaded.connect(self.on_installed_models_loaded)

        self.model_manager.load_models()

    def on_available_models_loaded(self, models: List[ModelInfo]):
        """Handle available models loaded"""
        # Filter models to remove invalid/undownloadable ones
        model_names = [model.name for model in models]
        filtered_models = self.filter_valid_models(model_names)

        # Update combo box
        self.model_combo.clear()
        self.model_combo.addItems(filtered_models)

        if filtered_models:
            self.status_bar.showMessage(f"Loaded {len(filtered_models)} available models")
        else:
            self.status_bar.showMessage("No valid models available")

    def on_installed_models_loaded(self, models: List[ModelInfo]):
        """Handle installed models loaded"""
        # Extract model names and apply filtering
        model_names = [model.name for model in models]
        filtered_models = self.filter_valid_models(model_names)

        # Update combo box with filtered installed models
        current_text = self.model_combo.currentText()
        self.model_combo.clear()

        if filtered_models:
            self.model_combo.addItems(filtered_models)
            
            # Try to select default model first, then restore previous selection
            model_to_select = None
            if self.default_model and self.default_model in filtered_models:
                model_to_select = self.default_model
            elif current_text in filtered_models:
                model_to_select = current_text
            
            if model_to_select:
                self.model_combo.setCurrentText(model_to_select)
            
            # Update tooltip after selection
            self.update_model_combo_tooltip()

        self.status_bar.showMessage(f"Loaded {len(filtered_models)} installed models (filtered from {len(model_names)} total)")

    def filter_valid_models(self, models: List[str]) -> List[str]:
        """Filter models to only include valid, downloadable ones"""
        valid_models = []

        for model in models:
            model_lower = model.lower()

            # Skip invalid model patterns
            if any(skip in model_lower for skip in [
                'embedding', 'vision', 'multimodal', 'experimental',
                'unstable', 'beta', 'alpha', 'dev', 'draft',
                'corrupt', 'broken', 'incomplete', 'failed'
            ]):
                continue

            # Skip models with "test" but not "latest" (since "latest" contains "test")
            if 'test' in model_lower and 'latest' not in model_lower:
                continue

            # Skip models with unusual or problematic formats
            if ':' in model:
                name, tag = model.split(':', 1)
                # Skip if tag looks invalid or unsupported
                invalid_tags = [
                    'fp16', 'gguf', 'bin', 'safetensors', 'pytorch',
                    'tf', 'onnx', 'openvino', 'mlx', 'f16', 'q2_k',
                    'q3_k', 'q4_k', 'q5_k', 'q6_k', 'q8_0', 'iq',
                    'code', 'instruct-fp16', 'chat-fp16'
                ]
                if any(invalid in tag.lower() for invalid in invalid_tags):
                    continue

            # Skip very old or deprecated models
            deprecated_models = [
                'codellama:7b-python', 'codellama:13b-python', 'codellama:34b-python',
                'vicuna', 'alpaca', 'chatglm', 'baichuan', 'internlm'
            ]
            if any(deprecated in model_lower for deprecated in deprecated_models):
                continue

            # Skip models that are too large (>70B parameters typically)
            if any(size in model_lower for size in ['70b', '72b', '180b', '405b']):
                continue

            # Only include models that are likely to work
            valid_patterns = [
                'llama', 'mistral', 'gemma', 'qwen', 'phi', 'tinyllama',
                'orca', 'dolphin', 'wizard', 'neural', 'nous', 'zephyr'
            ]

            if any(pattern in model_lower for pattern in valid_patterns):
                valid_models.append(model)

        return sorted(valid_models)

    def adjust_input_height(self):
        """Adjust input text box height based on content"""
        doc = self.input_text.document()
        height = doc.size().height() + 10
        height = max(40, min(120, height))
        self.input_text.setMaximumHeight(int(height))

    def send_message(self):
        """Send message to Ollama"""
        text = self.input_text.toPlainText().strip()
        if not text:
            return

        # Check if model is selected
        current_model = self.model_combo.currentText()
        if not current_model:
            QMessageBox.warning(self, "No Model", "Please select a model first.")
            return

        # Clear input
        self.input_text.clear()

        # Add user message to chat
        user_message = ChatMessage(
            role="user",
            content=text,
            timestamp=None,
            model=current_model
        )
        self.add_message_to_chat(user_message)
        self.message_history.append(user_message)

        # Start ollama worker
        if self.ollama_worker:
            self.ollama_worker.quit()
            self.ollama_worker.wait()

        # Create chat messages list including current user message
        self.ollama_worker = OllamaWorker(
            model=current_model,
            messages=self.message_history,
            api_config=self.api_config,
            model_config=self.model_config,
            options={}
        )
        self.ollama_worker.message_complete.connect(self.on_response_received)
        self.ollama_worker.error_occurred.connect(self.on_error)
        self.ollama_worker.finished.connect(self.on_worker_finished)

        self.ollama_worker.start()

        # Update UI
        self.send_btn.setEnabled(False)
        self.status_bar.showMessage("Generating response...")

    def add_message_to_chat(self, message: ChatMessage):
        """Add a message to the unified chat area"""
        message_widget = ChatMessageWidget(
            message,
            show_timestamps=self.ui_config.show_timestamps,
            font_size=self.ui_config.font_size,
            dark_mode=self.ui_config.dark_mode
        )
        self.chat_layout.addWidget(message_widget)

        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_response_received(self, response: str):
        """Handle response from Ollama"""
        # Create assistant message
        assistant_message = ChatMessage(
            role="assistant",
            content=response,
            timestamp=None,
            model=self.model_combo.currentText()
        )
        self.add_message_to_chat(assistant_message)
        self.message_history.append(assistant_message)

    def on_worker_finished(self):
        """Handle worker finished"""
        self.send_btn.setEnabled(True)
        self.status_bar.showMessage("Ready")

    def on_error(self, error: str):
        """Handle error"""
        QMessageBox.critical(self, "Error", f"An error occurred: {error}")
        self.send_btn.setEnabled(True)
        self.status_bar.showMessage("Error occurred")

    def show_model_context_menu(self, position):
        """Show context menu for model selection"""
        current_model = self.model_combo.currentText()
        
        if not current_model:
            return

        menu = QMenu(self)
        
        # Add "Set as Default" action
        set_default_action = menu.addAction(f"Set '{current_model}' as Default Model")
        set_default_action.triggered.connect(lambda: self.set_default_model(current_model))
        
        # Add current default info if there is one
        if self.default_model:
            menu.addSeparator()
            current_default_action = menu.addAction(f"Current Default: {self.default_model}")
            current_default_action.setEnabled(False)  # Make it non-clickable info
            
            # Add option to clear default
            clear_default_action = menu.addAction("Clear Default Model")
            clear_default_action.triggered.connect(self.clear_default_model)
        
        # Show the menu
        menu.exec(self.model_combo.mapToGlobal(position))

    def set_default_model(self, model_name: str):
        """Set the specified model as the default"""
        self.default_model = model_name
        self.settings.setValue("app/default_model", model_name)
        self.settings.sync()
        
        self.status_bar.showMessage(f"Set '{model_name}' as default model", 3000)
        
        # Update the model combo tooltip to show it's the default
        self.update_model_combo_tooltip()
        
        # Update the menu
        self.update_default_model_menu()

    def set_current_as_default(self):
        """Set the currently selected model as default"""
        current_model = self.model_combo.currentText()
        if current_model:
            self.set_default_model(current_model)
        else:
            QMessageBox.information(
                self,
                "No Model Selected",
                "Please select a model first before setting it as default."
            )

    def clear_default_model(self):
        """Clear the default model setting"""
        reply = QMessageBox.question(
            self,
            "Clear Default Model",
            "Are you sure you want to clear the default model setting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.default_model = ""
            self.settings.setValue("app/default_model", "")
            self.settings.sync()
            
            self.status_bar.showMessage("Default model cleared", 3000)
            self.update_model_combo_tooltip()
            self.update_default_model_menu()

    def update_model_combo_tooltip(self):
        """Update the model combo tooltip to show default model info"""
        current_model = self.model_combo.currentText()
        if self.default_model:
            if current_model == self.default_model:
                tooltip = f"Current model: {current_model} (Default)\nRight-click to change default model"
            else:
                tooltip = f"Current model: {current_model}\nDefault model: {self.default_model}\nRight-click to set as default"
        else:
            tooltip = f"Current model: {current_model}\nRight-click to set as default model"
        
        self.model_combo.setToolTip(tooltip)

    def update_default_model_menu(self):
        """Update the default model menu items"""
        # Clear existing actions
        self.default_model_menu.clear()
        
        if self.default_model:
            current_default_action = self.default_model_menu.addAction(f"Current: {self.default_model}")
            current_default_action.setEnabled(False)
            self.default_model_menu.addSeparator()
        
        set_current_default_action = self.default_model_menu.addAction("Set Current as Default")
        set_current_default_action.triggered.connect(self.set_current_as_default)
        
        clear_default_action = self.default_model_menu.addAction("Clear Default")
        clear_default_action.triggered.connect(self.clear_default_model)
        clear_default_action.setEnabled(bool(self.default_model))

    def on_model_changed(self, model_name: str):
        """Handle model selection change"""
        if model_name:
            self.status_bar.showMessage(f"Selected model: {model_name}")
            self.update_model_combo_tooltip()

    def new_chat(self):
        """Start a new chat conversation with current system prompt"""
        if len(self.message_history) > 0:
            reply = QMessageBox.question(
                self,
                "Start New Chat",
                "Are you sure you want to start a new chat? This will clear the current conversation.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.clear_chat()
        if self.model_config.system_prompt.strip():
            self.status_bar.showMessage("New chat started with system prompt active", 3000)
        else:
            self.status_bar.showMessage("New chat started", 3000)

    def clear_chat(self):
        """Clear the chat area"""
        # Remove all message widgets
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Clear message history
        self.message_history.clear()

        self.status_bar.showMessage("Chat cleared")

    def show_download_dialog(self):
        """Show model download dialog"""
        if not self.model_manager:
            self.model_manager = ModelManager(self.api_config)

        dialog = ModelDownloadDialog(self.model_manager, self)
        if dialog.exec():
            # Refresh models after download
            self.load_installed_models()

    def show_settings_dialog(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.api_config, self.model_config, self.ui_config, self)
        if dialog.exec():
            # Apply new settings
            old_api_config = self.api_config
            old_model_config = self.model_config
            self.api_config = dialog.get_api_config()
            self.model_config = dialog.get_model_config()
            self.ui_config = dialog.get_ui_config()
            
            # Check if system prompt changed and there's an active conversation
            if (old_model_config.system_prompt != self.model_config.system_prompt and 
                len(self.message_history) > 0):
                reply = QMessageBox.question(
                    self,
                    "System Prompt Changed",
                    "The system prompt has been changed. Would you like to clear the current chat to apply the new system prompt?\n\n"
                    "Click 'Yes' to clear the chat and start fresh with the new system prompt.\n"
                    "Click 'No' to keep the current conversation (new system prompt will apply to new chats).",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.clear_chat()
                    self.status_bar.showMessage("Chat cleared - new system prompt active", 3000)
                else:
                    self.status_bar.showMessage("Settings saved - new system prompt will apply to new chats", 3000)
            else:
                self.status_bar.showMessage("Settings saved successfully", 3000)
            
            # Save settings to disk immediately
            self.save_settings()
            
            # Update model manager if API config changed
            if (old_api_config.host != self.api_config.host or 
                old_api_config.port != self.api_config.port or 
                old_api_config.timeout != self.api_config.timeout):
                if self.model_manager:
                    self.model_manager.update_api_config(self.api_config)
                # Reload models with new API config
                self.load_installed_models()
            
            # Apply theme changes
            self.apply_theme()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Ollama Desktop",
            "Ollama Desktop Chat v2.0\n\n"
            "A modern desktop interface for Ollama AI models.\n"
            "Built with PySide6 and Python.\n\n"
            "Author: TW. Phee\n\n"
            "Features:\n"
            "• Unified chat interface\n"
            "• Model download and management\n"
            "• Remote server support\n"
            "• Modern UI with themes"
        )

    def save_settings(self):
        """Save current settings"""
        self.settings.setValue("api/host", self.api_config.host)
        self.settings.setValue("api/port", self.api_config.port)
        self.settings.setValue("api/timeout", self.api_config.timeout)
        self.settings.setValue("model/temperature", self.model_config.temperature)
        self.settings.setValue("model/top_p", self.model_config.top_p)
        self.settings.setValue("model/num_predict", self.model_config.num_predict)
        self.settings.setValue("model/num_ctx", self.model_config.num_ctx)
        self.settings.setValue("model/system_prompt", self.model_config.system_prompt)
        self.settings.setValue("ui/font_size", self.ui_config.font_size)
        self.settings.setValue("ui/dark_mode", self.ui_config.dark_mode)
        self.settings.setValue("app/default_model", self.default_model)
        
        # Force immediate write to disk
        self.settings.sync()

    def apply_theme(self):
        """Apply current theme"""
        if self.ui_config.dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QScrollArea {
                    background-color: #1e1e1e;
                    border: 1px solid #3c3c3c;
                    border-radius: 8px;
                }
                QWidget#chat_container {
                    background-color: #1e1e1e;
                }
                QTextEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 8px;
                    padding: 8px;
                    selection-background-color: #5E81AC;
                }
                QTextEdit::placeholder {
                    color: #aaaaaa;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px 8px;
                    min-height: 20px;
                }
                QComboBox::drop-down {
                    background-color: #3c3c3c;
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    color: #ffffff;
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    selection-background-color: #5E81AC;
                    selection-color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
                QPushButton:pressed {
                    background-color: #0a5d61;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border-top: 1px solid #3c3c3c;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border-bottom: 1px solid #3c3c3c;
                }
                QMenuBar::item {
                    background-color: transparent;
                    color: #ffffff;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QMenu::item {
                    color: #ffffff;
                    padding: 5px 10px;
                }
                QMenu::item:selected {
                    background-color: #0d7377;
                    color: #ffffff;
                }
                QMenu::item:disabled {
                    color: #888888;
                }
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QDialogButtonBox QPushButton {
                    background-color: #0d7377;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 60px;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #ffffff;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QCheckBox {
                    color: #ffffff;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #555555;
                    background-color: #3c3c3c;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #0d7377;
                    background-color: #0d7377;
                }
                QSpinBox, QDoubleSpinBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #555555;
                    height: 8px;
                    background: #3c3c3c;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #0d7377;
                    border: 1px solid #0d7377;
                    width: 18px;
                    border-radius: 9px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QScrollArea {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 8px;
                }
                QWidget#chat_container {
                    background-color: #ffffff;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 8px;
                    padding: 8px;
                    selection-background-color: #2563eb;
                    selection-color: #ffffff;
                }
                QTextEdit::placeholder {
                    color: #666666;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px 8px;
                    min-height: 20px;
                }
                QComboBox::drop-down {
                    background-color: #ffffff;
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    color: #000000;
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    selection-background-color: #2563eb;
                    selection-color: #ffffff;
                }
                QLabel {
                    color: #000000;
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #2563eb;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
                QPushButton:pressed {
                    background-color: #1e40af;
                }
                QPushButton:disabled {
                    background-color: #e5e7eb;
                    color: #9ca3af;
                }
                QStatusBar {
                    background-color: #ffffff;
                    color: #000000;
                    border-top: 1px solid #d0d0d0;
                }
                QMenuBar {
                    background-color: #ffffff;
                    color: #000000;
                    border-bottom: 1px solid #d0d0d0;
                }
                QMenuBar::item {
                    background-color: transparent;
                    color: #000000;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #f3f4f6;
                    color: #000000;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                }
                QMenu::item {
                    color: #000000;
                    padding: 5px 10px;
                }
                QMenu::item:selected {
                    background-color: #2563eb;
                    color: #ffffff;
                }
                QMenu::item:disabled {
                    color: #9ca3af;
                }
                QDialog {
                    background-color: #ffffff;
                    color: #000000;
                }
                QDialogButtonBox QPushButton {
                    background-color: #2563eb;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 60px;
                }
                QGroupBox {
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #000000;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QCheckBox {
                    color: #000000;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #d0d0d0;
                    background-color: #ffffff;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #2563eb;
                    background-color: #2563eb;
                }
                QSpinBox, QDoubleSpinBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #d0d0d0;
                    height: 8px;
                    background: #f3f4f6;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #2563eb;
                    border: 1px solid #2563eb;
                    width: 18px;
                    border-radius: 9px;
                }
            """)

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop any running workers
        if self.ollama_worker:
            self.ollama_worker.cancel()  # Cancel operation first
            self.ollama_worker.quit()
            self.ollama_worker.wait(3000)  # Wait up to 3 seconds

        if self.model_manager:
            self.model_manager.cancel_operation()  # Cancel operation first
            self.model_manager.quit()
            self.model_manager.wait(3000)  # Wait up to 3 seconds

        # Save settings
        self.save_settings()

        event.accept()
