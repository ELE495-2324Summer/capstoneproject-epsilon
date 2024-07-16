import ipywidgets.widgets as widgets
from jetbot import Camera, bgr8_to_jpeg, Robot
import pytesseract
from PIL import Image
import cv2
import numpy as np
import threading
from manevra_son import StopProcessing  # Import StopProcessing from manevra_son
from collision_final import park_between_red_lines
import time


def process_image(change):
    global last_image
    last_image = change['new']

def parking(target_text, camera, robot, park_boolean, park_numarası):
    
    try:
    
        label_widget = widgets.Label()
        # Tesseract konfigürasyonu
        custom_config = r'--oem 3 --psm 6 outputbase digits'

        camera.observe(process_image, names='value')

        start_time = time.time()
#         kernel = np.ones((5, 5), np.uint8)  # A 5x5 matrix of ones


        while time.time() - start_time < 5:
                img = camera.value
                # Görüntüyü OpenCV formatına dönüştürme
                image_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                # Görüntünün sadece alt kısmını kırpma
                height, width, _ = image_bgr.shape
                crop_x1 = int(width * 0.35)  # Sol kırpma oranı
                crop_y1 = 0  # Üstten kırpma yok
                crop_x2 = int(width * 0.65)  # Sağ kırpma oranı
                crop_y2 = int(height * 0.65)  # Alttan daha fazla kırpma oranı
                cropped_image = image_bgr[crop_y1:crop_y2, crop_x1:crop_x2]

                # Görüntüyü gri tonlamaya çevirme
                gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
#                 blur = cv2.GaussianBlur(gray_image, (3, 3), 0)
#                 binary = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
#                 dilated_image = cv2.dilate(binary, kernel, iterations=1)


                # Tesseract ile sadece sayı tanıma
                text = pytesseract.image_to_string(gray_image, config=custom_config)

                # Sadece sayıları filtreleme
                filtered_text = ''.join(filter(str.isdigit, text))
                park_numarası.append(filtered_text)

                # Tanınan metni widget üzerinde gösterme
                label_widget.value = f'Text: {filtered_text.strip()}'           

                if filtered_text == target_text:
                    time.sleep(0.5)
                    park_between_red_lines(camera, robot, park_boolean)
                    break

        print("Aranan Plaka Bulunamadı")
        park_boolean.append(True)
        robot.stop()
        
    except StopProcessing:
        raise
