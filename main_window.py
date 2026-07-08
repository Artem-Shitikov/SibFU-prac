import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import image_ops


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV Image Editor")
        self.resize(1000, 700)

        self.image = None  # текущее изображение как numpy-массив (BGR) или None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)

        controls_layout = QHBoxLayout()
        root_layout.addLayout(controls_layout)

        self.load_button = QPushButton("Загрузить изображение")
        self.load_button.clicked.connect(self.on_load_image)
        controls_layout.addWidget(self.load_button)

        self.capture_button = QPushButton("Снимок с веб-камеры")
        self.capture_button.clicked.connect(self.on_capture_photo)
        controls_layout.addWidget(self.capture_button)

        controls_layout.addStretch()

        self.image_label = QLabel("Изображение не загружено")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        root_layout.addWidget(self.image_label, stretch=1)

        self.statusBar().showMessage("Готово")

    def on_load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg)",
        )
        if not path:
            return  # пользователь нажал "Отмена"

        try:
            image = image_ops.load_image(path)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))
            self.statusBar().showMessage("Ошибка загрузки изображения")
            return

        self.image = image
        self.show_image(self.image)
        self.statusBar().showMessage(f"Загружено: {path}")

    def on_capture_photo(self):
        try:
            image = image_ops.capture_photo()
        except RuntimeError as e:
            QMessageBox.critical(self, "Ошибка веб-камеры", str(e))
            self.statusBar().showMessage("Ошибка при съёмке с веб-камеры")
            return

        self.image = image
        self.show_image(self.image)
        self.statusBar().showMessage("Снимок с веб-камеры сделан")

    def show_image(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg)

        scaled = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
