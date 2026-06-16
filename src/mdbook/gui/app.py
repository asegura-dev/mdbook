"""GUI mínima de mdbook (Fase 2).

Solo orquesta: recoge entradas del usuario, construye un ``BuildOptions``
validado y delega en ``compile_book``. No parsea Markdown ni genera HTML.
"""

from __future__ import annotations

import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pydantic import ValidationError

from mdbook.config import BuildOptions, discover_markdown
from mdbook.engine import compile_book


def _format_validation_error(exc: ValidationError) -> str:
    lineas = []
    for error in exc.errors():
        loc = ".".join(str(p) for p in error["loc"]) or "(opciones)"
        lineas.append(f"• {loc}: {error['msg']}")
    return "\n".join(lineas)


class MdbookApp:
    """Ventana principal. Mantiene el estado mínimo de la interfaz."""

    def __init__(self) -> None:
        self.files: list[Path] = []
        self.last_output: Path | None = None

        self.root = ctk.CTk()
        self.root.title("mdbook — Markdown a HTML de estudio")
        self.root.geometry("760x600")
        self.root.minsize(640, 520)

        self.title_var = tk.StringVar(value="Mi obra de estudio")
        self.output_var = tk.StringVar(value=str(Path.cwd() / "mdbook.html"))
        self.status_var = tk.StringVar(value="Elige una carpeta o archivos .md para empezar.")

        self._build_ui()

    # --- Construcción de la interfaz --------------------------------------
    def _build_ui(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        # Título de la obra
        top = ctk.CTkFrame(self.root)
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        top.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(top, text="Título de la obra:").grid(row=0, column=0, padx=(8, 8), pady=8)
        ctk.CTkEntry(top, textvariable=self.title_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 8), pady=8
        )

        # Botones de selección de archivos
        picker = ctk.CTkFrame(self.root)
        picker.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkButton(picker, text="Agregar carpeta…", command=self.add_folder).pack(
            side="left", padx=6, pady=8
        )
        ctk.CTkButton(picker, text="Agregar archivos…", command=self.add_files).pack(
            side="left", padx=6, pady=8
        )
        ctk.CTkButton(
            picker, text="Limpiar lista", fg_color="gray40", command=self.clear_files
        ).pack(side="right", padx=6, pady=8)

        ctk.CTkLabel(self.root, text="Documentos (el orden define el orden en el HTML):").grid(
            row=2, column=0, sticky="w", padx=18, pady=(6, 0)
        )

        # Lista de archivos + botones de orden
        body = ctk.CTkFrame(self.root)
        body.grid(row=3, column=0, sticky="nsew", padx=12, pady=6)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            body,
            activestyle="dotbox",
            highlightthickness=0,
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)
        scrollbar = ctk.CTkScrollbar(body, command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        order = ctk.CTkFrame(body, fg_color="transparent")
        order.grid(row=0, column=2, sticky="ns", padx=(4, 8), pady=8)
        ctk.CTkButton(order, text="▲ Subir", width=96, command=self.move_up).pack(
            padx=4, pady=(0, 6)
        )
        ctk.CTkButton(order, text="▼ Bajar", width=96, command=self.move_down).pack(padx=4, pady=6)
        ctk.CTkButton(
            order, text="Quitar", width=96, fg_color="gray40", command=self.remove_selected
        ).pack(padx=4, pady=6)

        # Salida
        out = ctk.CTkFrame(self.root)
        out.grid(row=4, column=0, sticky="ew", padx=12, pady=6)
        out.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(out, text="Salida (.html):").grid(row=0, column=0, padx=(8, 8), pady=8)
        ctk.CTkEntry(out, textvariable=self.output_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 8), pady=8
        )
        ctk.CTkButton(out, text="Elegir…", width=90, command=self.choose_output).grid(
            row=0, column=2, padx=(0, 8), pady=8
        )

        # Acciones
        actions = ctk.CTkFrame(self.root)
        actions.grid(row=5, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkButton(actions, text="Compilar", command=self.compile, height=40, width=160).pack(
            side="left", padx=8, pady=10
        )
        self.open_btn = ctk.CTkButton(
            actions,
            text="Abrir en navegador",
            command=self.open_browser,
            height=40,
            width=180,
            state="disabled",
        )
        self.open_btn.pack(side="left", padx=8, pady=10)

        ctk.CTkLabel(self.root, textvariable=self.status_var, anchor="w").grid(
            row=6, column=0, sticky="ew", padx=18, pady=(0, 12)
        )

    # --- Estado de la lista ----------------------------------------------
    def _refresh_list(self, select: int | None = None) -> None:
        self.listbox.delete(0, tk.END)
        for path in self.files:
            self.listbox.insert(tk.END, path.name)
        if select is not None and 0 <= select < len(self.files):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(select)
            self.listbox.activate(select)
        self.status_var.set(f"{len(self.files)} documento(s) en la lista.")

    def _selected_index(self) -> int | None:
        seleccion = self.listbox.curselection()  # type: ignore[no-untyped-call]
        return int(seleccion[0]) if seleccion else None

    def _add_paths(self, nuevos: list[Path]) -> None:
        agregados = 0
        for path in nuevos:
            resolved = path.resolve()
            if resolved not in self.files:
                self.files.append(resolved)
                agregados += 1
        self._refresh_list(select=len(self.files) - 1 if self.files else None)
        if nuevos and agregados == 0:
            self.status_var.set("Esos archivos ya estaban en la lista.")

    # --- Acciones de selección -------------------------------------------
    def add_folder(self) -> None:
        carpeta = filedialog.askdirectory(title="Elige una carpeta con archivos .md")
        if not carpeta:
            return
        try:
            encontrados = discover_markdown(Path(carpeta))
        except ValueError as exc:
            messagebox.showerror("Carpeta inválida", str(exc))
            return
        if not encontrados:
            messagebox.showwarning("Sin archivos", "La carpeta no contiene archivos .md.")
            return
        self._add_paths(encontrados)

    def add_files(self) -> None:
        rutas = filedialog.askopenfilenames(
            title="Elige archivos .md",
            filetypes=[("Markdown", "*.md"), ("Todos", "*.*")],
        )
        if not rutas:
            return
        self._add_paths([Path(r) for r in rutas])

    def remove_selected(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        del self.files[idx]
        self._refresh_list(select=min(idx, len(self.files) - 1) if self.files else None)

    def move_up(self) -> None:
        idx = self._selected_index()
        if idx is None or idx == 0:
            return
        self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
        self._refresh_list(select=idx - 1)

    def move_down(self) -> None:
        idx = self._selected_index()
        if idx is None or idx >= len(self.files) - 1:
            return
        self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
        self._refresh_list(select=idx + 1)

    def clear_files(self) -> None:
        self.files.clear()
        self._refresh_list()

    def choose_output(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar HTML como…",
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfile="mdbook.html",
        )
        if ruta:
            self.output_var.set(ruta)

    # --- Compilar / abrir -------------------------------------------------
    def compile(self) -> None:
        if not self.files:
            messagebox.showwarning("Sin documentos", "Agrega al menos un archivo .md.")
            return
        try:
            options = BuildOptions(
                title=self.title_var.get(),
                inputs=list(self.files),
                output=Path(self.output_var.get()),
            )
        except ValidationError as exc:
            messagebox.showerror("Opciones inválidas", _format_validation_error(exc))
            return

        try:
            written = compile_book(options)
        except Exception as exc:  # reportamos cualquier fallo al usuario
            messagebox.showerror("Error al compilar", str(exc))
            return

        self.last_output = written
        self.open_btn.configure(state="normal")
        self.status_var.set(f"Compilado: {written}")
        messagebox.showinfo("Listo", f"HTML generado en:\n{written}")

    def open_browser(self) -> None:
        if self.last_output is None:
            return
        webbrowser.open(self.last_output.as_uri())

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    """Entry point de la GUI (script ``mdbook-gui``)."""
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    MdbookApp().run()


if __name__ == "__main__":
    main()
