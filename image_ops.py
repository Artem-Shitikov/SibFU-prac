import cv2
import numpy as np

CHANNEL_INDEX = {"B": 0, "G": 1, "R": 2}


def load_image(path: str):
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Не удалось открыть файл как изображение: {path}")
    return image

def capture_photo(camera_index: int = 0):
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(
            "Не удалось подключиться к веб-камере. Возможные причины: "
            "камера не подключена, занята другим приложением, "
            "или не выдано разрешение (System Settings -> Privacy & Security -> Camera)."
        )

    ret, frame = camera.read()
    camera.release()

    if not ret:
        raise RuntimeError("Не удалось сделать снимок с веб-камеры")
    return frame


def extract_channel(image: np.ndarray, channel: str) -> np.ndarray:
    if channel not in CHANNEL_INDEX:
        raise ValueError(f"Неизвестный канал: {channel}. Допустимые значения: R, G, B")

    idx = CHANNEL_INDEX[channel]
    result = np.zeros_like(image)
    result[:, :, idx] = image[:, :, idx]
    return result


def crop_image(image: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    height, width = image.shape[:2]

    if not (0 <= x1 < x2 <= width):
        raise ValueError(
            f"Некорректные координаты по X: x1={x1}, x2={x2} (ширина изображения: {width}). "
            f"Должно выполняться 0 <= x1 < x2 <= {width}."
        )

    if not (0 <= y1 < y2 <= height):
        raise ValueError(
            f"Некорректные координаты по Y: y1={y1}, y2={y2} (высота изображения: {height}). "
            f"Должно выполняться 0 <= y1 < y2 <= {height}."
        )

    return image[y1:y2, x1:x2].copy()


def blur_image(image: np.ndarray, kernel_size: int) -> np.ndarray:
    if kernel_size < 1:
        raise ValueError(f"Размер ядра должен быть положительным числом, получено: {kernel_size}")

    return cv2.blur(image, (kernel_size, kernel_size))
