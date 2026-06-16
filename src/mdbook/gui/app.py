"""Minimal mdbook GUI.

It only orchestrates: collect the user's input, build a validated
``BuildOptions`` and hand it to ``compile_book``. It does not parse Markdown or
generate HTML.
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
    lines = []
    for error in exc.errors():
        loc = ".".join(str(p) for p in error["loc"]) or "(options)"
        lines.append(f"• {loc}: {error['msg']}")
    return "\n".join(lines)


class MdbookApp:
    """Main window. Holds the minimal interface state."""

    def __init__(self) -> None:
        self.files: list[Path] = []
        self.last_output: Path | None = None

        self.root = ctk.CTk()
        self.root.title("mdbook — Markdown to HTML study file")
        self.root.geometry("760x600")
        self.root.minsize(640, 520)

        self.title_var = tk.StringVar(value="My study book")
        self.output_var = tk.StringVar(value=str(Path.cwd() / "mdbook.html"))
        self.theme_var = tk.StringVar(value="light")
        self.crossref_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Pick a folder or .md files to start.")

        self._build_ui()

    # --- UI construction --------------------------------------------------
    def _build_ui(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        # Title of the work
        top = ctk.CTkFrame(self.root)
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        top.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(top, text="Title:").grid(row=0, column=0, padx=(8, 8), pady=8)
        ctk.CTkEntry(top, textvariable=self.title_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 8), pady=8
        )

        # File selection buttons
        picker = ctk.CTkFrame(self.root)
        picker.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkButton(picker, text="Add folder…", command=self.add_folder).pack(
            side="left", padx=6, pady=8
        )
        ctk.CTkButton(picker, text="Add files…", command=self.add_files).pack(
            side="left", padx=6, pady=8
        )
        ctk.CTkButton(picker, text="Clear list", fg_color="gray40", command=self.clear_files).pack(
            side="right", padx=6, pady=8
        )

        ctk.CTkLabel(self.root, text="Documents (the order sets the order in the HTML):").grid(
            row=2, column=0, sticky="w", padx=18, pady=(6, 0)
        )

        # File list + ordering buttons
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
        ctk.CTkButton(order, text="▲ Up", width=96, command=self.move_up).pack(padx=4, pady=(0, 6))
        ctk.CTkButton(order, text="▼ Down", width=96, command=self.move_down).pack(padx=4, pady=6)
        ctk.CTkButton(
            order, text="Remove", width=96, fg_color="gray40", command=self.remove_selected
        ).pack(padx=4, pady=6)

        # Output
        out = ctk.CTkFrame(self.root)
        out.grid(row=4, column=0, sticky="ew", padx=12, pady=6)
        out.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(out, text="Output (.html):").grid(row=0, column=0, padx=(8, 8), pady=8)
        ctk.CTkEntry(out, textvariable=self.output_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 8), pady=8
        )
        ctk.CTkButton(out, text="Choose…", width=90, command=self.choose_output).grid(
            row=0, column=2, padx=(0, 8), pady=8
        )

        # Build options (theme and cross-references)
        options_frame = ctk.CTkFrame(self.root)
        options_frame.grid(row=5, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkLabel(options_frame, text="Default theme:").pack(side="left", padx=(8, 6), pady=8)
        ctk.CTkOptionMenu(
            options_frame, values=["light", "dark"], variable=self.theme_var, width=120
        ).pack(side="left", padx=(0, 16), pady=8)
        ctk.CTkCheckBox(
            options_frame,
            text="Cross-references (e.g. T1 §6)",
            variable=self.crossref_var,
        ).pack(side="left", padx=6, pady=8)

        # Actions
        actions = ctk.CTkFrame(self.root)
        actions.grid(row=6, column=0, sticky="ew", padx=12, pady=6)
        ctk.CTkButton(actions, text="Compile", command=self.compile, height=40, width=160).pack(
            side="left", padx=8, pady=10
        )
        self.open_btn = ctk.CTkButton(
            actions,
            text="Open in browser",
            command=self.open_browser,
            height=40,
            width=180,
            state="disabled",
        )
        self.open_btn.pack(side="left", padx=8, pady=10)

        ctk.CTkLabel(self.root, textvariable=self.status_var, anchor="w").grid(
            row=7, column=0, sticky="ew", padx=18, pady=(0, 12)
        )

    # --- List state -------------------------------------------------------
    def _refresh_list(self, select: int | None = None) -> None:
        self.listbox.delete(0, tk.END)
        for path in self.files:
            self.listbox.insert(tk.END, path.name)
        if select is not None and 0 <= select < len(self.files):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(select)
            self.listbox.activate(select)
        self.status_var.set(f"{len(self.files)} document(s) in the list.")

    def _selected_index(self) -> int | None:
        selection = self.listbox.curselection()  # type: ignore[no-untyped-call]
        return int(selection[0]) if selection else None

    def _add_paths(self, new_paths: list[Path]) -> None:
        added = 0
        for path in new_paths:
            resolved = path.resolve()
            if resolved not in self.files:
                self.files.append(resolved)
                added += 1
        self._refresh_list(select=len(self.files) - 1 if self.files else None)
        if new_paths and added == 0:
            self.status_var.set("Those files were already in the list.")

    # --- Selection actions ------------------------------------------------
    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Pick a folder with .md files")
        if not folder:
            return
        try:
            found = discover_markdown(Path(folder))
        except ValueError as exc:
            messagebox.showerror("Invalid folder", str(exc))
            return
        if not found:
            messagebox.showwarning("No files", "The folder has no .md files.")
            return
        self._add_paths(found)

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Pick .md files",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if not paths:
            return
        self._add_paths([Path(p) for p in paths])

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
        path = filedialog.asksaveasfilename(
            title="Save HTML as…",
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfile="mdbook.html",
        )
        if path:
            self.output_var.set(path)

    # --- Compile / open ---------------------------------------------------
    def compile(self) -> None:
        if not self.files:
            messagebox.showwarning("No documents", "Add at least one .md file.")
            return
        try:
            options = BuildOptions(
                title=self.title_var.get(),
                inputs=list(self.files),
                output=Path(self.output_var.get()),
                theme=self.theme_var.get(),  # type: ignore[arg-type]  # validated by Pydantic
                cross_references=self.crossref_var.get(),
            )
        except ValidationError as exc:
            messagebox.showerror("Invalid options", _format_validation_error(exc))
            return

        try:
            written = compile_book(options)
        except Exception as exc:  # surface any failure to the user
            messagebox.showerror("Build failed", str(exc))
            return

        self.last_output = written
        self.open_btn.configure(state="normal")
        self.status_var.set(f"Built: {written}")
        messagebox.showinfo("Done", f"HTML written to:\n{written}")

    def open_browser(self) -> None:
        if self.last_output is None:
            return
        webbrowser.open(self.last_output.as_uri())

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    """GUI entry point (the ``mdbook-gui`` script)."""
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    MdbookApp().run()


if __name__ == "__main__":
    main()
