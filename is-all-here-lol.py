import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import time
import sys  # Añadir esta importación al inicio

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        
        # Create menu bar
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
        
        # Archivo menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Archivo", menu=self.file_menu)
        self.file_menu.add_command(label="Abrir", command=self.select_image)
        self.file_menu.add_command(label="Propiedades", command=self.show_properties)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=lambda: sys.exit())  # Modificar esta línea
        
        # Ver menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ver", menu=self.view_menu)
        
        # Submenu Zoom
        self.zoom_menu = tk.Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label="Zoom", menu=self.zoom_menu)
        self.zoom_menu.add_command(label="25%", command=lambda: self.set_zoom(0.25))
        self.zoom_menu.add_command(label="50%", command=lambda: self.set_zoom(0.5))
        self.zoom_menu.add_command(label="75%", command=lambda: self.set_zoom(0.75))
        self.zoom_menu.add_command(label="100% (Normal)", command=lambda: self.set_zoom(1.0))
        self.zoom_menu.add_command(label="150%", command=lambda: self.set_zoom(1.5))
        self.zoom_menu.add_command(label="200%", command=lambda: self.set_zoom(2.0))
        self.zoom_menu.add_separator()
        self.zoom_menu.add_command(label="Personalizado...", command=self.show_custom_zoom_dialog)
        
        self.view_menu.add_command(label="Reiniciar Zoom", command=self.reset_view)
        
        # Ayuda menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ayuda", menu=self.help_menu)
        self.help_menu.add_command(label="Acerca de", command=self.show_about)
        
        self.original_image = None
        self.displayed_image = None
        self.image_label = None
        self.canvas = None
        self.zoom = 1.0
        self.position = [0, 0]
        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        self.image_id = None
        self.file_path = None
        
        # Configuración inicial de la ventana
        self.root.geometry("800x600")
        self.root.title("Visor de Imágenes")
        try:
            self.root.iconbitmap('icon.ico')  # Añadir icono
        except:
            pass  # Si no encuentra el icono, continúa sin él
        self.root.update()
        
        # Add zoom label at bottom-right
        self.zoom_label = tk.Label(self.root, text="100%", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.zoom_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.root.deiconify()  # Mostrar la ventana
        
    def select_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.load_image(file_path)
        
    def load_image(self, file_path):
        try:
            self.file_path = file_path
            image = Image.open(file_path)
            # Ensure image has valid dimensions
            if image.size[0] > 0 and image.size[1] > 0:
                self.original_image = image
                self.displayed_image = image
                self.show_image()
            else:
                messagebox.showerror("Error", "Imagen inválida: dimensiones incorrectas")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def show_image(self):
        if self.canvas is not None:
            self.canvas.destroy()
            
        # Create canvas and ensure it's properly sized
        self.canvas = tk.Canvas(self.root, bg="black", width=800, height=600, cursor="arrow")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Force update to ensure canvas has size
        self.root.update_idletasks()
        
        # Bind events
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<Configure>", self.on_resize)
        
        self.update_image()

    def update_zoom_label(self):
        zoom_text = f"{int(self.zoom * 100)}%"
        self.zoom_label.config(text=zoom_text)

    def on_mousewheel(self, event):
        if self.displayed_image:
            # Windows
            if event.delta:
                if event.delta > 0:
                    self.zoom *= 1.1
                else:
                    self.zoom *= 0.9
            # Linux
            else:
                if event.num == 4:
                    self.zoom *= 1.1
                elif event.num == 5:
                    self.zoom *= 0.9
            
            self.zoom = max(0.1, min(5.0, self.zoom))
            self.update_zoom_label()  # Update label
            self.update_image()

    def start_drag(self, event):
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y
        self.canvas.configure(cursor="fleur")  # Cambiar a cursor de movimiento

    def on_drag(self, event):
        if self.dragging:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.position[0] += dx
            self.position[1] += dy
            self.start_x = event.x
            self.start_y = event.y
            self.update_image()

    def stop_drag(self, event):
        self.dragging = False
        self.canvas.configure(cursor="arrow")  # Volver a cursor normal
    
    def on_resize(self, event):
        self.update_image()
        
    def update_image(self):
        if self.displayed_image is None:
            return
            
        try:
            canvas_width = max(1, self.canvas.winfo_width())
            canvas_height = max(1, self.canvas.winfo_height())
            
            if canvas_width <= 0 or canvas_height <= 0:
                return
                
            # Calculate initial size
            image_width, image_height = self.displayed_image.size
            aspect_ratio = image_width / image_height
            
            # Calculate base size
            if canvas_width / canvas_height > aspect_ratio:
                base_height = canvas_height
                base_width = int(canvas_height * aspect_ratio)
            else:
                base_width = canvas_width
                base_height = int(canvas_width / aspect_ratio)
            
            # Apply zoom
            new_width = max(1, int(base_width * self.zoom))
            new_height = max(1, int(base_height * self.zoom))
            
            resized_image = self.displayed_image.resize(
                (new_width, new_height), 
                Image.Resampling.LANCZOS
            )
            self.photo = ImageTk.PhotoImage(resized_image)
            
            # Update canvas
            if hasattr(self, 'image_id') and self.image_id:
                self.canvas.delete(self.image_id)
                
            self.image_id = self.canvas.create_image(
                canvas_width//2 + self.position[0],
                canvas_height//2 + self.position[1],
                image=self.photo
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar imagen: {str(e)}")

    def reset_view(self):
        if self.original_image is not None:
            self.displayed_image = self.original_image
            self.zoom = 1.0
            self.position = [0, 0]
            self.update_zoom_label()  # Update label
            self.update_image()
            
    def set_zoom(self, zoom_level):
        if self.displayed_image:
            self.zoom = zoom_level
            self.update_zoom_label()  # Update label
            self.update_image()

    def show_custom_zoom_dialog(self):
        if not self.displayed_image:
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Zoom Personalizado")
        dialog.geometry("200x100")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar la ventana
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()/2 - 100,
            self.root.winfo_rooty() + self.root.winfo_height()/2 - 50
        ))
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(expand=True, fill='both')
        
        tk.Label(frame, text="Zoom (%):").pack()
        
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(int(self.zoom * 100)))
        entry.pack(pady=5)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def apply_zoom():
            try:
                zoom_value = float(entry.get()) / 100
                if 0.1 <= zoom_value <= 5.0:
                    self.set_zoom(zoom_value)
                    dialog.destroy()
                else:
                    messagebox.showwarning("Error", "El zoom debe estar entre 10% y 500%")
            except ValueError:
                messagebox.showwarning("Error", "Por favor ingrese un número válido")
        
        def on_enter(event):
            apply_zoom()
        
        entry.bind('<Return>', on_enter)
        
        buttons = tk.Frame(frame)
        buttons.pack(fill='x', pady=(10,0))
        
        tk.Button(buttons, text="Aceptar", command=apply_zoom).pack(side='right', padx=5)
        tk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side='right')

    def show_about(self):
        messagebox.showinfo(
            "Acerca de",
            "Visor de Imágenes\n\n" +
            "Controles:\n" +
            "- Rueda del ratón: Zoom\n" +
            "- Click y arrastrar: Mover imagen\n" +
            "- Menú Ver -> Reiniciar Zoom: Restablecer vista\n\n" +
            "Desarrollado por Juanmonopi"
        )

    def show_properties(self):
        if not self.original_image or not self.file_path:
            return

        # Get image info
        width, height = self.original_image.size
        format_type = self.original_image.format
        mode = self.original_image.mode
        
        # Get file info
        import os
        file_size = os.path.getsize(self.file_path) / 1024  # Size in KB
        file_name = os.path.basename(self.file_path)
        
        # Create properties dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Propiedades")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()/2 - 150,
            self.root.winfo_rooty() + self.root.winfo_height()/2 - 125
        ))
        
        # Create and pack widgets
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        # Properties list
        props = [
            ("Nombre:", file_name),
            ("Dimensiones:", f"{width}x{height} píxeles"),
            ("Formato:", format_type),
            ("Modo de color:", mode),
            ("Tamaño de archivo:", f"{file_size:.1f} KB"),
            ("Ruta:", self.file_path)
        ]
        
        for label, value in props:
            row = tk.Frame(frame)
            row.pack(fill='x', pady=2)
            tk.Label(row, text=label, width=12, anchor='w').pack(side='left')
            entry = tk.Entry(row, width=30)
            entry.insert(0, value)
            entry.configure(state='readonly')
            entry.pack(side='left', fill='x', expand=True)
        
        # OK button
        tk.Button(frame, text="Aceptar", command=dialog.destroy, width=10).pack(pady=(20,0))

root = tk.Tk()
app = ImageViewer(root)
root.mainloop()