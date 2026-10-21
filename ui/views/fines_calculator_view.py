import tkinter as tk
from tkinter import ttk
from ui.styles.theme import Theme


class FinesCalculatorView:
    def __init__(self, parent_frame, usuario):
        self.parent = parent_frame
        self.usuario = usuario
        self.construir_ui()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Encabezado
        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)

        tk.Label(header, text="Calculadora de Multas", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")

        # Card principal
        card = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        content = tk.Frame(card, bg=Theme.COLOR_WHITE)
        content.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(content, text="¿Cuánto debe pagar el lector?", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_WHITE).pack(anchor="w", pady=(0, 20))

        # Días de retraso (Slider)
        tk.Label(content, text="Días de retraso", bg=Theme.COLOR_WHITE).pack(anchor="w")
        self.scale_dias = tk.Scale(content, from_=0, to=30, orient="horizontal",
                                   bg=Theme.COLOR_WHITE, highlightthickness=0,
                                   command=lambda x: self.calcular())
        self.scale_dias.set(3)  # Valor por defecto
        self.scale_dias.pack(fill="x", pady=(0, 15))

        # Fila de valores
        row_frame = tk.Frame(content, bg=Theme.COLOR_WHITE)
        row_frame.pack(fill="x", pady=(0, 15))

        # Valor por día
        col1 = tk.Frame(row_frame, bg=Theme.COLOR_WHITE)
        col1.pack(side="left", expand=True, fill="x", padx=(0, 10))
        tk.Label(col1, text="Valor por día (COP)", bg=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_valor = ttk.Entry(col1)
        self.entry_valor.insert(0, "1500")
        self.entry_valor.pack(fill="x")
        self.entry_valor.bind("<KeyRelease>", lambda e: self.calcular())

        # Tipo de usuario
        col2 = tk.Frame(row_frame, bg=Theme.COLOR_WHITE)
        col2.pack(side="left", expand=True, fill="x", padx=(10, 0))
        tk.Label(col2, text="Tipo de usuario", bg=Theme.COLOR_WHITE).pack(anchor="w")
        self.combo_tipo = ttk.Combobox(col2, values=["Estudiante (tarifa completa)", "Docente (50% descuento)"],
                                       state="readonly")
        self.combo_tipo.current(0)
        self.combo_tipo.pack(fill="x")
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: self.calcular())

        # Checkbox Reincidente
        self.var_reincidente = tk.BooleanVar()
        chk = ttk.Checkbutton(content, text="Es reincidente (recargo del 20%)",
                              variable=self.var_reincidente, command=self.calcular)
        chk.pack(anchor="w", pady=(0, 20))

        # Total a pagar
        total_frame = tk.Frame(content, bg="#fdfbf7", highlightbackground="#c69814", highlightthickness=2)
        total_frame.pack(fill="x", pady=10)

        tk.Label(total_frame, text="Total a pagar", font=("Segoe UI", 12),
                 bg="#fdfbf7").pack(side="left", padx=20, pady=20)

        self.lbl_total = tk.Label(total_frame, text="$ 0", font=("Segoe UI", 24, "bold"),
                                  bg="#fdfbf7", fg=Theme.COLOR_TEXT_DARK)
        self.lbl_total.pack(side="right", padx=20, pady=20)

        # Calcular inicial
        self.calcular()

    def calcular(self, event=None):
        try:
            dias = self.scale_dias.get()
            valor_dia = float(self.entry_valor.get())
            es_docente = "Docente" in self.combo_tipo.get()
            es_reincidente = self.var_reincidente.get()

            total = dias * valor_dia

            # Descuento docente
            if es_docente:
                total *= 0.5

            # Recargo reincidente
            if es_reincidente:
                total *= 1.20

            # Formatear con separador de miles
            self.lbl_total.config(text=f"$ {total:,.0f}".replace(",", "."))
        except ValueError:
            self.lbl_total.config(text="$ 0")