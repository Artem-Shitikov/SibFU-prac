import cv2


def load_image(path: str):
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Не удалось открыть файл как изображение: {path}")
    return image
