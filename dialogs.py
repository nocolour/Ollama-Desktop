"""
Dialogs module
Contains all dialog classes for settings, model downloads, etc.
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QCheckBox, QComboBox, QGroupBox, QListWidget,
    QListWidgetItem, QPushButton, QProgressBar, QLabel, QMessageBox,
    QSlider, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from models import APIConfig, ModelConfig, UIConfig, AvailableModel
import ollama


class SettingsDialog(QDialog):
    """Settings dialog for API and UI configuration"""

    def __init__(self, api_config: APIConfig, model_config: ModelConfig,
                 ui_config: UIConfig, parent=None):
        super().__init__(parent)
        self.api_config = api_config
        self.model_config = model_config
        self.ui_config = ui_config
        self.dark_mode = ui_config.dark_mode
        self.setup_ui()
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 600)
        self.apply_theme()

    def setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout(self)

        # API Settings Group
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout(api_group)

        self.host_edit = QLineEdit(self.api_config.host)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.api_config.port)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(self.api_config.timeout)

        api_layout.addRow("Host:", self.host_edit)
        api_layout.addRow("Port:", self.port_spin)
        api_layout.addRow("Timeout (s):", self.timeout_spin)

        layout.addWidget(api_group)

        # Model Settings Group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout(model_group)

        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 200)
        self.temperature_slider.setValue(int(self.model_config.temperature * 100))
        self.temperature_slider.setToolTip("Controls randomness in responses (0.0 = deterministic, 2.0 = very random)")
        self.temperature_label = QLabel(f"{self.model_config.temperature:.2f}")

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)

        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(int(self.model_config.top_p * 100))
        self.top_p_slider.setToolTip("Controls diversity of word choices (0.0 = limited, 1.0 = full vocabulary)")
        self.top_p_label = QLabel(f"{self.model_config.top_p:.2f}")

        top_p_layout = QHBoxLayout()
        top_p_layout.addWidget(self.top_p_slider)
        top_p_layout.addWidget(self.top_p_label)

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        self.max_tokens_spin.setValue(self.model_config.num_predict)
        self.max_tokens_spin.setToolTip("Maximum number of tokens to generate in response")

        self.context_window_spin = QSpinBox()
        self.context_window_spin.setRange(512, 32768)
        self.context_window_spin.setValue(self.model_config.num_ctx)
        self.context_window_spin.setToolTip("Maximum context length (conversation history + response)")

        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlainText(self.model_config.system_prompt)
        self.system_prompt_edit.setMaximumHeight(100)

        model_layout.addRow("Temperature:", temp_layout)
        model_layout.addRow("Top P:", top_p_layout)
        model_layout.addRow("Max Tokens:", self.max_tokens_spin)
        model_layout.addRow("Context Window:", self.context_window_spin)
        model_layout.addRow("System Prompt:", self.system_prompt_edit)

        layout.addWidget(model_group)

        # UI Settings Group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)

        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setChecked(self.ui_config.dark_mode)

        self.auto_scroll_check = QCheckBox()
        self.auto_scroll_check.setChecked(self.ui_config.auto_scroll)

        self.show_timestamps_check = QCheckBox()
        self.show_timestamps_check.setChecked(self.ui_config.show_timestamps)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.ui_config.font_size)

        ui_layout.addRow("Dark Mode:", self.dark_mode_check)
        ui_layout.addRow("Auto Scroll:", self.auto_scroll_check)
        ui_layout.addRow("Show Timestamps:", self.show_timestamps_check)
        ui_layout.addRow("Font Size:", self.font_size_spin)

        layout.addWidget(ui_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        # Add Reset to Defaults button
        reset_btn = buttons.addButton("Reset to Defaults", QDialogButtonBox.ButtonRole.ResetRole)
        reset_btn.clicked.connect(self.reset_to_defaults)
        reset_btn.setToolTip("Reset all settings to recommended default values (Ctrl+R)")
        reset_btn.setShortcut("Ctrl+R")
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        # Connect signals
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(f"{v/100:.2f}")
        )
        self.top_p_slider.valueChanged.connect(
            lambda v: self.top_p_label.setText(f"{v/100:.2f}")
        )

    def reset_to_defaults(self):
        """Reset all settings to recommended default values"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their recommended default values?\n\n"
            "Default values:\n"
            "• API: localhost:11434, 30s timeout\n"
            "• Model: temp=0.7, top_p=0.9, max_tokens=1024, context=4096\n"
            "• UI: dark mode, auto scroll, show timestamps, font size=12\n"
            "• System prompt will be cleared\n\n"
            "Your current settings will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Reset API settings
        self.host_edit.setText("localhost")
        self.port_spin.setValue(11434)
        self.timeout_spin.setValue(30)
        
        # Reset model settings
        self.temperature_slider.setValue(70)  # 0.7 * 100
        self.temperature_label.setText("0.70")
        self.top_p_slider.setValue(90)  # 0.9 * 100
        self.top_p_label.setText("0.90")
        self.max_tokens_spin.setValue(1024)
        self.context_window_spin.setValue(4096)
        self.system_prompt_edit.clear()
        
        # Reset UI settings
        self.dark_mode_check.setChecked(True)
        self.auto_scroll_check.setChecked(True)
        self.show_timestamps_check.setChecked(True)
        self.font_size_spin.setValue(12)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Settings Reset",
            "All settings have been reset to their recommended default values."
        )

    def get_api_config(self) -> APIConfig:
        """Get the API configuration from dialog"""
        return APIConfig(
            host=self.host_edit.text(),
            port=self.port_spin.value(),
            timeout=self.timeout_spin.value()
        )

    def get_model_config(self) -> ModelConfig:
        """Get the model configuration from dialog"""
        return ModelConfig(
            temperature=self.temperature_slider.value() / 100.0,
            top_p=self.top_p_slider.value() / 100.0,
            num_predict=self.max_tokens_spin.value(),
            num_ctx=self.context_window_spin.value(),
            system_prompt=self.system_prompt_edit.toPlainText()
        )

    def get_ui_config(self) -> UIConfig:
        """Get the UI configuration from dialog"""
        return UIConfig(
            dark_mode=self.dark_mode_check.isChecked(),
            auto_scroll=self.auto_scroll_check.isChecked(),
            show_timestamps=self.show_timestamps_check.isChecked(),
            font_size=self.font_size_spin.value()
        )

    def apply_theme(self):
        """Apply theme to dialog based on dark_mode setting"""
        if self.dark_mode:
            # Inherit styles from parent window since QDialog doesn't override them
            pass
        else:
            # Light mode is handled by parent window's stylesheet reset
            pass


