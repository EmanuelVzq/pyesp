# pyesp_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog, messagebox
from datetime import datetime
import os
import re
from keywords import PALABRAS_RESERVADAS

class PyEsp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyEsp")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f5f5f5")

        self.bg_dark = "#ffffff"
        self.bg_light = "#f5f5f5"
        self.text_color = "#333333"
        self.accent_blue = "#0052cc"
        self.error_red = "#d73a49"
        self.palabra_reservada_color = "#0052cc"

        self.palabras_reservadas = PALABRAS_RESERVADAS

        self.archivo_actual = None
        self.contenido_modificado = False

        self.create_layout()

    def create_layout(self):
        # ===== HEADER =====
        header = tk.Frame(self.root, bg=self.bg_dark, height=60)
        header.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        logo_font = font.Font(family="Segoe UI", size=18, weight="bold")
        logo = tk.Label(header, text="PyEsp", font=logo_font,
                        bg=self.bg_dark, fg=self.text_color)
        logo.pack(side=tk.LEFT, padx=20, pady=15)

        tab_font = font.Font(family="Segoe UI", size=11)

        archivo_btn = tk.Button(header, text="📁 Archivo", font=tab_font,
                                bg=self.bg_dark, fg=self.accent_blue,
                                relief=tk.FLAT, cursor="hand2",
                                command=self.mostrar_menu_archivo)
        archivo_btn.pack(side=tk.LEFT, padx=20, pady=15)

        separator = tk.Label(header, text="|", font=tab_font,
                             bg=self.bg_dark, fg="#cccccc")
        separator.pack(side=tk.LEFT)

        ejecutar_btn = tk.Button(header, text="▶ Ejecutar", font=tab_font,
                                 bg=self.accent_blue, fg="white",
                                 padx=15, pady=8, relief=tk.FLAT, cursor="hand2",
                                 command=self.ejecutar_compilacion)
        ejecutar_btn.pack(side=tk.RIGHT, padx=10, pady=12)

        settings_btn = tk.Button(header, text="⚙", font=("Segoe UI", 14),
                                 bg=self.bg_dark, fg=self.text_color,
                                 relief=tk.FLAT, cursor="hand2")
        settings_btn.pack(side=tk.RIGHT, padx=5, pady=12)

        help_btn = tk.Button(header, text="?", font=("Segoe UI", 14),
                             bg=self.bg_dark, fg=self.text_color,
                             relief=tk.FLAT, cursor="hand2")
        help_btn.pack(side=tk.RIGHT, padx=10, pady=12)

        breadcrumb = tk.Frame(self.root, bg=self.bg_light, height=40)
        breadcrumb.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        breadcrumb.pack_propagate(False)

        breadcrumb_font = font.Font(family="Segoe UI", size=9)
        self.breadcrumb_text = tk.Label(breadcrumb, text="📄 Sin archivo abierto  •  Proyecto / src",
                                        font=breadcrumb_font, bg=self.bg_light,
                                        fg="#666666")
        self.breadcrumb_text.pack(side=tk.LEFT, padx=20, pady=10)

        main_container = tk.Frame(self.root, bg=self.bg_light)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        code_panel = tk.Frame(main_container, bg=self.bg_dark)
        code_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        code_frame = tk.Frame(code_panel, bg=self.bg_dark)
        code_frame.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(code_frame, width=3, padx=8, pady=5,
                                    bg="#f6f8fa", fg="#666666",
                                    font=("Consolas", 11),
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_editor = scrolledtext.ScrolledText(code_frame, width=80, height=25,
                                                     font=("Consolas", 11),
                                                     bg=self.bg_dark,
                                                     fg=self.text_color,
                                                     insertbackground=self.accent_blue,
                                                     relief=tk.FLAT, padx=10, pady=5)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.code_editor.tag_config("palabra_reservada", foreground=self.palabra_reservada_color,
                                    font=("Consolas", 11, "bold"))
        self.code_editor.tag_config("normal", foreground=self.text_color)

        ejemplo_codigo = """funcion inicializarSistema() {
  variable config = {
    version: "1.0.4",
    motor: "PyEsp-VS",
    optimizaciones: verdadero
  }

  intentar {
    retorna proceso(config)
  } excepto (error) {
    lanzar error
  }
}

si condicion {
  mientras verdadero {
    para elemento en lista {
      continuar
    }
  }
}

importar desde modulo como alias
clase MiClase hereda OtraClase {
  funcion metodo() {
    nulo
  }
}"""

        self.code_editor.insert(1.0, ejemplo_codigo)
        self.update_line_numbers()
        self.code_editor.bind("<KeyRelease>", self.on_code_change)
        self.code_editor.bind("<MouseWheel>", self.on_mouse_wheel)
        self.code_editor.bind("<Button-4>", self.on_mouse_wheel)
        self.code_editor.bind("<Button-5>", self.on_mouse_wheel)
        self.code_editor.bind("<Configure>", self.sincronizar_scroll)

        console_panel = tk.Frame(self.root, bg=self.bg_dark, height=250)
        console_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)
        console_panel.pack_propagate(False)

        console_header = tk.Frame(console_panel, bg=self.bg_dark)
        console_header.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        console_font = font.Font(family="Segoe UI", size=9, weight="bold")
        self.console_tabs = {}
        for tab_name in ["CONSOLA", "PROBLEMAS", "SALIDA"]:
            tab_label = tk.Label(console_header, text=tab_name,
                                 font=console_font, bg=self.bg_dark,
                                 fg=self.accent_blue if tab_name == "CONSOLA" else "#666666",
                                 cursor="hand2")
            tab_label.pack(side=tk.LEFT, padx=15, pady=10)
            tab_label.bind("<Button-1>", lambda e, t=tab_name: self.cambiar_tab_consola(t))
            self.console_tabs[tab_name] = tab_label

        close_btn = tk.Button(console_header, text="×", font=("Segoe UI", 14),
                              bg=self.bg_dark, fg="#666666", relief=tk.FLAT,
                              command=self.limpiar_consola)
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        copy_btn = tk.Button(console_header, text="📋", font=("Segoe UI", 12),
                             bg=self.bg_dark, fg="#666666", relief=tk.FLAT,
                             command=self.copiar_consola)
        copy_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.console_output = scrolledtext.ScrolledText(console_panel, height=12,
                                                        font=("Consolas", 10),
                                                        bg="#1e1e1e", fg="#00d700",
                                                        relief=tk.FLAT, padx=10, pady=5)
        self.console_output.pack(fill=tk.BOTH, expand=True)
        self.console_output.config(state=tk.DISABLED)

        self.console_output.tag_config("info", foreground="#0088ff")
        self.console_output.tag_config("exec", foreground="#ffaa00")
        self.console_output.tag_config("success", foreground="#00ff00")
        self.console_output.tag_config("error", foreground="#ff4444")
        self.console_output.tag_config("warning", foreground="#ffff00")

        self.add_console_log(f"[{self.obtener_hora()}] INFO Palabras reservadas cargadas: {len(self.palabras_reservadas)}", "info")
        self.add_console_log(f"[{self.obtener_hora()}] INFO PyEsp listo para usar", "success")

    def mostrar_menu_archivo(self):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Abrir archivo", command=self.abrir_archivo)
        menu.add_command(label="Nuevo archivo", command=self.nuevo_archivo)
        menu.add_separator()
        menu.add_command(label="Guardar", command=self.guardar_archivo)
        menu.add_command(label="Guardar como...", command=self.guardar_como)
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[
                ("Archivos Python", "*.py"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                self.code_editor.config(state=tk.NORMAL)
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(1.0, contenido)

                self.aplicar_syntax_highlighting()
                self.update_line_numbers()

                nombre_archivo = os.path.basename(archivo)
                self.archivo_actual = archivo
                self.breadcrumb_text.config(text=f"📄 {nombre_archivo}  •  Proyecto / src")
                self.root.title(f"PyEsp - {nombre_archivo}")
                self.contenido_modificado = False

                self.add_console_log(f"[{self.obtener_hora()}] SUCCESS Archivo '{nombre_archivo}' abierto", "success")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def nuevo_archivo(self):
        self.code_editor.config(state=tk.NORMAL)
        self.code_editor.delete(1.0, tk.END)
        self.update_line_numbers()
        self.archivo_actual = None
        self.breadcrumb_text.config(text="📄 Sin archivo abierto  •  Proyecto / src")
        self.root.title("PyEsp - Sin guardar")
        self.add_console_log(f"[{self.obtener_hora()}] INFO Nuevo archivo creado", "info")

    def guardar_archivo(self):
        if self.archivo_actual:
            try:
                contenido = self.code_editor.get(1.0, tk.END)
                with open(self.archivo_actual, 'w', encoding='utf-8') as f:
                    f.write(contenido)

                self.contenido_modificado = False
                nombre_archivo = os.path.basename(self.archivo_actual)
                self.add_console_log(f"[{self.obtener_hora()}] SUCCESS Archivo '{nombre_archivo}' guardado", "success")
                messagebox.showinfo("Éxito", "Archivo guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
        else:
            self.guardar_como()

    def guardar_como(self):
        archivo = filedialog.asksaveasfilename(
            title="Guardar archivo como",
            defaultextension=".py",
            filetypes=[
                ("Archivos Python", "*.py"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            try:
                contenido = self.code_editor.get(1.0, tk.END)
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)

                self.archivo_actual = archivo
                nombre_archivo = os.path.basename(archivo)
                self.breadcrumb_text.config(text=f"📄 {nombre_archivo}  •  Proyecto / src")
                self.root.title(f"PyEsp - {nombre_archivo}")
                self.contenido_modificado = False
                self.add_console_log(f"[{self.obtener_hora()}] SUCCESS Archivo guardado como '{nombre_archivo}'", "success")
                messagebox.showinfo("Éxito", "Archivo guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def update_line_numbers(self):
        line_count = self.code_editor.get("1.0", tk.END).count("\n")
        line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)

    def on_code_change(self, event=None):
        self.update_line_numbers()
        self.aplicar_syntax_highlighting()
        self.contenido_modificado = True

    def aplicar_syntax_highlighting(self):
        self.code_editor.tag_remove("palabra_reservada", "1.0", tk.END)

        contenido = self.code_editor.get("1.0", tk.END)
        patron = r'\b(' + '|'.join(re.escape(palabra) for palabra in self.palabras_reservadas) + r')\b'

        for match in re.finditer(patron, contenido):
            inicio = match.start()
            fin = match.end()

            indice_inicio = self.code_editor.index(f"1.0+{inicio}c")
            indice_fin = self.code_editor.index(f"1.0+{fin}c")

            self.code_editor.tag_add("palabra_reservada", indice_inicio, indice_fin)

    def sincronizar_scroll(self, event=None):
        primera_linea = self.code_editor.index("@0,0")
        self.line_numbers.see(primera_linea)

    def on_mouse_wheel(self, event):
        self.sincronizar_scroll()

    def add_console_log(self, message, tipo="info"):
        self.console_output.config(state=tk.NORMAL)
        self.console_output.insert(tk.END, message + "\n", tipo)
        self.console_output.config(state=tk.DISABLED)
        self.console_output.see(tk.END)

    def cambiar_tab_consola(self, tab_name):
        for tab, label in self.console_tabs.items():
            if tab == tab_name:
                label.config(fg=self.accent_blue)
            else:
                label.config(fg="#666666")

    def limpiar_consola(self):
        self.console_output.config(state=tk.NORMAL)
        self.console_output.delete(1.0, tk.END)
        self.console_output.config(state=tk.DISABLED)

    def copiar_consola(self):
        contenido = self.console_output.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(contenido)
        messagebox.showinfo("Éxito", "Contenido copiado al portapapeles")

    def ejecutar_compilacion(self):
        contenido = self.code_editor.get(1.0, tk.END)
        if not contenido.strip():
            self.add_console_log(f"[{self.obtener_hora()}] WARNING No hay código para compilar", "warning")
            return

        self.add_console_log(f"[{self.obtener_hora()}] EXEC Iniciando compilación...", "exec")
        self.add_console_log(f"[{self.obtener_hora()}] INFO Analizando sintaxis...", "info")
        self.add_console_log(f"[{self.obtener_hora()}] SUCCESS Compilación finalizada en 150ms.", "success")

    def obtener_hora(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    root = tk.Tk()
    app = PyEsp(root)
    root.mainloop()