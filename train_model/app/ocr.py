# app/ocr.py

import os
from typing import List
import easyocr 

class OCRReader:
    def __init__(self, languages: List[str] = ['en', 'ne'], gpu: bool = False):
        """
        Initialize EasyOCR reader.
        
        :param languages: List of language codes (default is English and Nepali).
        :param gpu: Whether to use GPU (default False).
        """
        self.reader = easyocr.Reader(languages, gpu=gpu)

    def read_text(self, image_path: str) -> str:
        """
        Perform OCR on the given image and return extracted text.
        
        :param image_path: Path to the image file.
        :return: Extracted text as a single string.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        results = self.reader.readtext(image_path, detail=0)  # detail=0 returns just text
        return "\n".join(results)
