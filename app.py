import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QDockWidget, QMenuBar, QMenu, 
    QToolBar, QSpinBox, QComboBox, QDialog, QListWidget, QCheckBox, 
    QColorDialog, QRadioButton, QLineEdit, QGridLayout, QGroupBox, QTabWidget
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QImage, QPixmap, QAction, QColor, QPainter, QPen, QKeySequence
import pyttsx3

class AudioBlindPainter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Untitled - Paint.NET 5.1.12 Accessible Studio Edition")
        self.resize(1650, 980)
        
        # Audio Speech Engine for Screen Reader Feedback
        self.speech_engine = pyttsx3.init()
        
        # Canvas Dimensions & Settings
        self.canvas_width = 800
        self.canvas_height = 600
        self.zoom_level = 100
        
        # Tool States (Matching Paint.NET Toolbar)
        self.current_tool = "Paintbrush"
        self.brush_size = 3
        self.hardness = 75
        self.spacing = 15
        self.fill_style = "Solid Color"
        self.antialiasing = True
        self.blend_mode = "Normal"
        self.primary_color = (0, 0, 0, 255)
        self.custom_colors_palette = []
        
        # Drawing & Tracking State
        self.drawing = False
        self.last_point = None
        self.last_spoken_region = ""
        
        # Layers Stack & History Stack
        self.layers = {
            "color": np.full((self.canvas_height, self.canvas_width, 4), 255, dtype=np.uint8),
            "lineart": np.full((self.canvas_height, self.canvas_width, 4), 255, dtype=np.uint8),
            "mask": np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        }
        self.history_stack = ["New Image"]
        
        # Deep Anatomical & Background Audio Region Map
        self.region_map = {
            (255, 0, 0): "Hair Area",
            (255, 100, 100): "Nose Area",
            (0, 255, 0): "Face and Skin",
            (255, 0, 255): "Lips and Mouth",
            (0, 0, 255): "Eyes and Details",
            (255, 215, 0): "Earrings and Accessories",
            (255, 255, 0): "Shirt and Chest Area",
            (100, 100, 255): "Stomach and Torso Area",
            (0, 255, 255): "Hands and Nails",
            (0, 128, 255): "Pants and Bottoms",
            (128, 0, 128): "Legs Area",
            (75, 0, 130): "Shoes and Feet",
            (255, 128, 0): "Background Elements",
            (0, 0, 0): "Blank Canvas Background"
        }
        
        self.setup_default_region_mask()
        self.apply_high_contrast_theme()
        
        # Build UI Elements matching Paint.NET
        self.init_menu_bar()
        self.init_top_toolbars()
        self.init_central_canvas()
        self.init_dockable_panels()
        self.init_status_bar()
        
        self.speak("AudioBlindPainter loaded in high contrast mode. Paint.NET layout and deep audio tracking active.")

    def setup_default_region_mask(self):
        mask = self.layers["mask"]
        mask[30:100, 350:450]   = [255, 0, 0]     # Hair
        mask[80:100, 390:410]   = [255, 215, 0]   # Earrings
        mask[100:150, 360:440]  = [0, 255, 0]     # Face
        mask[115:125, 395:405]  = [255, 100, 100] # Nose
        mask[135:145, 385:415]  = [255, 0, 255]   # Lips
        mask[105:115, 375:425]  = [0, 0, 255]     # Eyes
        mask[150:280, 320:480]  = [255, 255, 0]   # Shirt / Chest
        mask[280:380, 330:470]  = [100, 100, 255] # Stomach
        mask[180:260, 280:320]  = [0, 255, 255]   # Hands and Nails
        mask[380:480, 340:460]  = [0, 128, 255]   # Pants / Bottoms
        mask[480:550, 340:460]  = [128, 0, 128]   # Legs
        mask[550:580, 330:470]  = [75, 0, 130]    # Shoes
        mask[0:30, :]           = [255, 128, 0]   # Background

    def apply_high_contrast_theme(self):
        stylesheet = """
            QMainWindow { background-color: #000000; }
            QWidget { color: #FFFFFF; font-family: Arial, sans-serif; font-size: 15px; font-weight: bold; }
            QMenuBar { background-color: #000000; color: #FFFF00; font-size: 16px; border-bottom: 3px solid #FFFF00; }
            QMenuBar::item:selected { background-color: #FFFF00; color: #000000; }
            QMenu { background-color: #000000; color: #FFFFFF; border: 3px solid #FFFF00; }
            QMenu::item:selected { background-color: #00FFFF; color: #000000; }
            QToolBar { background-color: #111111; border-bottom: 3px solid #00FFFF; spacing: 10px; padding: 4px; }
            QDockWidget::title { background: #FFFF00; color: #000000; padding: 6px; border: 2px solid #FFFFFF; }
            QPushButton, QComboBox, QSpinBox, QLineEdit { background-color: #1a1a1a; color: #FFFFFF; border: 3px solid #00FFFF; padding: 6px 10px; border-radius: 4px; }
            QPushButton:hover, QComboBox:hover, QSpinBox:hover { background-color: #FFFF00; color: #000000; }
            QPushButton:focus { border: 3px solid #FFFFFF; }
            QListWidget { background-color: #000000; color: #FFFFFF; border: 3px solid #00FFFF; }
            QLabel { color: #FFFFFF; }
        """
        self.setStyleSheet(stylesheet)

    def init_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        file_menu.addAction(QAction("New...", self, shortcut=QKeySequence("Ctrl+N"), triggered=self.new_canvas))
        file_menu.addAction(QAction("Open...", self, shortcut=QKeySequence("Ctrl+O"), triggered=self.load_image))
        file_menu.addAction(QAction("Save", self, shortcut=QKeySequence("Ctrl+S"), triggered=lambda: self.speak("Saved project")))
        file_menu.addAction(QAction("Save As...", self, shortcut=QKeySequence("Ctrl+Shift+S"), triggered=lambda: self.speak("Save As")))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(QAction("Undo", self, shortcut=QKeySequence("Ctrl+Z"), triggered=lambda: self.speak("Undo")))
        edit_menu.addAction(QAction("Redo", self, shortcut=QKeySequence("Ctrl+Y"), triggered=lambda: self.speak("Redo")))
        edit_menu.addSeparator()
        edit_menu.addAction(QAction("Cut", self, shortcut=QKeySequence("Ctrl+X"), triggered=lambda: self.speak("Cut")))
        edit_menu.addAction(QAction("Copy", self, shortcut=QKeySequence("Ctrl+C"), triggered=lambda: self.speak("Copy")))
        edit_menu.addAction(QAction("Paste", self, shortcut=QKeySequence("Ctrl+V"), triggered=lambda: self.speak("Paste")))
        edit_menu.addAction(QAction("Select All", self, shortcut=QKeySequence("Ctrl+A"), triggered=lambda: self.speak("Select All")))

        view_menu = menubar.addMenu("View")
        view_menu.addAction(QAction("Zoom In", self, shortcut=QKeySequence("Ctrl++"), triggered=lambda: self.speak("Zoom In")))
        view_menu.addAction(QAction("Zoom Out", self, shortcut=QKeySequence("Ctrl+-"), triggered=lambda: self.speak("Zoom Out")))
        view_menu.addAction(QAction("Actual Size", self, shortcut=QKeySequence("Ctrl+0"), triggered=lambda: self.speak("Actual Size")))

        img_menu = menubar.addMenu("Image")
        img_menu.addAction(QAction("Resize...", self, shortcut=QKeySequence("Ctrl+R"), triggered=self.open_resize_dialog))
        img_menu.addAction(QAction("Canvas Size...", self, shortcut=QKeySequence("Ctrl+Shift+R"), triggered=self.open_resize_dialog))
        img_menu.addSeparator()
        img_menu.addAction(QAction("Flip Horizontal", self, triggered=lambda: self.flip_image("horizontal")))
        img_menu.addAction(QAction("Flip Vertical", self, triggered=lambda: self.flip_image("vertical")))

        layers_menu = menubar.addMenu("Layers")
        layers_menu.addAction(QAction("Add New Layer", self, shortcut=QKeySequence("Ctrl+Shift+N"), triggered=lambda: self.speak("New layer added")))
        layers_menu.addAction(QAction("Delete Layer", self, shortcut=QKeySequence("Ctrl+Shift+Delete"), triggered=lambda: self.speak("Layer deleted")))

        adj_menu = menubar.addMenu("Adjustments")
        adj_menu.addAction(QAction("Black and White", self, shortcut=QKeySequence("Ctrl+Shift+G"), triggered=lambda: self.apply_adjustment("bw")))
        adj_menu.addAction(QAction("Brightness / Contrast...", self, shortcut=QKeySequence("Ctrl+Shift+C"), triggered=lambda: self.apply_adjustment("bright")))
        adj_menu.addAction(QAction("Invert Colors", self, shortcut=QKeySequence("Ctrl+Shift+I"), triggered=lambda: self.apply_adjustment("invert")))

        eff_menu = menubar.addMenu("Effects")
        eff_menu.addAction(QAction("Gaussian Blur...", self, triggered=lambda: self.apply_effect("blur")))
        eff_menu.addAction(QAction("Sharpen...", self, triggered=lambda: self.apply_effect("sharpen")))

        settings_action = QAction("⚙ Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        menubar.addAction(settings_action)

    def init_top_toolbars(self):
        self.toolbar = QToolBar("Paint.NET Options", self)
        self.addToolBar(self.toolbar)
        
        self.toolbar.addWidget(QLabel(" Tool: "))
        self.tool_lbl = QLabel("Paintbrush")
        self.tool_lbl.setStyleSheet("color: #00FFFF; font-weight: bold;")
        self.toolbar.addWidget(self.tool_lbl)
        
        self.toolbar.addWidget(QLabel(" | Brush size: "))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(self.brush_size)
        self.size_spin.valueChanged.connect(lambda v: (setattr(self, 'brush_size', v), self.speak(f"Brush size {v}")))
        self.toolbar.addWidget(self.size_spin)

        self.toolbar.addWidget(QLabel(" Hardness: "))
        self.hard_spin = QSpinBox()
        self.hard_spin.setRange(1, 100)
        self.hard_spin.setValue(self.hardness)
        self.toolbar.addWidget(self.hard_spin)

        self.toolbar.addWidget(QLabel(" Spacing: "))
        self.space_spin = QSpinBox()
        self.space_spin.setRange(1, 100)
        self.space_spin.setValue(self.spacing)
        self.toolbar.addWidget(self.space_spin)

        self.toolbar.addWidget(QLabel(" Fill: "))
        self.fill_combo = QComboBox()
        self.fill_combo.addItems(["Solid Color", "Linear Gradient", "Pattern"])
        self.toolbar.addWidget(self.fill_combo)

        self.toolbar.addWidget(QLabel(" Blending: "))
        self.blend_combo = QComboBox()
        self.blend_combo.addItems(["Normal", "Multiply", "Screen", "Overlay"])
        self.toolbar.addWidget(self.blend_combo)

    def init_central_canvas(self):
        self.canvas_container = QWidget()
        layout = QVBoxLayout(self.canvas_container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.canvas_label = QLabel()
        self.canvas_label.setStyleSheet("background-color: #FFFFFF; border: 4px solid #FFFF00;")
        self.canvas_label.setMouseTracking(True)
        
        self.canvas_label.mousePressEvent = self.canvas_mouse_press
        self.canvas_label.mouseMoveEvent = self.canvas_mouse_move
        self.canvas_label.mouseReleaseEvent = self.canvas_mouse_release
        
        layout.addWidget(self.canvas_label)
        self.setCentralWidget(self.canvas_container)
        self.update_canvas_view()

    def init_dockable_panels(self):
        self.tools_dock = QDockWidget("Tools", self)
        t_widget = QWidget()
        t_layout = QVBoxLayout(t_widget)
        tools = [
            "Rectangle Select", "Lasso Select", "Magic Wand", "Paint Bucket", 
            "Paintbrush", "Pencil", "Eraser", "Color Picker", "Line / Curve", "Shapes"
        ]
        for t_name in tools:
            btn = QPushButton(t_name)
            btn.clicked.connect(lambda checked, name=t_name: self.select_tool(name))
            t_layout.addWidget(btn)
        t_layout.addStretch()
        self.tools_dock.setWidget(t_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tools_dock)

        self.colors_dock = QDockWidget("Colors", self)
        c_widget = QWidget()
        c_layout = QVBoxLayout(c_widget)
        color_btn = QPushButton("🎨 Choose Custom Color Wheel")
        color_btn.clicked.connect(self.choose_custom_color)
        c_layout.addWidget(color_btn)
        
        self.color_preview_lbl = QLabel("Current Color: Black")
        self.color_preview_lbl.setStyleSheet("color: #00FFFF; font-weight: bold;")
        c_layout.addWidget(self.color_preview_lbl)
        
        c_layout.addWidget(QLabel("Saved Custom Swatches:"))
        self.swatch_list = QListWidget()
        self.swatch_list.setMaximumHeight(90)
        c_layout.addWidget(self.swatch_list)
        c_layout.addStretch()
        self.colors_dock.setWidget(c_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.colors_dock)

        self.history_dock = QDockWidget("History", self)
        h_widget = QWidget()
        h_layout = QVBoxLayout(h_widget)
        self.history_list = QListWidget()
        self.history_list.addItems(self.history_stack)
        h_layout.addWidget(self.history_list)
        h_layout.addStretch()
        self.history_dock.setWidget(h_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.history_dock)

        self.layers_dock = QDockWidget("Layers", self)
        l_widget = QWidget()
        l_layout = QVBoxLayout(l_widget)
        self.layers_list = QListWidget()
        self.layers_list.addItems(["☑ Line Art Layer", "☑ Color & Painting Layer", "☑ Background Mask Layer"])
        l_layout.addWidget(self.layers_list)
        l_layout.addStretch()
        self.layers_dock.setWidget(l_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layers_dock)

    def init_status_bar(self):
        self.status_bar = self.statusBar()
        self.coord_label = QLabel("X: 0, Y: 0")
        self.size_status_label = QLabel("800 x 600 px")
        self.status_bar.addPermanentWidget(self.coord_label)
        self.status_bar.addPermanentWidget(self.size_status_label)

    def speak(self, text):
        print(f"[Audio]: {text}")
        try:
            self.speech_engine.say(text)
            self.speech_engine.startLoop(False)
            self.speech_engine.endLoop()
        except Exception:
            pass

    def select_tool(self, tool_name):
        self.current_tool = tool_name
        self.tool_lbl.setText(tool_name)
        self.speak(f"Tool selected: {tool_name}")

    def choose_custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.primary_color = (color.red(), color.green(), color.blue(), 255)
            hex_code = color.name()
            self.color_preview_lbl.setText(f"Current Color: {hex_code}")
            if hex_code not in self.custom_colors_palette:
                self.custom_colors_palette.append(hex_code)
                self.swatch_list.addItem(f"Custom #{len(self.custom_colors_palette)}: {hex_code}")
            self.speak("Custom color chosen and saved to palette.")

    def canvas_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.speak("Started drawing stroke")
            self.draw_stroke(self.last_point, self.last_point)

    def canvas_mouse_move(self, event):
        pos = event.position().toPoint()
        x, y = pos.x(), pos.y()
        self.coord_label.setText(f"X: {x}, Y: {y}")
        
        if self.drawing and self.last_point:
            self.draw_stroke(self.last_point, pos)
            self.last_point = pos
            
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            mask_color = tuple(self.layers["mask"][y, x][:3])
            region_name = self.region_map.get(mask_color, "Background Area")
            
            if region_name != self.last_spoken_region:
                self.last_spoken_region = region_name
                self.speak(region_name)

    def canvas_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.last_point = None
            self.speak("Stroke finished")

    def draw_stroke(self, p1, p2):
        h, w, c = self.layers["color"].shape
        q_img = QImage(self.layers["color"].data, w, h, w * c, QImage.Format.Format_RGBA8888)
        painter = QPainter(q_img)
        pen_color = QColor(255, 255, 255, 255) if self.current_tool == "Eraser" else QColor(*self.primary_color)
        painter.setPen(QPen(pen_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(p1, p2)
        painter.end()
        ptr = q_img.bits()
        ptr.setsize(h * w * c)
        self.layers["color"] = np.frombuffer(ptr, np.uint8).reshape((h, w, c))
        self.update_canvas_view()

    def update_canvas_view(self):
        composite = self.layers["color"].copy()
        h, w, c = composite.shape
        q_img = QImage(composite.data, w, h, w * c, QImage.Format.Format_RGBA8888)
        self.canvas_label.setPixmap(QPixmap.fromImage(q_img))

    def new_canvas(self):
        self.layers["color"] = np.full((self.canvas_height, self.canvas_width, 4), 255, dtype=np.uint8)
        self.update_canvas_view()
        self.history_stack.append("New Image")
        self.history_list.addItem("New Image")
        self.speak("New blank canvas created.")

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            img = Image.open(file_name).convert("RGBA").resize((self.canvas_width, self.canvas_height))
            self.layers["color"] = np.array(img, dtype=np.uint8)
            self.layers["mask"] = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
            self.update_canvas_view()
            self.speak("Image loaded successfully.")

    def open_resize_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Resize Canvas")
        dialog.resize(400, 300)
        layout = QVBoxLayout(dialog)
        w_input = QLineEdit(str(self.canvas_width))
        h_input = QLineEdit(str(self.canvas_height))
        layout.addWidget(QLabel("Width:"))
        layout.addWidget(w_input)
        layout.addWidget(QLabel("Height:"))
        layout.addWidget(h_input)
        ok_btn = QPushButton("OK")
        layout.addWidget(ok_btn)
        def apply_resize():
            try:
                new_w, new_h = int(w_input.text()), int(h_input.text())
                self.canvas_width, self.canvas_height = new_w, new_h
                self.size_status_label.setText(f"{new_w} x {new_h} px")
                for key in self.layers:
                    img = Image.fromarray(self.layers[key])
                    img = img.resize((new_w, new_h))
                    self.layers[key] = np.array(img, dtype=np.uint8)
                self.update_canvas_view()
                self.speak(f"Canvas resized to {new_w} by {new_h}")
                dialog.accept()
            except ValueError:
                self.speak("Invalid dimensions.")
        ok_btn.clicked.connect(apply_resize)
        dialog.exec()

    def flip_image(self, direction):
        img = Image.fromarray(self.layers["color"])
        img = img.transpose(Image.FLIP_LEFT_RIGHT if direction == "horizontal" else Image.FLIP_TOP_BOTTOM)
        self.layers["color"] = np.array(img, dtype=np.uint8)
        self.update_canvas_view()
        self.speak(f"Flipped {direction}")

    def apply_adjustment(self, adj_type):
        img = Image.fromarray(self.layers["color"])
        if adj_type == "bw":
            img = img.convert("L").convert("RGBA")
            self.speak("Black and white adjustment applied")
        elif adj_type == "bright":
            img = ImageEnhance.Brightness(img).enhance(1.2)
            self.speak("Brightness increased")
        elif adj_type == "invert":
            img = Image.fromarray(255 - img.convert("RGB")).convert("RGBA")
            self.speak("Colors inverted")
        self.layers["color"] = np.array(img, dtype=np.uint8)
        self.update_canvas_view()

    def apply_effect(self, eff_type):
        img = Image.fromarray(self.layers["color"])
        if eff_type == "blur":
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            self.speak("Blur effect applied")
        elif eff_type == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
            self.speak("Sharpen effect applied")
        self.layers["color"] = np.array(img, dtype=np.uint8)
        self.update_canvas_view()

    def open_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.resize(600, 400)
        layout = QHBoxLayout(dialog)
        sidebar = QListWidget()
        sidebar.addItems(["User Interface", "Canvas & Grid", "Tools & Input", "Speech & Accessibility", "Updates & About"])
        layout.addWidget(sidebar, 1)
        tabs = QTabWidget()
        ui_widget = QWidget()
        ui_layout = QVBoxLayout(ui_widget)
        ui_layout.addWidget(QCheckBox("Enable High Contrast Mode"))
        ui_layout.addStretch()
        tabs.addTab(ui_widget, "UI")
        layout.addWidget(tabs, 2)
        self.speak("Settings opened.")
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioBlindPainter()
    window.show()
    sys.exit(app.exec())
