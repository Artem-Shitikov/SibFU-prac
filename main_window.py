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
    QSpinBox,
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

        channels_layout = QHBoxLayout()
        root_layout.addLayout(channels_layout)

        channels_layout.addWidget(QLabel("Показать канал:"))
        for channel in ("R", "G", "B"):
            button = QPushButton(channel)
            button.clicked.connect(lambda checked=False, ch=channel: self.on_show_channel(ch))
            channels_layout.addWidget(button)
        channels_layout.addStretch()

        crop_layout = QHBoxLayout()
        root_layout.addLayout(crop_layout)

        crop_layout.addWidget(QLabel("Обрезка: X1"))
        self.crop_x1_spin = QSpinBox()
        self.crop_x1_spin.setRange(0, 100000)
        crop_layout.addWidget(self.crop_x1_spin)

        crop_layout.addWidget(QLabel("Y1"))
        self.crop_y1_spin = QSpinBox()
        self.crop_y1_spin.setRange(0, 100000)
        crop_layout.addWidget(self.crop_y1_spin)

        crop_layout.addWidget(QLabel("X2"))
        self.crop_x2_spin = QSpinBox()
        self.crop_x2_spin.setRange(0, 100000)
        self.crop_x2_spin.setValue(100)
        crop_layout.addWidget(self.crop_x2_spin)

        crop_layout.addWidget(QLabel("Y2"))
        self.crop_y2_spin = QSpinBox()
        self.crop_y2_spin.setRange(0, 100000)
        self.crop_y2_spin.setValue(100)
        crop_layout.addWidget(self.crop_y2_spin)

        self.crop_button = QPushButton("Обрезать")
        self.crop_button.clicked.connect(self.on_crop)
        crop_layout.addWidget(self.crop_button)

        crop_layout.addStretch()

        blur_layout = QHBoxLayout()
        root_layout.addLayout(blur_layout)

        blur_layout.addWidget(QLabel("Усреднение: размер ядра"))
        self.blur_kernel_spin = QSpinBox()
        self.blur_kernel_spin.setRange(1, 200)
        self.blur_kernel_spin.setValue(5)
        blur_layout.addWidget(self.blur_kernel_spin)

        self.blur_button = QPushButton("Усреднить")
        self.blur_button.clicked.connect(self.on_blur)
        blur_layout.addWidget(self.blur_button)

        blur_layout.addStretch()

        circle_layout = QHBoxLayout()
        root_layout.addLayout(circle_layout)

        circle_layout.addWidget(QLabel("Круг: X"))
        self.circle_x_spin = QSpinBox()
        self.circle_x_spin.setRange(0, 100000)
        circle_layout.addWidget(self.circle_x_spin)

        circle_layout.addWidget(QLabel("Y"))
        self.circle_y_spin = QSpinBox()
        self.circle_y_spin.setRange(0, 100000)
        circle_layout.addWidget(self.circle_y_spin)

        circle_layout.addWidget(QLabel("Радиус"))
        self.circle_radius_spin = QSpinBox()
        self.circle_radius_spin.setRange(1, 100000)
        self.circle_radius_spin.setValue(30)
        circle_layout.addWidget(self.circle_radius_spin)

        self.circle_button = QPushButton("Нарисовать круг")
        self.circle_button.clicked.connect(self.on_draw_circle)
        circle_layout.addWidget(self.circle_button)

        circle_layout.addStretch()

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

    def on_show_channel(self, channel: str):
        if self.image is None:
            QMessageBox.warning(self, "Нет изображения", "Сначала загрузите изображение или сделайте снимок с камеры.")
            return

        result = image_ops.extract_channel(self.image, channel)
        self.show_image(result)
        self.statusBar().showMessage(f"Показан канал: {channel}")

    def on_crop(self):
        if self.image is None:
            QMessageBox.warning(self, "Нет изображения", "Сначала загрузите изображение или сделайте снимок с камеры.")
            return

        x1 = self.crop_x1_spin.value()
        y1 = self.crop_y1_spin.value()
        x2 = self.crop_x2_spin.value()
        y2 = self.crop_y2_spin.value()

        try:
            result = image_ops.crop_image(self.image, x1, y1, x2, y2)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка обрезки", str(e))
            self.statusBar().showMessage("Ошибка при обрезке изображения")
            return

        self.show_image(result)
        self.statusBar().showMessage(f"Обрезано: ({x1}, {y1}) - ({x2}, {y2})")

    def on_blur(self):
        if self.image is None:
            QMessageBox.warning(self, "Нет изображения", "Сначала загрузите изображение или сделайте снимок с камеры.")
            return

        kernel_size = self.blur_kernel_spin.value()

        try:
            result = image_ops.blur_image(self.image, kernel_size)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка усреднения", str(e))
            self.statusBar().showMessage("Ошибка при усреднении изображения")
            return

        self.show_image(result)
        self.statusBar().showMessage(f"Усреднение с ядром {kernel_size}x{kernel_size}")

    def on_draw_circle(self):
        if self.image is None:
            QMessageBox.warning(self, "Нет изображения", "Сначала загрузите изображение или сделайте снимок с камеры.")
            return

        x = self.circle_x_spin.value()
        y = self.circle_y_spin.value()
        radius = self.circle_radius_spin.value()

        try:
            result = image_ops.draw_circle(self.image, x, y, radius)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка рисования круга", str(e))
            self.statusBar().showMessage("Ошибка при рисовании круга")
            return

        self.show_image(result)
        self.statusBar().showMessage(f"Круг: центр ({x}, {y}), радиус {radius}")

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
