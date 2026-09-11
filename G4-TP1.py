import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk

# Matrices de conversión NTSC RGB <-> YIQ
M_rgb_to_yiq = np.array([
    [0.299, 0.587, 0.114],
    [0.5957, -0.2744, -0.3212],
    [0.2115, -0.5227, 0.3112]
])

M_yiq_to_rgb = np.array([
    [1.0, 0.9563, 0.6210],
    [1.0, -0.2721, -0.6474],
    [1.0, -1.1070, 1.7046]
])

class YIQImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manipulación en Tiempo Real de Luminancia y Saturación (YIQ)")
        self.root.geometry("900x600")

        self.image_path = None
        self.original_image = None
        self.processed_photo = None # Mantener referencia para evitar recolector de basura

        # --- PANEL IZQUIERDO: Controles ---
        control_frame = tk.Frame(root, width=300, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.btn_load = tk.Button(control_frame, text="Cargar Imagen", command=self.load_image, bg="#007ACC", fg="white", font=("Arial", 10, "bold"))
        self.btn_load.pack(fill=tk.X, pady=10)

        tk.Label(control_frame, text="Coeficiente de Luminancia (a):", font=("Arial", 9)).pack(anchor="w", pady=(10, 0))
        self.scale_a = tk.Scale(control_frame, from_=0.0, to=2.0, resolution=0.05, orient=tk.HORIZONTAL, command=self.on_slider_change)
        self.scale_a.set(1.0)
        self.scale_a.pack(fill=tk.X, pady=5)

        tk.Label(control_frame, text="Coeficiente de Saturación (b):", font=("Arial", 9)).pack(anchor="w", pady=(10, 0))
        self.scale_b = tk.Scale(control_frame, from_=0.0, to=2.0, resolution=0.05, orient=tk.HORIZONTAL, command=self.on_slider_change)
        self.scale_b.set(1.0)
        self.scale_b.pack(fill=tk.X, pady=5)

        self.btn_reset = tk.Button(control_frame, text="Restablecer Valores", command=self.reset_sliders, bg="#d9534f", fg="white")
        self.btn_reset.pack(fill=tk.X, pady=20)

        # --- PANEL DERECHO: Visualización de Imágenes ---
        display_frame = tk.Frame(root, padx=10, pady=10)
        display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Sub-panel Original
        orig_frame = tk.LabelFrame(display_frame, text="Imagen Original", font=("Arial", 10, "bold"))
        orig_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_original = tk.Label(orig_frame, text="Sin imagen cargada")
        self.lbl_original.pack(expand=True, fill=tk.BOTH)

        # Sub-panel Procesada
        proc_frame = tk.LabelFrame(display_frame, text="Imagen Modificada", font=("Arial", 10, "bold"))
        proc_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_processed = tk.Label(proc_frame, text="Sin imagen procesada")
        self.lbl_processed.pack(expand=True, fill=tk.BOTH)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos de Imagen", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            try:
                self.image_path = path
                self.original_image = Image.open(self.image_path).convert("RGB")
                
                # Mostrar la imagen original adaptada al tamaño del panel
                self.display_image(self.original_image, is_original=True)
                
                # Procesar inmediatamente con los valores actuales (1.0, 1.0)
                self.process_image()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

    def display_image(self, img, is_original=True):
        # Redimensionar la imagen manteniendo proporción para que quepa en el panel (max 350x450)
        img_copy = img.copy()
        img_copy.thumbnail((350, 450))
        photo = ImageTk.PhotoImage(img_copy)

        if is_original:
            self.lbl_original.config(image=photo, text="")
            self.lbl_original.image = photo  # Guardar referencia
        else:
            self.lbl_processed.config(image=photo, text="")
            self.lbl_processed.image = photo # Guardar referencia

    def on_slider_change(self, event=None):
        # Cada vez que se mueve un slider, se ejecuta el procesamiento en tiempo real si hay imagen
        if self.original_image is not None:
            self.process_image()

    def reset_sliders(self):
        self.scale_a.set(1.0)
        self.scale_b.set(1.0)

    def process_image(self):
        if self.original_image is None:
            return

        a = self.scale_a.get()
        b = self.scale_b.get()

        # Convertir a numpy array con tipo float32
        img_np = np.array(self.original_image, dtype=np.float32)

        # Paso 1: Normalizar los valores de RGB del píxel ([0, 1])
        rgb_norm = img_np / 255.0

        # Paso 2: RGB -> YIQ (multiplicación matricial)
        yiq = np.dot(rgb_norm, M_rgb_to_yiq.T)

        Y = yiq[:, :, 0]
        I = yiq[:, :, 1]
        Q = yiq[:, :, 2]

        # Paso 3 y 4: Alterar Y, I y Q
        Y_prime = a * Y
        I_prime = b * I
        Q_prime = b * Q

        # Paso 5: Chequear que Y' <= 1 (y >= 0 para evitar negativos)
        Y_prime = np.clip(Y_prime, 0.0, 1.0)

        # Paso 6: Chequear rangos de I' y Q'
        I_prime = np.clip(I_prime, -0.5957, 0.5957)
        Q_prime = np.clip(Q_prime, -0.5226, 0.5226)

        # Reconstruir matriz Y'I'Q'
        yiq_prime = np.stack([Y_prime, I_prime, Q_prime], axis=-1)

        # Paso 7: Y'I'Q' -> R'G'B' (normalizado)
        rgb_prime = np.dot(yiq_prime, M_yiq_to_rgb.T)
        rgb_prime = np.clip(rgb_prime, 0.0, 1.0)

        # Paso 8: Convertir R'G'B' a bytes (uint8) y mostrar
        img_out_np = (rgb_prime * 255).astype(np.uint8)
        img_out = Image.fromarray(img_out_np)

        # Mostrar en el panel derecho de la interfaz
        self.display_image(img_out, is_original=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = YIQImageProcessorApp(root)
    root.mainloop()