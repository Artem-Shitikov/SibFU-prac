import cv2


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
