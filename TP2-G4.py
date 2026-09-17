import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class TP2App:
    def __init__(self, root):
        self.root = root
        self.root.title("TP2: Aritmética de Píxeles")
        self.root.geometry("950x910") # Aumentado ligeramente para dar espacio al botón de descarga

        self.img1_path = None
        self.img2_path = None
        self.img1_np = None
        self.img2_np = None
        self.result_np = None

        # Referencias fijas para evitar que el recolector de basura borre las imágenes
        self.photo1 = None
        self.photo2 = None
        self.photo_res = None

        # ==========================================
        # 1. PANEL SUPERIOR: Imágenes Originales
        # ==========================================
        frame_orig = tk.LabelFrame(root, text=" Imágenes Originales ", padx=10, pady=10)
        frame_orig.pack(fill="x", padx=15, pady=5)

        frame_orig.columnconfigure(0, weight=1)
        frame_orig.columnconfigure(1, weight=1)

        # Columna 1: Imagen 1
        btn_img1 = tk.Button(frame_orig, text="Cargar Imagen 1", command=lambda: self.cargar_imagen(1), bg="#d0f0c0", font=("Arial", 9, "bold"))
        btn_img1.grid(row=0, column=0, pady=5)
        self.lbl_img1 = tk.Label(frame_orig, text="[ Sin Imagen 1 ]", bg="#e6e6e6", width=35, height=10)
        self.lbl_img1.grid(row=1, column=0, padx=5, pady=5)

        # Columna 2: Imagen 2
        btn_img2 = tk.Button(frame_orig, text="Cargar Imagen 2", command=lambda: self.cargar_imagen(2), bg="#ffcccb", font=("Arial", 9, "bold"))
        btn_img2.grid(row=0, column=1, pady=5)
        self.lbl_img2 = tk.Label(frame_orig, text="[ Sin Imagen 2 ]", bg="#e6e6e6", width=35, height=10)
        self.lbl_img2.grid(row=1, column=1, padx=5, pady=5)

        # ==========================================
        # 2. PANEL CENTRAL: Botones de Operaciones
        # ==========================================
        frame_ops = tk.LabelFrame(root, text=" Operaciones de Aritmética de Píxeles ", padx=10, pady=10)
        frame_ops.pack(fill="x", padx=15, pady=5)

        frame_ops.columnconfigure(0, weight=1)
        frame_ops.columnconfigure(1, weight=1)

        tk.Button(frame_ops, text="1. Suma Clampeada (RGB)", command=lambda: self.operar("rgb_suma"), width=35, bg="#f7f7f7").grid(row=0, column=0, padx=5, pady=3)
        tk.Button(frame_ops, text="2. Suma en Espacio YIQ", command=lambda: self.operar("yiq_suma"), width=35, bg="#f7f7f7").grid(row=0, column=1, padx=5, pady=3)
        tk.Button(frame_ops, text="3. Producto (Multiplicación)", command=lambda: self.operar("producto"), width=35, bg="#f7f7f7").grid(row=1, column=0, padx=5, pady=3)
        tk.Button(frame_ops, text="4. Resta con Valor Absoluto", command=lambda: self.operar("resta_abs"), width=35, bg="#f7f7f7").grid(row=1, column=1, padx=5, pady=3)
        tk.Button(frame_ops, text="5. If-Lighter (Máximo)", command=lambda: self.operar("if_lighter"), width=35, bg="#f7f7f7").grid(row=2, column=0, padx=5, pady=3)
        tk.Button(frame_ops, text="6. If-Darker (Mínimo)", command=lambda: self.operar("if_darker"), width=35, bg="#f7f7f7").grid(row=2, column=1, padx=5, pady=3)

        # ==========================================
        # 3. PANEL INFERIOR: Resultado
        # ==========================================
        frame_res = tk.LabelFrame(root, text=" Resultado ", padx=10, pady=10)
        frame_res.pack(fill="both", expand=True, padx=15, pady=5)

        self.lbl_resultado_titulo = tk.Label(frame_res, text="[ Esperando Operación ]", font=("Arial", 10, "bold"))
        self.lbl_resultado_titulo.pack(pady=2)

        self.lbl_resultado = tk.Label(frame_res, text="", bg="#d9d9d9", width=45, height=10)
        self.lbl_resultado.pack(fill="both", expand=True, padx=5, pady=5)

        # Botón para descargar el resultado (inicialmente deshabilitado)
        self.btn_guardar = tk.Button(frame_res, text="💾 Guardar Imagen Resultante", command=self.guardar_imagen, bg="#c8e6c9", font=("Arial", 9, "bold"), state="disabled")
        self.btn_guardar.pack(pady=5)

    def cargar_imagen(self, num):
        path = filedialog.askopenfilename(filetypes=[("Archivos de Imagen", "*.jpg *.jpeg *.png *.bmp")])
        if not path:
            return

        img_pil = Image.open(path).convert("RGB")
        img_np = np.array(img_pil).astype(np.float32) / 255.0

        # Crear miniatura para la vista previa
        img_thumb = img_pil.copy()
        img_thumb.thumbnail((250, 180), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_thumb)

        if num == 1:
            self.img1_path = path
            self.img1_np = img_np
            self.photo1 = photo
            self.lbl_img1.config(image=self.photo1, text="", width=0, height=0)
        else:
            self.img2_path = path
            self.img2_np = img_np
            self.photo2 = photo
            self.lbl_img2.config(image=self.photo2, text="", width=0, height=0)

    def verificar_y_alinear_imagenes(self):
        if self.img1_np is None or self.img2_np is None:
            messagebox.showwarning("Atención", "Debes cargar ambas imágenes antes de realizar una operación.")
            return False

        # Redimensionar la Imagen 2 para que coincida exactamente con la Imagen 1 si difieren en tamaño
        if self.img1_np.shape != self.img2_np.shape:
            h, w, _ = self.img1_np.shape
            img2_pil = Image.fromarray((self.img2_np * 255).astype(np.uint8))
            img2_pil = img2_pil.resize((w, h), Image.Resampling.LANCZOS)
            self.img2_np = np.array(img2_pil).astype(np.float32) / 255.0

        return True

    def mostrar_resultado(self, img_np, titulo=""):
        self.result_np = img_np # Guardar el resultado en la clase para poder exportarlo después
        img_uint8 = np.clip(img_np * 255.0, 0, 255).astype(np.uint8)
        img_pil = Image.fromarray(img_uint8)

        # Escalar el resultado para que encaje cómodamente en la parte inferior
        img_pil_thumb = img_pil.copy()
        img_pil_thumb.thumbnail((380, 220), Image.Resampling.LANCZOS)
        self.photo_res = ImageTk.PhotoImage(img_pil_thumb)

        self.lbl_resultado_titulo.config(text=f"Resultado: {titulo}")
        self.lbl_resultado.config(image=self.photo_res, text="", width=0, height=0)
        
        # Habilitar el botón de descarga una vez generado el resultado
        self.btn_guardar.config(state="normal")

    def guardar_imagen(self):
        if self.result_np is None:
            messagebox.showwarning("Atención", "No hay ninguna imagen de resultado para guardar.")
            return

        # Cuadro de diálogo para guardar archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Archivos PNG", "*.png"), ("Archivos JPEG", "*.jpg"), ("Todos los archivos", "*.*")],
            title="Guardar imagen resultante"
        )

        if file_path:
            try:
                img_uint8 = np.clip(self.result_np * 255.0, 0, 255).astype(np.uint8)
                img_pil = Image.fromarray(img_uint8)
                img_pil.save(file_path)
                messagebox.showinfo("Éxito", f"Imagen guardada correctamente en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen:\n{str(e)}")

    # --- FUNCIONES DE MATRICES YIQ ---
    def rgb2yiq(self, rgb):
        transform = np.array([
            [0.299, 0.587, 0.114],
            [0.5957, -0.2744, -0.3212],
            [0.2115, -0.5227, 0.3112]
        ])
        return np.dot(rgb, transform.T)

    def yiq2rgb(self, yiq):
        transform_inv = np.array([
            [1.0, 0.956, 0.621],
            [1.0, -0.27208, -0.6474],
            [1.0, -1.106, 1.703]
        ])
        return np.dot(yiq, transform_inv.T)

    # --- LÓGICA DE OPERACIONES ---
    def operar(self, tipo):
        if not self.verificar_y_alinear_imagenes():
            return

        i1 = self.img1_np
        i2 = self.img2_np

        if tipo == "rgb_suma":
            res = np.clip(i1 + i2, 0.0, 1.0)
            titulo = "Suma Clampeada (RGB)"

        elif tipo == "yiq_suma":
            yiq1 = self.rgb2yiq(i1)
            yiq2 = self.rgb2yiq(i2)
            yiq_res = yiq1 + yiq2

            # Control de límites en YIQ
            yiq_res[:, :, 0] = np.clip(yiq_res[:, :, 0], 0.0, 1.0)
            yiq_res[:, :, 1] = np.clip(yiq_res[:, :, 1], -0.5957, 0.5957)
            yiq_res[:, :, 2] = np.clip(yiq_res[:, :, 2], -0.5226, 0.5226)

            res = np.clip(self.yiq2rgb(yiq_res), 0.0, 1.0)
            titulo = "Suma en Espacio YIQ"

        elif tipo == "producto":
            res = np.clip(i1 * i2, 0.0, 1.0)
            titulo = "Producto (Multiplicación)"

        elif tipo == "resta_abs":
            res = np.abs(i1 - i2)
            titulo = "Resta con Valor Absoluto"

        elif tipo == "if_lighter":
            res = np.maximum(i1, i2)
            titulo = "If-Lighter (Máximo)"

        elif tipo == "if_darker":
            res = np.minimum(i1, i2)
            titulo = "If-Darker (Mínimo)"

        self.mostrar_resultado(res, titulo)

if __name__ == "__main__":
    root = tk.Tk()
    app = TP2App(root)
    root.mainloop()