class ModelDownloadDialog(QDialog):
    """Dialog for downloading new models from Ollama registry with remote server support"""

    # Curated list of popular models
    AVAILABLE_MODELS = [
        AvailableModel("llama3.2:latest", "Latest Llama 3.2 model with improved performance", "4.7GB", "Large Language Models"),
        AvailableModel("llama3.2:8b", "Llama 3.2 8B - High-performance model", "4.7GB", "Large Language Models"),
        AvailableModel("llama3.2:3b", "Llama 3.2 3B - Compact yet powerful", "2.0GB", "Large Language Models"),
        AvailableModel("llama3.2:1b", "Llama 3.2 1B - Ultra-lightweight", "1.3GB", "Large Language Models"),
        AvailableModel("mistral:latest", "Mistral 7B - Fast and efficient", "4.1GB", "Large Language Models"),
        AvailableModel("mistral-small3.2:latest", "Mistral Small 3.2 - Advanced compact model", "14.2GB", "Large Language Models"),
        AvailableModel("codellama:latest", "Code Llama for programming tasks", "3.8GB", "Code Generation"),
        AvailableModel("phi3:latest", "Microsoft Phi-3 - Compact and capable", "2.3GB", "Large Language Models"),
        AvailableModel("gemma:latest", "Google Gemma model", "5.2GB", "Large Language Models"),
        AvailableModel("qwen:latest", "Qwen model from Alibaba", "4.1GB", "Large Language Models"),
        AvailableModel("qwen2.5:4b", "Qwen2.5 4B - Compact and efficient", "2.4GB", "Large Language Models"),
        AvailableModel("qwen2.5:7b", "Qwen2.5 7B - Balanced performance and size", "4.1GB", "Large Language Models"),
        AvailableModel("qwen3:1.7b", "Qwen3 1.7B - Ultra-compact next-gen model", "1.0GB", "Large Language Models"),
        AvailableModel("qwen3:4b", "Qwen3 4B - Efficient next-gen model", "2.4GB", "Large Language Models"),
        AvailableModel("qwen3:8b", "Qwen3 8B - Advanced next-gen model", "4.6GB", "Large Language Models"),
        AvailableModel("neural-chat:latest", "Intel Neural Chat", "4.1GB", "Conversational AI"),
        AvailableModel("starling-lm:latest", "Starling language model", "4.1GB", "Large Language Models"),
        AvailableModel("vicuna:latest", "Vicuna conversational model", "4.1GB", "Conversational AI"),
        AvailableModel("orca-mini:latest", "Orca Mini - Compact model", "1.9GB", "Large Language Models"),
        AvailableModel("zephyr:latest", "HuggingFace Zephyr", "4.1GB", "Large Language Models"),
    ]

    def __init__(self, model_manager, parent=None):
        super().__init__(parent)
        self.model_manager = model_manager
        self.is_downloading = False
        # Get dark mode from parent if available
        self.dark_mode = getattr(parent, 'ui_config', None)
        if self.dark_mode:
            self.dark_mode = self.dark_mode.dark_mode
        else:
            self.dark_mode = True  # Default to dark mode
        self.setup_ui()
        self.setWindowTitle("Download Models")
        self.setModal(True)
        self.resize(600, 500)

        # Connect signals
        self.model_manager.pull_progress.connect(self.update_progress)
        self.model_manager.model_pulled.connect(self.model_downloaded)
        self.model_manager.error_occurred.connect(self.download_error)

    def setup_ui(self):
        """Setup the model download dialog UI"""
        layout = QVBoxLayout(self)

        # Server info display
        self.server_info_label = QLabel()
        self.update_server_info()
        layout.addWidget(self.server_info_label)

        # Test connection and refresh buttons
        test_layout = QHBoxLayout()
        self.test_connection_btn = QPushButton("🔗 Test Remote Connection")
        self.test_connection_btn.clicked.connect(self.test_remote_connection)

        self.refresh_btn = QPushButton("🔄 Refresh Model List")
        self.refresh_btn.clicked.connect(self.populate_model_list)

        self.show_downloaded_btn = QPushButton("📋 Show Downloaded Models")
        self.show_downloaded_btn.clicked.connect(self.show_downloaded_models)

        test_layout.addWidget(self.test_connection_btn)
        test_layout.addWidget(self.refresh_btn)
        test_layout.addWidget(self.show_downloaded_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

        # Model list
        self.model_list = QListWidget()
        self.populate_model_list()

        # Model list header with status info
        list_header = QLabel("Available Models: (✅ = Downloaded, 📥 = Available for download)")
        if self.dark_mode:
            list_header.setStyleSheet("QLabel { color: #81A1C1; font-weight: bold; padding: 5px; }")
        else:
            list_header.setStyleSheet("QLabel { color: #059669; font-weight: bold; padding: 5px; }")
        layout.addWidget(list_header)
        layout.addWidget(self.model_list)

        # Progress area
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Select a model to download")

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.download_button = QPushButton("📥 Download Selected")
        self.download_button.clicked.connect(self.download_selected)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)

        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def update_server_info(self):
        """Update server information display"""
        api_config = self.model_manager.api_config
        server_url = f"{api_config.host}:{api_config.port}"
        self.server_info_label.setText(f"📡 Target Server: {server_url}")
        if self.dark_mode:
            self.server_info_label.setStyleSheet("QLabel { color: #81A1C1; font-weight: bold; padding: 5px; }")
        else:
            self.server_info_label.setStyleSheet("QLabel { color: #059669; font-weight: bold; padding: 5px; }")

    def test_remote_connection(self):
        """Test connection to remote Ollama server"""
        self.test_connection_btn.setEnabled(False)
        self.test_connection_btn.setText("🔄 Testing...")

        try:
            api_config = self.model_manager.api_config
            client = ollama.Client(host=api_config.base_url)

            # Test connection by listing models
            response = client.list()
            model_count = len(response.models) if hasattr(response, 'models') else 0

            QMessageBox.information(
                self,
                "Connection Test",
                f"✅ Successfully connected to {api_config.base_url}\\n"
                f"Found {model_count} existing models on remote server."
            )

            # Show existing models if any
            if model_count > 0:
                existing_models = [model.model for model in response.models]
                model_list = "\\n".join(f"  • {model}" for model in existing_models[:10])
                if model_count > 10:
                    model_list += f"\\n  ... and {model_count - 10} more"

                QMessageBox.information(
                    self,
                    "Existing Models",
                    f"Models already on remote server:\\n\\n{model_list}"
                )

        except Exception as e:
            api_config = self.model_manager.api_config  # Get config for error message
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"❌ Failed to connect to remote server:\\n\\n{str(e)}\\n\\n"
                f"Please ensure:\\n"
                f"• Ollama is running on {api_config.host}:{api_config.port}\\n"
                f"• The server is accessible from this network\\n"
                f"• Firewall allows connections on port {api_config.port}"
            )

        finally:
            self.test_connection_btn.setEnabled(True)
            self.test_connection_btn.setText("🔗 Test Remote Connection")

    def populate_model_list(self):
        """Populate the model list with downloaded status indicators"""
        self.model_list.clear()

        # Get currently downloaded models from the server
        downloaded_models = self._get_downloaded_models()
        downloaded_model_names = {model.lower() for model in downloaded_models}

        # Create a set of available model names for quick lookup
        available_model_names = {model.name.lower() for model in self.AVAILABLE_MODELS}

        # Add models from our curated list with download status
        for model in self.AVAILABLE_MODELS:
            item = QListWidgetItem()

            # Check if model is already downloaded
            is_downloaded = model.name.lower() in downloaded_model_names
            status_indicator = "✅ " if is_downloaded else "📥 "
            status_text = " (Downloaded)" if is_downloaded else ""

            item.setText(f"{status_indicator}{model.name} - {model.description} ({model.size}){status_text}")
            item.setData(Qt.ItemDataRole.UserRole, model)

            # Add visual styling
            font = QFont()
            font.setPointSize(10)
            if is_downloaded:
                font.setBold(True)
            item.setFont(font)

            self.model_list.addItem(item)

        # Add any downloaded models that are not in our curated list
        missing_models = []
        for downloaded_model in downloaded_models:
            if downloaded_model.lower() not in available_model_names:
                missing_models.append(downloaded_model)

        if missing_models:
            # Add separator
            separator_item = QListWidgetItem()
            separator_item.setText("━━━ Additional Downloaded Models ━━━")
            separator_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
            font = QFont()
            font.setBold(True)
            font.setItalic(True)
            separator_item.setFont(font)
            self.model_list.addItem(separator_item)

            # Add missing models
            for model_name in sorted(missing_models):
                # Create AvailableModel object for missing models
                missing_model = AvailableModel(
                    name=model_name,
                    description=f"Downloaded model",
                    size="Unknown",
                    category="Downloaded Models"
                )

                item = QListWidgetItem()
                item.setText(f"✅ {model_name} - Already downloaded (Unknown size)")
                item.setData(Qt.ItemDataRole.UserRole, missing_model)

                # Style for already downloaded models
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                item.setFont(font)

                self.model_list.addItem(item)

    def _get_downloaded_models(self):
        """Get list of models currently downloaded on the server"""
        try:
            api_config = self.model_manager.api_config
            client = ollama.Client(host=api_config.base_url)
            response = client.list()

            # Handle both old dict format and new Model object format
            models_data = response.get('models', []) if isinstance(response, dict) else response.models

            model_names = []
            for model in models_data:
                if hasattr(model, 'model'):  # New Model object format
                    name = str(model.model) if model.model else None
                else:  # Old dict format (fallback)
                    name = str(model.get('name')) if model.get('name') else None

                if name:
                    model_names.append(name)

            return model_names

        except Exception as e:
            # If we can't connect, return empty list (silently handle connection errors)
            return []

    def download_selected(self):
        """Download the selected model to remote server"""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a model to download.")
            return

        # Check if this is a separator item (non-selectable)
        if not (current_item.flags() & Qt.ItemFlag.ItemIsSelectable):
            QMessageBox.information(self, "Invalid Selection", "Please select a downloadable model.")
            return

        if self.is_downloading:
            QMessageBox.information(self, "Download in Progress", "A download is already in progress.")
            return

        model = current_item.data(Qt.ItemDataRole.UserRole)

        # Check if model is already downloaded
        downloaded_models = self._get_downloaded_models()
        downloaded_model_names = {model_name.lower() for model_name in downloaded_models}

        if model.name.lower() in downloaded_model_names:
            QMessageBox.information(
                self,
                "Model Already Downloaded",
                f"The model '{model.name}' is already downloaded on the remote server.\\n\\n"
                f"You can use it directly without downloading again."
            )
            return

        # Confirm download to remote server
        api_config = self.model_manager.api_config
        reply = QMessageBox.question(
            self,
            "Confirm Download",
            f"Download {model.name} ({model.size}) to remote server?\\n\\n"
            f"Target: {api_config.base_url}\\n\\n"
            f"This will download the model directly to the remote server.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Start download
        self.is_downloading = True
        self.download_button.setEnabled(False)
        self.cancel_button.setText("🛑 Cancel Download")

        self.progress_label.setText(f"Downloading {model.name} to remote server...")
        self.progress_bar.setRange(0, 0)  # Indeterminate initially

        # Start the download via ModelManager
        self.model_manager.pull_model(model.name)

    def update_progress(self, percentage: int, status: str):
        """Update download progress"""
        if percentage >= 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percentage)
        else:
            self.progress_bar.setRange(0, 0)  # Indeterminate

        self.progress_label.setText(f"📥 {status}")

    def model_downloaded(self, model_name: str):
        """Handle successful model download"""
        self.is_downloading = False
        self.download_button.setEnabled(True)
        self.cancel_button.setText("Close")

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_label.setText(f"✅ {model_name} downloaded successfully!")

        # Refresh the model list to show updated download status
        self.populate_model_list()

        api_config = self.model_manager.api_config
        QMessageBox.information(
            self,
            "Download Complete",
            f"✅ {model_name} has been successfully downloaded to:\\n\\n"
            f"{api_config.base_url}\\n\\n"
            f"The model is now available on the remote server."
        )

    def download_error(self, error_message: str):
        """Handle download error"""
        self.is_downloading = False
        self.download_button.setEnabled(True)
        self.cancel_button.setText("Close")

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_label.setText("❌ Download failed")

        QMessageBox.critical(
            self,
            "Download Error",
            f"❌ Failed to download model:\\n\\n{error_message}\\n\\n"
            f"Please check your connection to the remote server."
        )

    def cancel_download(self):
        """Cancel download or close dialog"""
        if self.is_downloading:
            reply = QMessageBox.question(
                self,
                "Cancel Download",
                "Are you sure you want to cancel the download?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.model_manager.cancel_operation()
                self.is_downloading = False
                self.download_button.setEnabled(True)
                self.cancel_button.setText("Close")
                self.progress_label.setText("Download cancelled")
                self.progress_bar.setValue(0)
        else:
            self.reject()

    def show_downloaded_models(self):
        """Show detailed information about currently downloaded models"""
        self.show_downloaded_btn.setEnabled(False)
        self.show_downloaded_btn.setText("🔄 Loading...")

        try:
            api_config = self.model_manager.api_config
            client = ollama.Client(host=api_config.base_url)
            response = client.list()

            # Handle both old dict format and new Model object format
            models_data = response.get('models', []) if isinstance(response, dict) else response.models

            if not models_data:
                QMessageBox.information(
                    self,
                    "No Downloaded Models",
                    f"No models are currently downloaded on the remote server:\\n\\n"
                    f"{api_config.base_url}\\n\\n"
                    f"Use the 'Download Models' feature to add some models."
                )
                return

            # Build detailed model information
            model_details = []
            total_size = 0

            for model in models_data:
                if hasattr(model, 'model'):  # New Model object format
                    name = str(model.model) if model.model else "Unknown"
                    size = getattr(model, 'size', 0)
                    modified = str(getattr(model, 'modified_at', 'Unknown'))
                    digest = str(getattr(model, 'digest', 'Unknown'))[:12] + "..."
                    details = getattr(model, 'details', {})
                else:  # Old dict format (fallback)
                    name = str(model.get('name', 'Unknown'))
                    size = model.get('size', 0)
                    modified = str(model.get('modified_at', 'Unknown'))
                    digest = str(model.get('digest', 'Unknown'))[:12] + "..."
                    details = model.get('details', {})

                # Format size
                formatted_size = self._format_size(size)
                total_size += size

                # Format modified date
                if modified != 'Unknown' and 'T' in modified:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = modified[:16]  # Fallback
                else:
                    formatted_date = modified

                # Get model parameters if available
                params = "Unknown"
                if isinstance(details, dict):
                    param_count = details.get('parameter_size', details.get('parameters', None))
                    if param_count:
                        params = param_count

                model_details.append({
                    'name': name,
                    'size': formatted_size,
                    'raw_size': size,
                    'modified': formatted_date,
                    'digest': digest,
                    'params': params
                })

            # Sort by size (largest first)
            model_details.sort(key=lambda x: x['raw_size'], reverse=True)

            # Build display text
            total_formatted_size = self._format_size(total_size)
            model_count = len(model_details)

            header = f"📊 Downloaded Models on {api_config.base_url}\\n"
            header += f"{'='*60}\\n"
            header += f"Total Models: {model_count} | Total Size: {total_formatted_size}\\n\\n"

            model_list_text = ""
            for i, model in enumerate(model_details, 1):
                model_list_text += f"{i:2d}. 📦 {model['name']}\\n"
                model_list_text += f"     Size: {model['size']} | Parameters: {model['params']}\\n"
                model_list_text += f"     Modified: {model['modified']}\\n"
                model_list_text += f"     Digest: {model['digest']}\\n\\n"

            full_text = header + model_list_text

            # Create a custom dialog to show the information
            dialog = QDialog(self)
            dialog.setWindowTitle("Downloaded Models")
            dialog.setModal(True)
            dialog.resize(700, 500)

            layout = QVBoxLayout(dialog)

            # Add header info
            header_label = QLabel(f"📊 {model_count} Models Downloaded ({total_formatted_size} total)")
            if self.dark_mode:
                header_label.setStyleSheet("QLabel { color: #81A1C1; font-weight: bold; font-size: 16px; padding: 10px; }")
            else:
                header_label.setStyleSheet("QLabel { color: #059669; font-weight: bold; font-size: 16px; padding: 10px; }")
            layout.addWidget(header_label)

            # Add scrollable text area
            text_area = QTextEdit()
            text_area.setPlainText(full_text)
            text_area.setReadOnly(True)
            if self.dark_mode:
                text_area.setStyleSheet("""
                    QTextEdit {
                        background-color: #2E3440;
                        color: #ECEFF4;
                        border: 1px solid #4C566A;
                        border-radius: 5px;
                        padding: 10px;
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                        font-size: 11px;
                        line-height: 1.4;
                    }
                """)
            else:
                text_area.setStyleSheet("""
                    QTextEdit {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                        border-radius: 5px;
                        padding: 10px;
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                        font-size: 11px;
                        line-height: 1.4;
                    }
                """)
            layout.addWidget(text_area)

            # Add buttons
            button_layout = QHBoxLayout()

            refresh_models_btn = QPushButton("🔄 Refresh")
            refresh_models_btn.clicked.connect(lambda: self._refresh_downloaded_models_dialog(dialog, text_area, header_label))

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)

            button_layout.addWidget(refresh_models_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"❌ Failed to fetch downloaded models:\\n\\n{str(e)}\\n\\n"
                f"Please ensure the Ollama server is running and accessible."
            )

        finally:
            self.show_downloaded_btn.setEnabled(True)
            self.show_downloaded_btn.setText("📋 Show Downloaded Models")

    def _refresh_downloaded_models_dialog(self, dialog, text_area, header_label):
        """Refresh the downloaded models dialog"""
        try:
            api_config = self.model_manager.api_config
            client = ollama.Client(host=api_config.base_url)
            response = client.list()

            # Handle both old dict format and new Model object format
            models_data = response.get('models', []) if isinstance(response, dict) else response.models

            if not models_data:
                text_area.setPlainText("No models are currently downloaded on the server.")
                header_label.setText("📊 0 Models Downloaded (0 B total)")
                return

            # Build updated model information (same logic as above)
            model_details = []
            total_size = 0

            for model in models_data:
                if hasattr(model, 'model'):  # New Model object format
                    name = str(model.model) if model.model else "Unknown"
                    size = getattr(model, 'size', 0)
                    modified = str(getattr(model, 'modified_at', 'Unknown'))
                    digest = str(getattr(model, 'digest', 'Unknown'))[:12] + "..."
                    details = getattr(model, 'details', {})
                else:  # Old dict format (fallback)
                    name = str(model.get('name', 'Unknown'))
                    size = model.get('size', 0)
                    modified = str(model.get('modified_at', 'Unknown'))
                    digest = str(model.get('digest', 'Unknown'))[:12] + "..."
                    details = model.get('details', {})

                formatted_size = self._format_size(size)
                total_size += size

                # Format modified date
                if modified != 'Unknown' and 'T' in modified:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = modified[:16]
                else:
                    formatted_date = modified

                params = "Unknown"
                if isinstance(details, dict):
                    param_count = details.get('parameter_size', details.get('parameters', None))
                    if param_count:
                        params = param_count

                model_details.append({
                    'name': name,
                    'size': formatted_size,
                    'raw_size': size,
                    'modified': formatted_date,
                    'digest': digest,
                    'params': params
                })

            model_details.sort(key=lambda x: x['raw_size'], reverse=True)

            total_formatted_size = self._format_size(total_size)
            model_count = len(model_details)

            header = f"📊 Downloaded Models on {api_config.base_url}\\n"
            header += f"{'='*60}\\n"
            header += f"Total Models: {model_count} | Total Size: {total_formatted_size}\\n\\n"

            model_list_text = ""
            for i, model in enumerate(model_details, 1):
                model_list_text += f"{i:2d}. 📦 {model['name']}\\n"
                model_list_text += f"     Size: {model['size']} | Parameters: {model['params']}\\n"
                model_list_text += f"     Modified: {model['modified']}\\n"
                model_list_text += f"     Digest: {model['digest']}\\n\\n"

            full_text = header + model_list_text
            text_area.setPlainText(full_text)
            header_label.setText(f"📊 {model_count} Models Downloaded ({total_formatted_size} total)")

        except Exception as e:
            text_area.setPlainText(f"Error refreshing model list: {str(e)}")
            header_label.setText("📊 Error Loading Models")

    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        # Convert to appropriate unit
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                if unit == 'B':
                    return f"{int(size_bytes)} {unit}"
                else:
                    return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} PB"
