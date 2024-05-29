import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import pywt
import os

def add_watermark(image_path, watermark_path, alpha=0.1):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)

    coeffs_image = pywt.dwt2(image, 'haar')
    LL, (LH, HL, HH) = coeffs_image

    watermark_resized = cv2.resize(watermark, (LL.shape[1], LL.shape[0]))

    LL_wm = LL + alpha * watermark_resized

    coeffs_wm = LL_wm, (LH, HL, HH)
    image_wm = pywt.idwt2(coeffs_wm, 'haar')

    image_wm_resized = cv2.resize(image_wm, (image.shape[1], image.shape[0]))

    output_path = os.path.join(os.getcwd(), 'WatermarkImage.jpg')
    cv2.imwrite(output_path, np.uint8(np.clip(image_wm_resized, 0, 255)))

    print(f"Marca de agua agregada y guardada en {output_path}")

def extract_watermark(image_with_watermark_path, watermark_path, alpha=0.1):
    image_wm = cv2.imread(image_with_watermark_path, cv2.IMREAD_GRAYSCALE)
    watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)

    coeffs_image_wm = pywt.dwt2(image_wm, 'haar')
    LL_wm, (LH_wm, HL_wm, HH_wm) = coeffs_image_wm

    watermark_resized = cv2.resize(watermark, (LL_wm.shape[1], LL_wm.shape[0]))

    LL_original = LL_wm - alpha * watermark_resized

    coeffs_no_wm = LL_original, (LH_wm, HL_wm, HH_wm)
    image_no_wm = pywt.idwt2(coeffs_no_wm, 'haar')

    image_no_wm_resized = cv2.resize(image_no_wm, (image_wm.shape[1], image_wm.shape[0]))

    output_path_no_watermark = os.path.join(os.getcwd(), 'WatermarklessImage.jpg')
    cv2.imwrite(output_path_no_watermark, np.uint8(np.clip(image_no_wm_resized, 0, 255)))

    print(f"Imagen sin marca de agua guardada en {output_path_no_watermark}")

def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image_path_var.set(file_path)
        load_image(image_label, file_path)

def select_watermark():
    file_path = filedialog.askopenfilename()
    if file_path:
        watermark_path_var.set(file_path)
        load_image(watermark_label, file_path)

def load_image(label, file_path):
    image = Image.open(file_path)
    image.thumbnail((200, 200))
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)
    label.image = photo

def process_image(add=True):
    image_path = image_path_var.get()
    watermark_path = watermark_path_var.get()
    alpha = alpha_var.get()

    if not image_path or not watermark_path:
        messagebox.showwarning("Advertencia", "Por favor, selecciona todas las rutas de archivo necesarias.")
        return

    try:
        if add:
            add_watermark(image_path, watermark_path, alpha)
            messagebox.showinfo("Éxito", "Marca de agua agregada y guardada en 'MarcaDeAguaAdd.jpg'")
        else:
            extract_watermark(image_path, watermark_path, alpha)
            messagebox.showinfo("Éxito", "Imagen sin marca de agua guardada en 'ImagenSinMarcaDeAgua.jpg'")
    except ValueError as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Marca de Agua Digital")

image_path_var = tk.StringVar()
watermark_path_var = tk.StringVar()
alpha_var = tk.DoubleVar(value=0.1)

tk.Label(root, text="Imagen:").grid(row=0, column=0, sticky="e")
tk.Button(root, text="Seleccionar", command=select_image).grid(row=0, column=1)
image_label = tk.Label(root)
image_label.grid(row=1, column=0, columnspan=2)

tk.Label(root, text="Marca de Agua:").grid(row=2, column=0, sticky="e")
tk.Button(root, text="Seleccionar", command=select_watermark).grid(row=2, column=1)
watermark_label = tk.Label(root)
watermark_label.grid(row=3, column=0, columnspan=2)

tk.Label(root, text="Intensidad de la Marca de Agua (α):").grid(row=4, column=0, sticky="e")
tk.Scale(root, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=alpha_var).grid(row=4, column=1, columnspan=2, sticky="we")

tk.Button(root, text="Agregar Marca de Agua", command=lambda: process_image(add=True)).grid(row=5, column=0, columnspan=3, pady=5)
tk.Button(root, text="Extraer Marca de Agua", command=lambda: process_image(add=False)).grid(row=6, column=0, columnspan=3, pady=5)

root.mainloop()
