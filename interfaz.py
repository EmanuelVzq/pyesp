import tkinter as tk
from tkinter import ttk, scrolledtext, font
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from datetime import datetime


class PyEsp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyEsp")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f5f5f5")

        # Colores
        self.bg_dark = "#ffffff"
        self.bg_light = "#f5f5f5"
        self.text_color = "#333333"
        self.accent_blue = "#0052cc"
        self.error_red = "#d73a49"

        self.create_layout()

    def create_layout(self):
        # ===== HEADER =====
        header = tk.Frame(self.root, bg=self.bg_dark, height=60)
        header.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # Logo
        logo_font = font.Font(family="Helvetica", size=16, weight="bold")
        logo = tk.Label(header, text="PyEsp", font=logo_font,
                        bg=self.bg_dark, fg=self.text_color)
        logo.pack(side=tk.LEFT, padx=20, pady=15)

        # Tabs
        tab_font = font.Font(family="Helvetica", size=10)
        archivo_tab = tk.Label(header, text="Archivo", font=tab_font,
                               bg=self.bg_dark, fg=self.accent_blue)
        archivo_tab.pack(side=tk.LEFT, padx=20, pady=15)

        separator = tk.Label(header, text="|", font=tab_font,
                             bg=self.bg_dark, fg="#cccccc")
        separator.pack(side=tk.LEFT)

        # Botón Ejecutar
        ejecutar_btn = tk.Button(header, text="▶ Ejecutar", font=tab_font,
                                 bg=self.accent_blue, fg="white",
                                 padx=15, pady=8, relief=tk.FLAT, cursor="hand2")
        ejecutar_btn.pack(side=tk.RIGHT, padx=10, pady=12)

        # Iconos (settings, help)
        settings_btn = tk.Button(header, text="⚙", font=("Helvetica", 14),
                                 bg=self.bg_dark, fg=self.text_color,
                                 relief=tk.FLAT, cursor="hand2")
        settings_btn.pack(side=tk.RIGHT, padx=5, pady=12)

        help_btn = tk.Button(header, text="?", font=("Helvetica", 14),
                             bg=self.bg_dark, fg=self.text_color,
                             relief=tk.FLAT, cursor="hand2")
        help_btn.pack(side=tk.RIGHT, padx=10, pady=12)

        # ===== BREADCRUMB =====
        breadcrumb = tk.Frame(self.root, bg=self.bg_light, height=40)
        breadcrumb.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        breadcrumb.pack_propagate(False)

        breadcrumb_font = font.Font(family="Helvetica", size=9)
        breadcrumb_text = tk.Label(breadcrumb, text="📄 main.js  •  Proyecto / src",
                                   font=breadcrumb_font, bg=self.bg_light,
                                   fg="#666666")
        breadcrumb_text.pack(side=tk.LEFT, padx=20, pady=10)

        # ===== MAIN CONTENT =====
        main_container = tk.Frame(self.root, bg=self.bg_light)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Panel de código (izquierda)
        code_panel = tk.Frame(main_container, bg=self.bg_dark)
        code_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Números de línea + código
        code_frame = tk.Frame(code_panel, bg=self.bg_dark)
        code_frame.pack(fill=tk.BOTH, expand=True)

        # Números de línea
        self.line_numbers = tk.Text(code_frame, width=3, padx=5, pady=5,
                                    bg="#f6f8fa", fg="#666666",
                                    font=("Courier New", 10),
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor de código
        self.code_editor = scrolledtext.ScrolledText(code_frame, width=80, height=25,
                                                     font=("Courier New", 10),
                                                     bg=self.bg_dark,
                                                     fg=self.text_color,
                                                     insertbackground=self.accent_blue,
                                                     relief=tk.FLAT, padx=10, pady=5)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Agregar código de ejemplo
        ejemplo_codigo = """function initializeSystem() {
  // Configuración inicial del compilador
  const config = {
    version: "1.0.4",
    engine: "PyEsp-VS",
    optimizations: true
  };

  try {
    console.log("Iniciando proceso de compilación...");
    return process(config);
  } catch (error) {
    console.error("Error crítico detectado:", error);
  }
}

export default initializeSystem;"""

        self.code_editor.insert(1.0, ejemplo_codigo)
        self.update_line_numbers()
        self.code_editor.bind("<KeyRelease>", self.on_code_change)

        # ===== CONSOLE PANEL =====
        console_panel = tk.Frame(self.root, bg=self.bg_dark, height=250)
        console_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)
        console_panel.pack_propagate(False)

        # Console tabs
        console_header = tk.Frame(console_panel, bg=self.bg_dark)
        console_header.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        console_font = font.Font(family="Helvetica", size=9, weight="bold")
        for tab_name in ["CONSOLA", "PROBLEMAS", "SALIDA"]:
            tab_label = tk.Label(console_header, text=tab_name,
                                 font=console_font, bg=self.bg_dark,
                                 fg=self.accent_blue if tab_name == "CONSOLA" else "#666666")
            tab_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Botones derechos consola
        close_btn = tk.Button(console_header, text="×", font=("Helvetica", 14),
                              bg=self.bg_dark, fg="#666666", relief=tk.FLAT)
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        copy_btn = tk.Button(console_header, text="📋", font=("Helvetica", 12),
                             bg=self.bg_dark, fg="#666666", relief=tk.FLAT)
        copy_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Output console
        self.console_output = scrolledtext.ScrolledText(console_panel, height=12,
                                                        font=("Courier New", 9),
                                                        bg="#1e1e1e", fg="#00d700",
                                                        relief=tk.FLAT, padx=10, pady=5)
        self.console_output.pack(fill=tk.BOTH, expand=True)
        self.console_output.config(state=tk.DISABLED)

        # Agregar logs de ejemplo
        self.add_console_log("[10:42:01] INFO Escuchando cambios en el sistema de archivos...")
        self.add_console_log("[10:42:05] EXEC Compilación en curso para main.js...")
        self.add_console_log("[10:42:06] SUCCESS Proceso finalizado exitosamente en 124ms.")
        self.add_console_error("> Iniciando proceso de compilación...")
        self.add_console_error("⚠ ReferenceError: process is not defined at main.js:12:12")

    def update_line_numbers(self):
        """Actualiza los números de línea"""
        line_count = self.code_editor.get("1.0", tk.END).count("\n")
        line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)

    def on_code_change(self, event=None):
        """Evento cuando cambia el código"""
        self.update_line_numbers()

    def add_console_log(self, message):
        """Agrega un log a la consola"""
        self.console_output.config(state=tk.NORMAL)
        self.console_output.insert(tk.END, message + "\n", "info")
        self.console_output.config(state=tk.DISABLED)
        self.console_output.see(tk.END)

        # Configurar color para logs INFO
        self.console_output.tag_config("info", foreground="#0088ff")

    def add_console_error(self, message):
        """Agrega un error a la consola"""
        self.console_output.config(state=tk.NORMAL)
        self.console_output.insert(tk.END, message + "\n", "error")
        self.console_output.config(state=tk.DISABLED)
        self.console_output.see(tk.END)

        # Configurar color para errores
        self.console_output.tag_config("error", foreground="#ff4444")


if __name__ == "__main__":
    root = tk.Tk()
    app = PyEsp(root)
    root.mainloop()