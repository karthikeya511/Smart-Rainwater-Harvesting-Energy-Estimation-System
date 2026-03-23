"""
Smart Rainwater Harvesting and Energy Estimation System
PyQt5 User Interface - CORRECTED VERSION
"""

import sys
import pandas as pd
import joblib
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QGroupBox,
    QRadioButton, QButtonGroup, QMessageBox, QFrame, QScrollArea,
    QGridLayout, QSizePolicy, QSlider, QSplitter
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QTextCursor


class GradientWidget(QWidget):
    """Custom widget with gradient background"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._start_color = QColor(41, 128, 185)  # Blue
        self._end_color = QColor(109, 213, 250)   # Light blue
        
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self._start_color)
        gradient.setColorAt(1, self._end_color)
        painter.fillRect(self.rect(), gradient)


class RainwaterHarvestingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dataset = None
        self.models = {}
        self.encoders = None
        self.current_zoom = 100  # Default zoom level
        self.init_ui()
        self.load_dataset()
        self.load_models()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Smart Rainwater Harvesting & Energy Estimation System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                color: #2980b9;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QRadioButton {
                font-size: 13px;
                color: #2c3e50;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
            QScrollBar:horizontal {
                border: none;
                background: #ecf0f1;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #3498db;
                min-width: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #2980b9;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3498db;
            }
            QSplitter::handle:hover {
                background-color: #2980b9;
            }
        """)
        
        # Top section (Inputs) - Scrollable
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(15)
        top_layout.setContentsMargins(5, 5, 5, 5)
        
        # Input method selection
        input_method_group = self.create_input_method_selection()
        top_layout.addWidget(input_method_group)
        
        # Location-based input section
        self.location_widget = self.create_location_input()
        top_layout.addWidget(self.location_widget)
        
        # Parameter-based input section with scroll
        self.parameter_scroll = QScrollArea()
        self.parameter_scroll.setWidgetResizable(True)
        self.parameter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.parameter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.parameter_widget = self.create_parameter_input()
        self.parameter_scroll.setWidget(self.parameter_widget)
        self.parameter_scroll.hide()
        top_layout.addWidget(self.parameter_scroll)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.analyze_btn = QPushButton("🔍 Analyze Data")
        self.analyze_btn.setMinimumHeight(45)
        self.analyze_btn.clicked.connect(self.analyze_data)
        
        self.clear_btn = QPushButton("🔄 Clear All")
        self.clear_btn.setMinimumHeight(45)
        self.clear_btn.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.clear_btn)
        top_layout.addLayout(button_layout)
        
        top_layout.addStretch()
        
        # Wrap top section in scroll area
        top_scroll = QScrollArea()
        top_scroll.setWidgetResizable(True)
        top_scroll.setWidget(top_widget)
        top_scroll.setMinimumHeight(300)
        
        # Bottom section (Results) - Scrollable with zoom controls
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setSpacing(10)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        
        # Zoom controls
        zoom_control_widget = self.create_zoom_controls()
        bottom_layout.addWidget(zoom_control_widget)
        
        # Results section
        self.results_widget = self.create_results_section()
        bottom_layout.addWidget(self.results_widget)
        
        # Add both sections to splitter
        splitter.addWidget(top_scroll)
        splitter.addWidget(bottom_widget)
        
        # Set initial sizes (40% input, 60% results)
        splitter.setSizes([400, 500])
        
        main_layout.addWidget(splitter)
        
    def create_header(self):
        """Create header with title and description"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                border-radius: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title = QLabel("💧 Smart Rainwater Harvesting & Energy Estimation System")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Advanced Analysis for Sustainable Water Management")
        subtitle.setStyleSheet("color: white; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        return header_widget
    
    def create_zoom_controls(self):
        """Create zoom control widget for results section"""
        zoom_widget = QWidget()
        zoom_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(10, 5, 10, 5)
        
        zoom_label = QLabel("🔍 Zoom:")
        zoom_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        # Zoom out button
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }
        """)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        self.zoom_slider.setMaximumWidth(300)
        
        # Zoom in button
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }
        """)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        # Zoom percentage label
        self.zoom_percent_label = QLabel("100%")
        self.zoom_percent_label.setStyleSheet("font-weight: bold; color: #2980b9; min-width: 50px;")
        self.zoom_percent_label.setAlignment(Qt.AlignCenter)
        
        # Reset zoom button
        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.setFixedHeight(30)
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(self.zoom_percent_label)
        zoom_layout.addWidget(reset_zoom_btn)
        zoom_layout.addStretch()
        
        return zoom_widget
    
    def create_input_method_selection(self):
        """Create input method selection group"""
        group = QGroupBox("📋 Select Input Method")
        layout = QHBoxLayout()
        layout.setSpacing(30)
        
        self.input_method_group = QButtonGroup()
        
        self.location_radio = QRadioButton("🌍 Location-Based Input")
        self.location_radio.setChecked(True)
        self.location_radio.toggled.connect(self.toggle_input_method)
        
        self.parameter_radio = QRadioButton("⚙️ Direct Parameters Input")
        
        self.input_method_group.addButton(self.location_radio)
        self.input_method_group.addButton(self.parameter_radio)
        
        layout.addWidget(self.location_radio)
        layout.addWidget(self.parameter_radio)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_location_input(self):
        """Create location-based input section"""
        group = QGroupBox("🗺️ Location Information")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # City input
        city_label = QLabel("City:")
        city_label.setStyleSheet("font-weight: bold;")
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Vijayawada")
        
        # District input
        district_label = QLabel("District:")
        district_label.setStyleSheet("font-weight: bold;")
        self.district_input = QLineEdit()
        self.district_input.setPlaceholderText("e.g., Krishna")
        
        # State input
        state_label = QLabel("State:")
        state_label.setStyleSheet("font-weight: bold;")
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("e.g., Andhra Pradesh")
        
        layout.addWidget(city_label, 0, 0)
        layout.addWidget(self.city_input, 0, 1)
        layout.addWidget(district_label, 1, 0)
        layout.addWidget(self.district_input, 1, 1)
        layout.addWidget(state_label, 2, 0)
        layout.addWidget(self.state_input, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def create_parameter_input(self):
        """Create parameter-based input section - WITH ALL 7 FEATURES"""
        group = QGroupBox("⚙️ Direct Parameters")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Rainfall Intensity
        self.rainfall_intensity_input = self.create_labeled_input(
            "Rainfall Intensity (mm/hr):", "e.g., 25.5", layout, 0
        )
        
        # Raindrop Size
        self.raindrop_size_input = self.create_labeled_input(
            "Raindrop Size (mm):", "e.g., 3.2", layout, 1
        )
        
        # Rainfall Type
        rainfall_type_label = QLabel("Rainfall Type:")
        rainfall_type_label.setStyleSheet("font-weight: bold;")
        self.rainfall_type_combo = QComboBox()
        self.rainfall_type_combo.addItems(["Moderate", "Heavy", "Storm"])
        layout.addWidget(rainfall_type_label, 2, 0)
        layout.addWidget(self.rainfall_type_combo, 2, 1)
        
        # Roof Area
        self.roof_area_input = self.create_labeled_input(
            "Roof Area (m²):", "e.g., 150", layout, 3
        )
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 10px 0;")
        layout.addWidget(separator, 4, 0, 1, 2)
        
        # Water Quality Parameters Header
        quality_header = QLabel("💧 Water Quality Parameters:")
        quality_header.setStyleSheet("font-weight: bold; color: #2980b9; font-size: 14px; margin-top: 10px;")
        layout.addWidget(quality_header, 5, 0, 1, 2)
        
        # pH
        self.ph_input = self.create_labeled_input(
            "pH Level:", "e.g., 7.0 (Range: 5.5 - 9.5)", layout, 6
        )
        
        # TDS
        self.tds_input = self.create_labeled_input(
            "TDS (ppm):", "e.g., 250 (Typical: 0 - 3000)", layout, 7
        )
        
        # Turbidity
        self.turbidity_input = self.create_labeled_input(
            "Turbidity (NTU):", "e.g., 3.5 (Range: 0 - 10)", layout, 8
        )
        
        # Info note
        info_label = QLabel("ℹ️ All fields are required for accurate prediction")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 11px; margin-top: 10px;")
        layout.addWidget(info_label, 9, 0, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_labeled_input(self, label_text, placeholder, layout, row):
        """Helper to create labeled input field"""
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold;")
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        layout.addWidget(label, row, 0)
        layout.addWidget(input_field, row, 1)
        return input_field
    
    def create_results_section(self):
        """Create results display section"""
        group = QGroupBox("📊 Analysis Results")
        layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(400)
        self.results_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.5;
                padding: 10px;
            }
        """)
        # Enable smooth scrolling
        self.results_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.results_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(self.results_text)
        group.setLayout(layout)
        return group
    
    def toggle_input_method(self):
        """Toggle between location and parameter input"""
        if self.location_radio.isChecked():
            self.location_widget.show()
            self.parameter_scroll.hide()
        else:
            self.location_widget.hide()
            self.parameter_scroll.show()
    
    def load_dataset(self):
        """Load the rainfall dataset"""
        try:
            # Updated path to match your dataset
            self.dataset = pd.read_csv(r"../dataset/final_augmented_rainwater_dataset.csv")
            print(f"Dataset loaded successfully! Shape: {self.dataset.shape}")
            print(f"Rainfall types in dataset: {self.dataset['rainfall_type'].unique()}")
        except Exception as e:
            QMessageBox.warning(self, "Dataset Error", 
                              f"Could not load dataset: {str(e)}\n\n"
                              "Please ensure the dataset file is in the correct location.")
    
    def load_models(self):
        """Load machine learning models"""
        try:
            MODEL_DIR = r"../Models"
            
            self.models['ph'] = joblib.load(f"{MODEL_DIR}/ph_model.pkl")
            self.models['tds'] = joblib.load(f"{MODEL_DIR}/tds_model.pkl")
            self.models['turbidity'] = joblib.load(f"{MODEL_DIR}/turbidity_model.pkl")
            self.models['harvestable'] = joblib.load(f"{MODEL_DIR}/harvestable_model.pkl")
            self.models['quantity'] = joblib.load(f"{MODEL_DIR}/harvest_quantity_model.pkl")
            self.encoders = joblib.load(f"{MODEL_DIR}/label_encoders.pkl")
            
            print("Models loaded successfully!")
            print(f"Available rainfall type encodings: {self.encoders['rainfall_type'].classes_}")
        except Exception as e:
            QMessageBox.warning(self, "Model Error", 
                              f"Could not load models: {str(e)}\n\n"
                              "Please ensure model files are in the correct directory.")
    
    def analyze_data(self):
        """Main analysis function"""
        if self.location_radio.isChecked():
            self.analyze_by_location()
        else:
            self.analyze_by_parameters()
    
    def analyze_by_location(self):
        """Analyze data based on location input"""
        if self.dataset is None:
            QMessageBox.warning(self, "Error", "Dataset not loaded!")
            return
        
        city = self.city_input.text().strip()
        district = self.district_input.text().strip()
        state = self.state_input.text().strip()
        
        if not all([city, district, state]):
            QMessageBox.warning(self, "Input Error", 
                              "Please enter City, District, and State!")
            return
        
        # Case-insensitive search
        mask = (
            self.dataset['city'].str.lower() == city.lower()
        ) & (
            self.dataset['district'].str.lower() == district.lower()
        ) & (
            self.dataset['state'].str.lower() == state.lower()
        )
        
        result = self.dataset[mask]
        
        if result.empty:
            QMessageBox.warning(self, "Not Found", 
                              f"No data found for:\n{city}, {district}, {state}\n\n"
                              "Please check the spelling and try again.")
            return
        
        # Get the first matching record
        data = result.iloc[0]
        self.display_results(data)
    
    def analyze_by_parameters(self):
        """Analyze data based on direct parameter input - WITH ALL 7 FEATURES"""
        if not self.models:
            QMessageBox.warning(self, "Error", "Models not loaded!")
            return
        
        try:
            # Get input values and validate
            rainfall_intensity_text = self.rainfall_intensity_input.text().strip()
            raindrop_size_text = self.raindrop_size_input.text().strip()
            roof_area_text = self.roof_area_input.text().strip()
            ph_text = self.ph_input.text().strip()
            tds_text = self.tds_input.text().strip()
            turbidity_text = self.turbidity_input.text().strip()
            
            # Check if fields are empty
            if not all([rainfall_intensity_text, raindrop_size_text, roof_area_text, 
                       ph_text, tds_text, turbidity_text]):
                QMessageBox.warning(self, "Input Error", 
                                  "Please fill in all required fields:\n"
                                  "• Rainfall Intensity\n"
                                  "• Raindrop Size\n"
                                  "• Rainfall Type\n"
                                  "• Roof Area\n"
                                  "• pH Level\n"
                                  "• TDS\n"
                                  "• Turbidity")
                return
            
            # Convert to float
            try:
                rainfall_intensity = float(rainfall_intensity_text)
                raindrop_size = float(raindrop_size_text)
                roof_area = float(roof_area_text)
                ph = float(ph_text)
                tds = float(tds_text)
                turbidity = float(turbidity_text)
            except ValueError as ve:
                QMessageBox.warning(self, "Input Error", 
                                  f"Invalid numeric value entered.\n\n"
                                  f"Please ensure all values are valid numbers.\n"
                                  f"Use decimal point (.) not comma (,)\n\n"
                                  f"Error: {str(ve)}")
                return
            
            # Validate ranges
            if rainfall_intensity <= 0 or rainfall_intensity > 100:
                QMessageBox.warning(self, "Input Error", 
                                  "Rainfall Intensity should be between 0 and 100 mm/hr")
                return
            
            if raindrop_size <= 0 or raindrop_size > 10:
                QMessageBox.warning(self, "Input Error", 
                                  "Raindrop Size should be between 0 and 10 mm")
                return
            
            if roof_area <= 0 or roof_area > 1000:
                QMessageBox.warning(self, "Input Error", 
                                  "Roof Area should be between 0 and 1000 m²")
                return
            
            if ph < 0 or ph > 14:
                QMessageBox.warning(self, "Input Error", 
                                  "pH should be between 0 and 14")
                return
            
            if tds < 0 or tds > 5000:
                QMessageBox.warning(self, "Input Error", 
                                  "TDS should be between 0 and 5000 ppm")
                return
            
            if turbidity < 0 or turbidity > 100:
                QMessageBox.warning(self, "Input Error", 
                                  "Turbidity should be between 0 and 100 NTU")
                return
            
            rainfall_type = self.rainfall_type_combo.currentText()
            
            print(f"\n{'='*60}")
            print(f"DEBUG - Input values:")
            print(f"  Rainfall Intensity: {rainfall_intensity}")
            print(f"  Raindrop Size: {raindrop_size}")
            print(f"  Rainfall Type: {rainfall_type}")
            print(f"  Roof Area: {roof_area}")
            print(f"  pH: {ph}")
            print(f"  TDS: {tds}")
            print(f"  Turbidity: {turbidity}")
            
            # Encode rainfall type
            try:
                rainfall_type_encoded = self.encoders['rainfall_type'].transform([rainfall_type])[0]
                print(f"  Encoded Rainfall Type: {rainfall_type_encoded}")
            except Exception as e:
                QMessageBox.critical(self, "Encoding Error", 
                                   f"Error encoding rainfall type '{rainfall_type}':\n{str(e)}\n\n"
                                   f"Available types: {self.encoders['rainfall_type'].classes_}")
                return
            
            # Prepare features for prediction with ALL 7 features
            # Order: [rainfall_intensity, raindrop_size, rainfall_type_encoded, roof_area, ph, tds, turbidity]
            features = np.array([[rainfall_intensity, raindrop_size, rainfall_type_encoded, 
                                 roof_area, ph, tds, turbidity]])
            print(f"  Features array shape: {features.shape}")
            print(f"  Features array: {features}")
            print(f"{'='*60}\n")
            
            # Make predictions
            try:
                # For direct parameter input, we're predicting harvestable and quantity
                # pH, TDS, Turbidity are provided as inputs, not predicted
                harvestable = self.models['harvestable'].predict(features)[0]
                quantity = self.models['quantity'].predict(features)[0]
                
                print(f"DEBUG - Predictions:")
                print(f"  Harvestable: {harvestable}")
                print(f"  Quantity: {quantity}")
                
            except Exception as e:
                QMessageBox.critical(self, "Prediction Error", 
                                   f"Error during model prediction:\n{str(e)}\n\n"
                                   f"Please check that models are compatible with the input features.")
                import traceback
                traceback.print_exc()
                return
            
            # Calculate energy (approximate formula based on dataset pattern)
            energy = rainfall_intensity * roof_area * 9.8 * 0.001
            
            # Create a result dictionary
            result_data = {
                'rainfall_intensity_mm_hr': rainfall_intensity,
                'raindrop_size_mm': raindrop_size,
                'rainfall_type': rainfall_type,
                'roof_area_m2': roof_area,
                'ph': ph,
                'tds': tds,
                'turbidity': turbidity,
                'harvestable': harvestable,
                'harvest_quantity_liters': quantity,
                'rain_energy_joules': energy
            }
            
            self.display_results(pd.Series(result_data), predicted=True)
            
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", 
                               f"An unexpected error occurred:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def zoom_in(self):
        """Increase zoom level"""
        current = self.zoom_slider.value()
        self.zoom_slider.setValue(min(200, current + 10))
    
    def zoom_out(self):
        """Decrease zoom level"""
        current = self.zoom_slider.value()
        self.zoom_slider.setValue(max(50, current - 10))
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_slider.setValue(100)
    
    def update_zoom(self, value):
        """Update the zoom level of results text"""
        self.current_zoom = value
        self.zoom_percent_label.setText(f"{value}%")
        
        # Calculate font size based on zoom (base size is 13px at 100%)
        base_font_size = 13
        new_font_size = int(base_font_size * (value / 100))
        
        # Update the results text style with new font size
        self.results_text.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {new_font_size}px;
                line-height: 1.5;
                padding: 10px;
            }}
        """)
        
        # Preserve scroll position
        scrollbar = self.results_text.verticalScrollBar()
        current_pos = scrollbar.value()
        max_pos = scrollbar.maximum()
        
        # If we were at the bottom, stay at the bottom
        if current_pos == max_pos:
            scrollbar.setValue(scrollbar.maximum())
    
    def display_results(self, data, predicted=False):
        """Display analysis results with formatting"""
        # Store current scroll position
        scrollbar = self.results_text.verticalScrollBar()
        
        html_output = """
        <div style='font-family: Arial; line-height: 1.8; padding: 10px;'>
        <h2 style='color: #2980b9; border-bottom: 3px solid #3498db; padding-bottom: 10px;'>
        ⚡ Analysis Results {}
        </h2>
        """.format("(Predicted)" if predicted else "(From Dataset)")
        
        # Input Parameters Section
        html_output += """
        <h3 style='color: #16a085; margin-top: 20px;'>📥 Input Parameters</h3>
        <table style='width: 100%; border-collapse: collapse;'>
        """
        
        if not predicted:
            html_output += f"""
            <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>Location:</b></td>
                <td style='padding: 8px;'>{data.get('city', 'N/A')}, {data.get('district', 'N/A')}, {data.get('state', 'N/A')}</td></tr>
            """
        
        html_output += f"""
        <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>Rainfall Intensity:</b></td>
            <td style='padding: 8px;'>{data['rainfall_intensity_mm_hr']:.2f} mm/hr</td></tr>
        <tr><td style='padding: 8px;'><b>Raindrop Size:</b></td>
            <td style='padding: 8px;'>{data['raindrop_size_mm']:.2f} mm</td></tr>
        <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>Rainfall Type:</b></td>
            <td style='padding: 8px;'>{data['rainfall_type']}</td></tr>
        <tr><td style='padding: 8px;'><b>Roof Area:</b></td>
            <td style='padding: 8px;'>{data['roof_area_m2']:.2f} m²</td></tr>
        </table>
        """
        
        # Water Quality Parameters Section
        html_output += """
        <h3 style='color: #16a085; margin-top: 20px;'>💧 Water Quality Parameters</h3>
        <table style='width: 100%; border-collapse: collapse;'>
        """
        
        # pH - Handle missing values
        if pd.notna(data['ph']):
            ph_value = data['ph']
            ph_status = self.get_ph_status(ph_value)
            html_output += f"""
            <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>pH:</b></td>
                <td style='padding: 8px;'>{ph_value:.2f} {ph_status}</td></tr>
            <tr><td colspan='2' style='padding: 5px 8px; font-size: 11px; color: #7f8c8d;'>
                Normal Range: 6.5 - 8.5</td></tr>
            """
        else:
            html_output += f"""
            <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>pH:</b></td>
                <td style='padding: 8px;'><span style='color: #95a5a6;'>Not Available</span></td></tr>
            <tr><td colspan='2' style='padding: 5px 8px; font-size: 11px; color: #7f8c8d;'>
                Normal Range: 6.5 - 8.5</td></tr>
            """
        
        # TDS
        tds_value = data['tds']
        tds_status = self.get_tds_status(tds_value)
        html_output += f"""
        <tr><td style='padding: 8px;'><b>TDS (Total Dissolved Solids):</b></td>
            <td style='padding: 8px;'>{tds_value:.2f} ppm {tds_status}</td></tr>
        <tr><td colspan='2' style='padding: 5px 8px; font-size: 11px; color: #7f8c8d;'>
            Excellent: &lt; 300 ppm | Good: 300-600 ppm | Fair: 600-900 ppm | Poor: &gt; 900 ppm</td></tr>
        """
        
        # Turbidity
        turb_value = data['turbidity']
        turb_status = self.get_turbidity_status(turb_value)
        html_output += f"""
        <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>Turbidity:</b></td>
            <td style='padding: 8px;'>{turb_value:.2f} NTU {turb_status}</td></tr>
        <tr><td colspan='2' style='padding: 5px 8px; font-size: 11px; color: #7f8c8d;'>
            Excellent: &lt; 1 NTU | Good: 1-5 NTU | Fair: 5-10 NTU | Poor: &gt; 10 NTU</td></tr>
        </table>
        """
        
        # Harvesting Information Section
        html_output += """
        <h3 style='color: #16a085; margin-top: 20px;'>🌊 Harvesting Information</h3>
        <table style='width: 100%; border-collapse: collapse;'>
        """
        
        harvestable = data['harvestable']
        harvest_status = "✅ <span style='color: #27ae60; font-weight: bold;'>YES</span>" if harvestable == 1 else "❌ <span style='color: #e74c3c; font-weight: bold;'>NO</span>"
        
        html_output += f"""
        <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>Harvestable:</b></td>
            <td style='padding: 8px;'>{harvest_status}</td></tr>
        <tr><td style='padding: 8px;'><b>Harvest Quantity:</b></td>
            <td style='padding: 8px;'><b style='color: #2980b9; font-size: 16px;'>{data['harvest_quantity_liters']:.2f} Liters</b></td></tr>
        </table>
        """
        
        # Energy Information Section
        html_output += f"""
        <h3 style='color: #16a085; margin-top: 20px;'>⚡ Energy Generation</h3>
        <table style='width: 100%; border-collapse: collapse;'>
        <tr><td style='padding: 8px; background-color: #ecf0f1;'><b>Rain Energy:</b></td>
            <td style='padding: 8px;'><b style='color: #e67e22; font-size: 16px;'>{data['rain_energy_joules']:.2f} Joules</b></td></tr>
        <tr><td colspan='2' style='padding: 5px 8px; font-size: 11px; color: #7f8c8d;'>
            Equivalent to: {data['rain_energy_joules'] / 3600:.4f} Watt-hours (Wh)</td></tr>
        </table>
        """
        
        # Recommendations
        html_output += """
        <h3 style='color: #16a085; margin-top: 20px;'>💡 Recommendations</h3>
        <div style='padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px; margin-bottom: 20px;'>
        """
        
        if harvestable == 1:
            html_output += "<p style='margin: 5px 0;'>✓ Water quality is suitable for harvesting.</p>"
            if pd.notna(data['ph']):
                ph_value = data['ph']
                if ph_value < 6.5 or ph_value > 8.5:
                    html_output += "<p style='margin: 5px 0;'>⚠ pH adjustment recommended before use.</p>"
            if tds_value > 600:
                html_output += "<p style='margin: 5px 0;'>⚠ Consider filtration to reduce TDS levels.</p>"
            if turb_value > 5:
                html_output += "<p style='margin: 5px 0;'>⚠ Filtration recommended to reduce turbidity.</p>"
        else:
            html_output += "<p style='margin: 5px 0;'>✗ Water quality is not suitable for harvesting without treatment.</p>"
            html_output += "<p style='margin: 5px 0;'>• Advanced filtration and treatment required.</p>"
        
        html_output += "</div></div>"
        
        self.results_text.setHtml(html_output)
        
        # Scroll to top of results
        self.results_text.moveCursor(QTextCursor.Start)
        self.results_text.ensureCursorVisible()
    
    def get_ph_status(self, ph):
        """Get pH status indicator"""
        if 6.5 <= ph <= 8.5:
            return "✅ (Normal)"
        elif 6.0 <= ph < 6.5 or 8.5 < ph <= 9.0:
            return "⚠️ (Borderline)"
        else:
            return "❌ (Abnormal)"
    
    def get_tds_status(self, tds):
        """Get TDS status indicator"""
        if tds < 300:
            return "✅ (Excellent)"
        elif tds < 600:
            return "✅ (Good)"
        elif tds < 900:
            return "⚠️ (Fair)"
        else:
            return "❌ (Poor)"
    
    def get_turbidity_status(self, turb):
        """Get turbidity status indicator"""
        if turb < 1:
            return "✅ (Excellent)"
        elif turb < 5:
            return "✅ (Good)"
        elif turb < 10:
            return "⚠️ (Fair)"
        else:
            return "❌ (Poor)"
    
    def clear_all(self):
        """Clear all input fields and results"""
        # Clear location inputs
        self.city_input.clear()
        self.district_input.clear()
        self.state_input.clear()
        
        # Clear parameter inputs
        self.rainfall_intensity_input.clear()
        self.raindrop_size_input.clear()
        self.roof_area_input.clear()
        self.rainfall_type_combo.setCurrentIndex(0)
        self.ph_input.clear()
        self.tds_input.clear()
        self.turbidity_input.clear()
        
        # Clear results
        self.results_text.clear()
        self.results_text.setPlaceholderText("Results will appear here after analysis...")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = RainwaterHarvestingUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()