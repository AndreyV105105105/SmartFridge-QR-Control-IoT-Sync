from flask import Flask, render_template, request, jsonify
from pyzbar.pyzbar import decode
from PIL import Image, ImageOps
import io
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_qr_decode(img):
    """Безопасное декодирование QR-кода с обработкой исключений"""
    try:
        # Конвертация в grayscale для лучшего распознавания
        gray_img = img.convert('L')
        return decode(gray_img)
    except Exception as e:
        logger.error(f"Decoding error: {str(e)}")
        return None


def process_image(file_stream):
    """Оптимизированная обработка изображения для мобильных устройств"""
    try:
        img = Image.open(io.BytesIO(file_stream))

        # Удаление EXIF ориентации
        img = ImageOps.exif_transpose(img)

        # Проверка и конвертация формата
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Уменьшение размера для производительности
        w, h = img.size
        img = img.resize((w // 2, h // 2))

        return img
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        return None