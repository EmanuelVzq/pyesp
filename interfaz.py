import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog, messagebox
from datetime import datetime
import os
import re
from keywords import PALABRAS_RESERVADAS
from analizador_lexico import analizar_codigo, tabla_simbolos

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

        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                                         sashrelief=tk.RAISED, sashwidth=8,
                                         bg=self.bg_light)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        code_panel = tk.Frame(main_container, bg=self.bg_dark)
        main_container.add(code_panel)

        code_frame = tk.Frame(code_panel, bg=self.bg_dark)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        ejemplo_codigo = """
# Ejemplo 
funcion imprimir_lista(lista):
    para elemento en lista:
        imprimir(elemento)

variable numeros = [1, 2, 3, 4]
imprimir_lista(numeros)
"""

        self.code_editor.insert(1.0, ejemplo_codigo)
        self.update_line_numbers()
        self.code_editor.bind("<KeyRelease>", self.on_code_change)
        self.code_editor.bind("<MouseWheel>", self.on_mouse_wheel)
        self.code_editor.bind("<Button-4>", self.on_mouse_wheel)
        self.code_editor.bind("<Button-5>", self.on_mouse_wheel)
        self.code_editor.bind("<Configure>", self.sincronizar_scroll)

        result_panel = tk.Frame(main_container, bg=self.bg_light, width=520)
        result_panel.pack_propagate(False)
        main_container.add(result_panel, minsize=320)

        notebook = ttk.Notebook(result_panel)
        notebook.pack(fill=tk.BOTH, expand=True)

        token_tab = tk.Frame(notebook, bg=self.bg_light)
        symbol_tab = tk.Frame(notebook, bg=self.bg_light)
        notebook.add(token_tab, text="Tabla de Tokens")
        notebook.add(symbol_tab, text="Tabla de Símbolos")

        style = ttk.Style()
        style.configure("Custom.Treeview", background="#ffffff", fieldbackground="#ffffff",
                        foreground="#333333", font=("Consolas", 10))
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#f0f0f0",
                        foreground="#333333")
        style.map("Custom.Treeview", background=[("selected", "#cce5ff")], foreground=[("selected", "#000000")])

        token_frame = tk.Frame(token_tab, bg=self.bg_light)
        token_frame.pack(fill=tk.BOTH, expand=True)

        self.tokens_table = ttk.Treeview(token_frame, columns=("token", "lexema", "tipo", "linea", "columna", "id"),
                                        show="headings", style="Custom.Treeview")
        self.tokens_table.heading("token", text="Token")
        self.tokens_table.heading("lexema", text="Lexema")
        self.tokens_table.heading("tipo", text="Tipo")
        self.tokens_table.heading("linea", text="L")
        self.tokens_table.heading("columna", text="C")
        self.tokens_table.heading("id", text="ID")
        self.tokens_table.column("token", width=120, anchor="w")
        self.tokens_table.column("lexema", width=220, anchor="w")
        self.tokens_table.column("tipo", width=140, anchor="w")
        self.tokens_table.column("linea", width=40, anchor="center")
        self.tokens_table.column("columna", width=40, anchor="center")
        self.tokens_table.column("id", width=40, anchor="center")
        self.tokens_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        token_scroll_y = ttk.Scrollbar(token_frame, orient=tk.VERTICAL, command=self.tokens_table.yview)
        token_scroll_x = ttk.Scrollbar(token_frame, orient=tk.HORIZONTAL, command=self.tokens_table.xview)
        self.tokens_table.configure(yscrollcommand=token_scroll_y.set, xscrollcommand=token_scroll_x.set)
        token_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        token_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        symbol_frame = tk.Frame(symbol_tab, bg=self.bg_light)
        symbol_frame.pack(fill=tk.BOTH, expand=True)

        self.symbols_table = ttk.Treeview(symbol_frame, columns=("token", "lexema", "categoria", "id"),
                                          show="headings", style="Custom.Treeview")
        self.symbols_table.heading("token", text="Token")
        self.symbols_table.heading("lexema", text="Lexema")
        self.symbols_table.heading("categoria", text="Categoria")
        self.symbols_table.heading("id", text="ID")
        self.symbols_table.column("token", width=120, anchor="w")
        self.symbols_table.column("lexema", width=240, anchor="w")
        self.symbols_table.column("categoria", width=220, anchor="w")
        self.symbols_table.column("id", width=40, anchor="center")
        self.symbols_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        symbol_scroll_y = ttk.Scrollbar(symbol_frame, orient=tk.VERTICAL, command=self.symbols_table.yview)
        symbol_scroll_x = ttk.Scrollbar(symbol_frame, orient=tk.HORIZONTAL, command=self.symbols_table.xview)
        self.symbols_table.configure(yscrollcommand=symbol_scroll_y.set, xscrollcommand=symbol_scroll_x.set)
        symbol_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        symbol_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

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

    def actualizar_tablas(self, tokens, simbolos):
        for item in self.tokens_table.get_children():
            self.tokens_table.delete(item)
        for t in tokens:
            self.tokens_table.insert("", tk.END, values=(
                t['token'],
                t['lexema'],
                t['tipo'],
                t['linea'],
                t['columna'],
                t['id']
            ))

        for item in self.symbols_table.get_children():
            self.symbols_table.delete(item)
        for s in simbolos:
            self.symbols_table.insert("", tk.END, values=(
                s['token'],
                s['lexema'],
                s['categoria'],
                s['id']
            ))

    def ejecutar_compilacion(self):
        contenido = self.code_editor.get(1.0, tk.END)

        if not contenido.strip():
            self.add_console_log(f"[{self.obtener_hora()}] WARNING No hay código para compilar", "warning")
            return

        self.limpiar_consola()

        resultado = analizar_codigo(contenido)

        tokens = resultado["tokens"]
        errores = resultado["errores"]

        self.actualizar_tablas(tokens, tabla_simbolos)

        self.add_console_log(f"[{self.obtener_hora()}] SUCCESS Análisis léxico completado", "success")

        if errores:
            for idx, error in enumerate(errores, 1):
                linea_texto = f"L{error['linea']}, C{error['posicion']}" if error.get('linea') else f"C{error['posicion']}"
                self.add_console_log(
                    f"[{self.obtener_hora()}] ERROR #{idx}: {error['categoria']} - '{error['caracter']}' en {linea_texto}: {error['descripcion']}",
                    "error"
                )

    def obtener_hora(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    root = tk.Tk()
    app = PyEsp(root)
    root.mainloop()