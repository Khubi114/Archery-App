"""
Archery Score Recording App
Run: python archery_score_app.py
Requires: Python 3.8+ with tkinter (standard library)
"""

import tkinter as tk
from tkinter import ttk, font
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────── DATA ───────────────────────────

SCORE_ORDER = ["X", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "M"]
EQUIPMENT_LIST = ["Recurve", "Compound", "Barebow", "Longbow"]

DEFAULT_ARCHERS = [
    {"id": 1, "name": "Irene Moser",  "equipment": "Recurve"},
    {"id": 2, "name": "John Smith",   "equipment": "Compound"},
    {"id": 3, "name": "Sarah Lee",    "equipment": "Barebow"},
    {"id": 4, "name": "Tom Nguyen",   "equipment": "Recurve"},
]

ROUNDS = [
    {
        "id": "melbourne", "name": "Melbourne, 90 arrows",
        "arrows_per_end": 6,
        "distances": [
            {"range": "50m", "face": "122cm", "ends": 5},
            {"range": "40m", "face": "122cm", "ends": 5},
            {"range": "30m", "face": "80cm",  "ends": 5},
        ],
    },
    {
        "id": "wa720_70", "name": "WA 720 (70m)",
        "arrows_per_end": 6,
        "distances": [{"range": "70m", "face": "122cm", "ends": 12}],
    },
    {
        "id": "wa720_50", "name": "WA 720 (50m)",
        "arrows_per_end": 6,
        "distances": [{"range": "50m", "face": "122cm", "ends": 12}],
    },
    {
        "id": "wa18", "name": "WA Indoor 18m",
        "arrows_per_end": 3,
        "distances": [{"range": "18m", "face": "40cm", "ends": 20}],
    },
    {
        "id": "york", "name": "York Round",
        "arrows_per_end": 6,
        "distances": [
            {"range": "100yd", "face": "122cm", "ends": 12},
            {"range": "80yd",  "face": "122cm", "ends": 8},
            {"range": "60yd",  "face": "80cm",  "ends": 4},
        ],
    },
]

# ─────────────────────────── HELPERS ───────────────────────────

def score_to_num(s):
    if s == "X":  return 10
    if s == "M":  return 0
    return int(s)

def score_index(s):
    return SCORE_ORDER.index(s)

def end_total(arrows):
    return sum(score_to_num(a) for a in arrows)

def running_total(end_scores, up_to):
    return sum(end_total(e) for e in end_scores[:up_to + 1] if e)

def get_total_ends(rnd):
    return sum(d["ends"] for d in rnd["distances"])

def get_end_info(rnd, end_idx):
    count = 0
    for d in rnd["distances"]:
        if end_idx < count + d["ends"]:
            return d["range"], d["face"]
        count += d["ends"]
    return "?", "?"

def arrow_colors(score):
    """Returns (bg, fg) for a score chip."""
    if score in ("X", "10"): return "#f0c040", "#111111"
    if score in ("9", "8"):  return "#d63030", "#ffffff"
    if score in ("7", "6"):  return "#2060cc", "#ffffff"
    if score in ("5", "4"):  return "#222222", "#ffffff"
    if score in ("3", "2", "1"): return "#cccccc", "#111111"
    if score == "M":         return "#440000", "#ff8888"
    return "#444444", "#ffffff"

# ─────────────────────────── COLORS / THEME ───────────────────────────

C = {
    "bg":         "#0b1a10",
    "panel":      "#132219",
    "panel_lt":   "#1c3024",
    "border":     "#1f3a27",
    "accent":     "#5cb87a",
    "accent_dim": "#2e6644",
    "gold":       "#f0c040",
    "text":       "#ddeee2",
    "muted":      "#6b9a75",
    "danger":     "#e05050",
    "danger_bg":  "#2a0a0a",
}

# ─────────────────────────── BASE FRAME ───────────────────────────

class BaseScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()

    def card(self, parent, pady=(0, 0), padx=0):
        outer = tk.Frame(parent, bg=C["border"], bd=0)
        outer.pack(fill="x", pady=pady, padx=padx)
        inner = tk.Frame(outer, bg=C["panel"], padx=16, pady=14)
        inner.pack(fill="x", padx=1, pady=1)
        return inner

    def label(self, parent, text, size=13, color=None, bold=False, **kw):
        f = (("Courier", size, "bold") if bold else ("Courier", size))
        return tk.Label(parent, text=text, bg=parent["bg"],
                        fg=color or C["text"], font=f, **kw)

    def section_title(self, parent, text):
        lbl = tk.Label(parent, text=text.upper(), bg=C["panel"],
                       fg=C["muted"], font=("Courier", 9, "bold"),
                       anchor="w")
        lbl.pack(fill="x", pady=(0, 6))
        return lbl

    def styled_button(self, parent, text, command, style="primary",
                      width=None, height=1):
        styles = {
            "primary": (C["accent"],     "#0b1a10"),
            "gold":    (C["gold"],       "#0b1a10"),
            "ghost":   (C["panel_lt"],   C["text"]),
            "danger":  (C["danger_bg"],  C["danger"]),
        }
        bg, fg = styles.get(style, styles["primary"])
        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            font=("Courier", 12, "bold"), relief="flat", cursor="hand2",
            height=height, bd=0,
            **({"width": width} if width else {}),
        )

        def on_enter(e):  btn.config(bg=self._brighten(bg))
        def on_leave(e):  btn.config(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _brighten(self, hex_color):
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            r = min(255, r + 20)
            g = min(255, g + 20)
            b = min(255, b + 20)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def styled_dropdown(self, parent, variable, choices, width=30):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                        fieldbackground=C["panel_lt"],
                        background=C["panel_lt"],
                        foreground=C["text"],
                        arrowcolor=C["muted"],
                        selectbackground=C["panel_lt"],
                        selectforeground=C["text"],
                        bordercolor=C["border"],
                        lightcolor=C["border"],
                        darkcolor=C["border"])
        cb = ttk.Combobox(parent, textvariable=variable, values=choices,
                          style="Dark.TCombobox", state="readonly", width=width,
                          font=("Courier", 12))
        return cb

# ─────────────────────────── SCREEN: SETUP ───────────────────────────

class SetupScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._build()

    def _build(self):
        # Scrollable container
        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        frame = tk.Frame(canvas, bg=C["bg"])
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        self._frame = frame

        wrap = tk.Frame(frame, bg=C["bg"])
        wrap.pack(fill="x", padx=24, pady=20)

        # ── Hero ──
        hero = tk.Frame(wrap, bg=C["bg"])
        hero.pack(fill="x", pady=(0, 16))
        tk.Label(hero, text="🎯", bg=C["bg"], font=("", 36)).pack()
        tk.Label(hero, text="Score Recording", bg=C["bg"], fg=C["text"],
                 font=("Courier", 20, "bold")).pack(pady=(4, 2))
        tk.Label(hero, text="Set up a new scoring session", bg=C["bg"],
                 fg=C["muted"], font=("Courier", 11)).pack()

        # ── Round card ──
        rc = self.card(wrap, pady=(0, 12))
        self.section_title(rc, "Choose Round")
        self._round_var = tk.StringVar(value=ROUNDS[0]["name"])
        round_names = [r["name"] for r in ROUNDS]
        cb = self.styled_dropdown(rc, self._round_var, round_names, width=34)
        cb.pack(fill="x", pady=(0, 8))
        self._round_info_var = tk.StringVar()
        self._round_info_lbl = tk.Label(rc, textvariable=self._round_info_var,
                                        bg=C["panel"], fg=C["muted"],
                                        font=("Courier", 10), wraplength=340,
                                        justify="left")
        self._round_info_lbl.pack(fill="x")
        self._round_var.trace_add("write", lambda *_: self._update_round_info())
        self._update_round_info()

        # ── Archer card ──
        ac = self.card(wrap, pady=(0, 12))
        self.section_title(ac, "Choose Archer")
        self._archer_var = tk.StringVar(value="— Select archer —")
        archer_names = ["— Select archer —"] + [a["name"] for a in DEFAULT_ARCHERS]
        acb = self.styled_dropdown(ac, self._archer_var, archer_names, width=34)
        acb.pack(fill="x", pady=(0, 8))

        # Equipment row (shown after archer selected)
        self._eq_frame = tk.Frame(ac, bg=C["panel_lt"], padx=10, pady=8)
        self._eq_frame.pack(fill="x")
        self._eq_lbl = tk.Label(self._eq_frame, text="", bg=C["panel_lt"],
                                fg=C["text"], font=("Courier", 12, "bold"),
                                anchor="w")
        self._eq_lbl.pack(side="left", expand=True, fill="x")
        self._eq_var = tk.StringVar()
        eq_cb = self.styled_dropdown(self._eq_frame, self._eq_var,
                                     EQUIPMENT_LIST, width=14)
        eq_cb.pack(side="right")
        self._eq_frame.pack_forget()  # hidden until archer chosen

        self._archer_var.trace_add("write", lambda *_: self._on_archer_change())

        # ── Done button ──
        self._done_btn = self.styled_button(wrap, "Done", self._on_done,
                                            style="primary")
        self._done_btn.pack(fill="x", pady=(4, 0), ipady=10)
        self._update_done_btn()

    def _update_round_info(self):
        name = self._round_var.get()
        rnd = next((r for r in ROUNDS if r["name"] == name), None)
        if not rnd:
            return
        total = get_total_ends(rnd)
        parts = [f"{d['ends']}× {d['range']} ({d['face']})"
                 for d in rnd["distances"]]
        info = f"{total} ends · {rnd['arrows_per_end']} arrows/end   |   " + "   ".join(parts)
        self._round_info_var.set(info)

    def _on_archer_change(self):
        name = self._archer_var.get()
        archer = next((a for a in DEFAULT_ARCHERS if a["name"] == name), None)
        if archer:
            self._eq_lbl.config(text=archer["name"])
            self._eq_var.set(archer["equipment"])
            self._eq_frame.pack(fill="x")
        else:
            self._eq_frame.pack_forget()
        self._update_done_btn()

    def _update_done_btn(self):
        name = self._archer_var.get()
        valid = name != "— Select archer —"
        bg = C["accent"] if valid else C["accent_dim"]
        fg = "#0b1a10" if valid else "#2a5a35"
        self._done_btn.config(bg=bg, fg=fg,
                              state="normal" if valid else "disabled")

    def _on_done(self):
        round_name = self._round_var.get()
        archer_name = self._archer_var.get()
        rnd = next(r for r in ROUNDS if r["name"] == round_name)
        archer = next(a for a in DEFAULT_ARCHERS if a["name"] == archer_name)
        equipment = self._eq_var.get() or archer["equipment"]
        self.app.start_session(rnd, {**archer, "equipment": equipment})

# ─────────────────────────── SCREEN: ENDS LIST ───────────────────────────

class EndsListScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._widgets = []

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        session = self.app.session
        rnd = session["round"]
        archer = session["archer"]
        end_scores = session["end_scores"]
        total_ends = get_total_ends(rnd)
        completed = sum(1 for e in end_scores if e is not None)
        grand_total = sum(end_total(e) for e in end_scores if e)
        all_done = completed == total_ends

        # ── Header info card ──
        hc = tk.Frame(self, bg=C["panel"], padx=16, pady=12)
        hc.pack(fill="x", padx=12, pady=(12, 6))

        tk.Label(hc, text="🎯  " + archer["name"], bg=C["panel"], fg=C["text"],
                 font=("Courier", 14, "bold"), anchor="w").pack(side="left")
        tk.Label(hc, text=f"{grand_total}", bg=C["panel"], fg=C["gold"],
                 font=("Courier", 22, "bold")).pack(side="right")
        tk.Label(hc, text=f"{archer['equipment']} · {rnd['name']}", bg=C["panel"],
                 fg=C["muted"], font=("Courier", 10)).pack(side="left", padx=(8, 0))

        # Progress bar
        bar_outer = tk.Frame(hc, bg=C["border"], height=4)
        bar_outer.pack(fill="x", side="bottom", pady=(8, 0))
        bar_outer.pack_propagate(False)
        pct = completed / total_ends if total_ends else 0
        bar_inner = tk.Frame(bar_outer,
                             bg=C["gold"] if all_done else C["accent"],
                             height=4)
        bar_inner.place(x=0, y=0, relwidth=pct, height=4)

        # ── Scrollable ends list ──
        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview,
                                 bg=C["panel"], troughcolor=C["bg"])
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=12)

        list_frame = tk.Frame(canvas, bg=C["bg"])
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        list_frame.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        for i in range(total_ends):
            rng, face = get_end_info(rnd, i)
            arrows = end_scores[i]
            is_done = arrows is not None
            self._end_row(list_frame, i, rng, face, arrows, is_done,
                          end_scores, total_ends)

        # ── Finish button ──
        if all_done:
            btn = tk.Button(
                self, text="🏆  View Final Score",
                command=self.app.show_complete,
                bg=C["gold"], fg="#0b1a10",
                font=("Courier", 13, "bold"), relief="flat",
                cursor="hand2", pady=12,
            )
            btn.pack(fill="x", padx=12, pady=8)

    def _end_row(self, parent, i, rng, face, arrows, is_done,
                 end_scores, total_ends):
        row = tk.Frame(parent, bg=C["panel"], pady=10, padx=12)
        row.pack(fill="x", pady=(0, 2))

        # Badge (number / checkmark)
        badge_bg = C["accent_dim"] if is_done else C["panel_lt"]
        badge_fg = C["accent"] if is_done else C["muted"]
        badge_text = "✓" if is_done else str(i + 1)
        badge = tk.Label(row, text=badge_text, bg=badge_bg, fg=badge_fg,
                         font=("Courier", 11, "bold"), width=3, height=1,
                         relief="flat")
        badge.pack(side="left", padx=(0, 10))

        # End info
        info_frame = tk.Frame(row, bg=C["panel"])
        info_frame.pack(side="left", fill="x", expand=True)
        tk.Label(info_frame, text=f"End {i + 1} of {total_ends}",
                 bg=C["panel"], fg=C["text"],
                 font=("Courier", 12, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info_frame, text=f"{rng} · {face}",
                 bg=C["panel"], fg=C["muted"],
                 font=("Courier", 9), anchor="w").pack(anchor="w")

        if is_done:
            # Arrow chips
            chips_frame = tk.Frame(row, bg=C["panel"])
            chips_frame.pack(side="right")
            for sc in arrows:
                bg, fg = arrow_colors(sc)
                tk.Label(chips_frame, text=sc, bg=bg, fg=fg,
                         font=("Courier", 9, "bold"), width=3, height=1,
                         relief="flat").pack(side="left", padx=1)
            total = end_total(arrows)
            rt = running_total(end_scores, i)
            tk.Label(chips_frame, text=f"  {total}", bg=C["panel"], fg=C["gold"],
                     font=("Courier", 14, "bold")).pack(side="left", padx=(6, 0))
            tk.Label(chips_frame, text=f"={rt}", bg=C["panel"], fg=C["muted"],
                     font=("Courier", 9)).pack(side="left")
        else:
            btn = tk.Button(
                row, text="✏ Enter",
                command=lambda idx=i: self.app.show_entry(idx),
                bg=C["accent"], fg="#0b1a10",
                font=("Courier", 10, "bold"), relief="flat", cursor="hand2",
                padx=10, pady=4,
            )
            btn.pack(side="right")

# ─────────────────────────── SCREEN: SCORE ENTRY ───────────────────────────

class ScoreEntryScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._arrow_labels = []
        self._key_buttons = {}
        self._end_idx = None
        self._arrows = []

    def load_end(self, end_idx):
        self._end_idx = end_idx
        self._arrows = []
        for w in self.winfo_children():
            w.destroy()
        self._arrow_labels = []
        self._key_buttons = {}
        self._build()

    def _build(self):
        session = self.app.session
        rnd = session["round"]
        archer = session["archer"]
        end_idx = self._end_idx
        total_ends = get_total_ends(rnd)
        rng, face = get_end_info(rnd, end_idx)
        ape = rnd["arrows_per_end"]

        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=16, pady=12)

        # ── Header card ──
        hc = tk.Frame(outer, bg=C["panel"], padx=14, pady=10)
        hc.pack(fill="x", pady=(0, 10))
        tk.Label(hc, text=f"{archer['name']}  ·  {archer['equipment']}",
                 bg=C["panel"], fg=C["text"],
                 font=("Courier", 13, "bold"), anchor="w").pack(side="left")
        tk.Label(hc,
                 text=f"End {end_idx + 1}/{total_ends}  {rng} · {face}",
                 bg=C["panel"], fg=C["muted"],
                 font=("Courier", 10), anchor="e").pack(side="right")

        # ── Arrow slots ──
        slots_card = tk.Frame(outer, bg=C["panel"], padx=14, pady=12)
        slots_card.pack(fill="x", pady=(0, 10))
        tk.Label(slots_card,
                 text=f"ARROWS  (0 / {ape})",
                 bg=C["panel"], fg=C["muted"],
                 font=("Courier", 9, "bold"), anchor="w").pack(anchor="w", pady=(0, 8))

        slots_row = tk.Frame(slots_card, bg=C["panel"])
        slots_row.pack(anchor="w")
        self._arrow_labels = []
        for _ in range(ape):
            lbl = tk.Label(slots_row, text="–", width=3, height=1,
                           bg=C["panel_lt"], fg=C["border"],
                           font=("Courier", 12, "bold"), relief="flat")
            lbl.pack(side="left", padx=2)
            self._arrow_labels.append(lbl)

        self._count_lbl = tk.Label(slots_card,
                                   text=f"Arrows entered: 0 / {ape}",
                                   bg=C["panel"], fg=C["muted"],
                                   font=("Courier", 9))
        self._count_lbl.pack(anchor="w", pady=(6, 0))

        self._hint_lbl = tk.Label(slots_card,
                                  text="Enter scores highest first: X → 10 → 9 → … → M",
                                  bg=C["panel"], fg=C["muted"],
                                  font=("Courier", 9), wraplength=340, justify="left")
        self._hint_lbl.pack(anchor="w", pady=(2, 0))

        self._total_lbl = tk.Label(slots_card, text="0",
                                   bg=C["panel"], fg=C["text"],
                                   font=("Courier", 26, "bold"))
        self._total_lbl.pack(anchor="e")

        # ── Keypad ──
        kp_card = tk.Frame(outer, bg=C["panel"], padx=14, pady=12)
        kp_card.pack(fill="x", pady=(0, 10))
        kp_grid = tk.Frame(kp_card, bg=C["panel"])
        kp_grid.pack()

        keypad_rows = [["X", "10", "9", "8"], ["7", "6", "5", "4"], ["3", "2", "1", "M"]]
        self._ape = ape
        for r_idx, row in enumerate(keypad_rows):
            for c_idx, score in enumerate(row):
                bg, fg = arrow_colors(score)
                btn = tk.Button(
                    kp_grid, text=score, width=5, height=2,
                    bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                    font=("Courier", 13, "bold"), relief="flat", cursor="hand2",
                    command=lambda s=score: self._key_press(s),
                )
                btn.grid(row=r_idx, column=c_idx, padx=4, pady=4)
                self._key_buttons[score] = btn

        # Backspace
        back_btn = tk.Button(
            kp_card, text="⌫  Remove Last Arrow",
            command=self._backspace,
            bg=C["panel_lt"], fg=C["text"],
            font=("Courier", 11, "bold"), relief="flat", cursor="hand2",
            pady=6,
        )
        back_btn.pack(fill="x", pady=(8, 0))
        self._back_btn = back_btn

        # ── Actions ──
        act = tk.Frame(outer, bg=C["bg"])
        act.pack(fill="x", pady=(0, 0))
        tk.Button(act, text="Cancel",
                  command=self.app.show_ends,
                  bg=C["danger_bg"], fg=C["danger"],
                  font=("Courier", 11, "bold"), relief="flat",
                  cursor="hand2", pady=10).pack(side="left", fill="x",
                                                 expand=True, padx=(0, 6))
        self._save_btn = tk.Button(act, text="Save End",
                                   command=self._save,
                                   bg=C["accent_dim"], fg="#2a5a35",
                                   font=("Courier", 11, "bold"), relief="flat",
                                   cursor="hand2", pady=10, state="disabled")
        self._save_btn.pack(side="right", fill="x", expand=True)

        self._refresh_ui()

    def _key_press(self, score):
        if len(self._arrows) >= self._ape:
            return
        if not self._can_enter(score):
            return
        self._arrows.append(score)
        self._refresh_ui()

    def _backspace(self):
        if self._arrows:
            self._arrows.pop()
            self._refresh_ui()

    def _can_enter(self, score):
        if not self._arrows:
            return True
        last_idx = score_index(self._arrows[-1])
        return score_index(score) >= last_idx

    def _refresh_ui(self):
        ape = self._ape
        # Arrow chips
        for i, lbl in enumerate(self._arrow_labels):
            if i < len(self._arrows):
                sc = self._arrows[i]
                bg, fg = arrow_colors(sc)
                lbl.config(text=sc, bg=bg, fg=fg)
            else:
                lbl.config(text="–", bg=C["panel_lt"], fg=C["border"])

        # Count / hint
        n = len(self._arrows)
        self._count_lbl.config(text=f"Arrows entered: {n} / {ape}")
        all_done = n == ape
        if all_done:
            self._hint_lbl.config(text="✓ All arrows entered — ready to save.",
                                  fg=C["accent"])
        elif n == 0:
            self._hint_lbl.config(
                text="Enter scores highest first: X → 10 → 9 → … → M",
                fg=C["muted"])
        else:
            last = self._arrows[-1]
            self._hint_lbl.config(
                text=f"Next arrow must be ≤  {last}", fg=C["muted"])

        # Total
        total = end_total(self._arrows)
        self._total_lbl.config(
            text=str(total),
            fg=C["gold"] if all_done else C["text"])

        # Key enable / disable
        for score, btn in self._key_buttons.items():
            if n >= ape or not self._can_enter(score):
                btn.config(state="disabled",
                           bg="#0e2016", fg="#2a4030", cursor="arrow")
            else:
                bg, fg = arrow_colors(score)
                btn.config(state="normal", bg=bg, fg=fg, cursor="hand2")

        # Backspace
        self._back_btn.config(state="normal" if n > 0 else "disabled",
                              fg=C["text"] if n > 0 else C["muted"])

        # Save
        if all_done:
            self._save_btn.config(state="normal",
                                  bg=C["gold"], fg="#0b1a10")
        else:
            self._save_btn.config(state="disabled",
                                  bg=C["accent_dim"], fg="#2a5a35")

    def _save(self):
        if len(self._arrows) != self._ape:
            return
        self.app.save_end(self._end_idx, list(self._arrows))

# ─────────────────────────── SCREEN: COMPLETE ───────────────────────────

class CompleteScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        session = self.app.session
        rnd = session["round"]
        archer = session["archer"]
        end_scores = session["end_scores"]
        total_ends = get_total_ends(rnd)
        ape = rnd["arrows_per_end"]
        grand_total = sum(end_total(e) for e in end_scores)
        all_arrows = [a for e in end_scores for a in e]
        tens = sum(1 for a in all_arrows if a in ("X", "10"))
        xs = sum(1 for a in all_arrows if a == "X")
        misses = sum(1 for a in all_arrows if a == "M")

        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview,
                          bg=C["panel"], troughcolor=C["bg"])
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        wrap = tk.Frame(canvas, bg=C["bg"])
        canvas.create_window((0, 0), window=wrap, anchor="nw")
        wrap.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        outer = tk.Frame(wrap, bg=C["bg"])
        outer.pack(fill="x", padx=16, pady=12)

        # ── Trophy hero ──
        hero = tk.Frame(outer, bg=C["panel_lt"], padx=20, pady=20)
        hero.pack(fill="x", pady=(0, 10))
        tk.Label(hero, text="🏆", bg=C["panel_lt"], font=("", 40)).pack()
        tk.Label(hero, text="Round Complete!", bg=C["panel_lt"], fg=C["gold"],
                 font=("Courier", 18, "bold")).pack(pady=(4, 2))
        tk.Label(hero, text=f"{archer['name']}  ·  {archer['equipment']}",
                 bg=C["panel_lt"], fg=C["muted"],
                 font=("Courier", 11)).pack()
        tk.Label(hero, text=rnd["name"], bg=C["panel_lt"], fg=C["muted"],
                 font=("Courier", 10)).pack(pady=(0, 8))
        tk.Label(hero, text=str(grand_total), bg=C["panel_lt"], fg=C["gold"],
                 font=("Courier", 48, "bold")).pack()
        tk.Label(hero, text=f"out of {len(all_arrows) * 10}",
                 bg=C["panel_lt"], fg=C["muted"],
                 font=("Courier", 11)).pack(pady=(0, 12))

        # Stats row
        stats = tk.Frame(hero, bg=C["panel"])
        stats.pack()
        for label, val, color in [
            ("10s + Xs", tens, C["accent"]),
            ("Xs", xs, C["accent"]),
            ("Misses", misses, C["danger"]),
        ]:
            s = tk.Frame(stats, bg=C["panel"], padx=16, pady=8)
            s.pack(side="left")
            tk.Label(s, text=str(val), bg=C["panel"], fg=color,
                     font=("Courier", 20, "bold")).pack()
            tk.Label(s, text=label, bg=C["panel"], fg=C["muted"],
                     font=("Courier", 9)).pack()

        # ── Scorecard ──
        sc_card = tk.Frame(outer, bg=C["panel"])
        sc_card.pack(fill="x", pady=(0, 10))
        hdr = tk.Frame(sc_card, bg=C["panel_lt"], padx=12, pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text="SCORECARD", bg=C["panel_lt"], fg=C["muted"],
                 font=("Courier", 9, "bold"), anchor="w").pack(side="left")
        tk.Label(hdr, text=f"{total_ends} ends · {ape} arrows/end",
                 bg=C["panel_lt"], fg=C["muted"],
                 font=("Courier", 9), anchor="e").pack(side="right")

        for i, arrows in enumerate(end_scores):
            rng, face = get_end_info(rnd, i)
            total = end_total(arrows)
            rt = running_total(end_scores, i)
            row = tk.Frame(sc_card, bg=C["panel"], padx=12, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=str(i + 1), bg=C["panel"], fg=C["muted"],
                     font=("Courier", 10), width=3).pack(side="left")
            tk.Label(row, text=rng, bg=C["panel"], fg=C["muted"],
                     font=("Courier", 9), width=6).pack(side="left")
            chips = tk.Frame(row, bg=C["panel"])
            chips.pack(side="left", expand=True, fill="x")
            for sc in arrows:
                bg, fg = arrow_colors(sc)
                tk.Label(chips, text=sc, bg=bg, fg=fg,
                         font=("Courier", 9, "bold"), width=3, height=1,
                         relief="flat").pack(side="left", padx=1)
            tk.Label(row, text=f"{total:>3}", bg=C["panel"], fg=C["text"],
                     font=("Courier", 12, "bold")).pack(side="right", padx=(8, 0))
            tk.Label(row, text=f"={rt}", bg=C["panel"], fg=C["muted"],
                     font=("Courier", 9)).pack(side="right")
            # Separator
            tk.Frame(sc_card, bg=C["border"], height=1).pack(fill="x")

        # Grand total row
        gt_row = tk.Frame(sc_card, bg=C["panel_lt"], padx=12, pady=8)
        gt_row.pack(fill="x")
        tk.Label(gt_row, text="Grand Total", bg=C["panel_lt"], fg=C["text"],
                 font=("Courier", 13, "bold"), anchor="w").pack(side="left")
        tk.Label(gt_row, text=str(grand_total), bg=C["panel_lt"], fg=C["gold"],
                 font=("Courier", 20, "bold")).pack(side="right")

        # ── New Session ──
        tk.Button(outer, text="← New Session",
                  command=self.app.show_setup,
                  bg=C["panel_lt"], fg=C["text"],
                  font=("Courier", 12, "bold"), relief="flat",
                  cursor="hand2", pady=10).pack(fill="x", pady=(0, 20))

# ─────────────────────────── APP SHELL ───────────────────────────

class ArcheryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Archery Score Recording")
        self.root.geometry("480x700")
        self.root.minsize(400, 580)
        self.root.configure(bg=C["bg"])

        # ── Header ──
        self.header = tk.Frame(self.root, bg=C["panel"], pady=12)
        self.header.pack(fill="x")
        self._back_btn = tk.Button(
            self.header, text="←", command=self._back_action,
            bg=C["panel"], fg=C["muted"],
            font=("Courier", 16), relief="flat", cursor="hand2",
            padx=8,
        )
        self._back_btn.pack(side="left", padx=(8, 0))
        tk.Label(self.header, text="🎯  Archery Score",
                 bg=C["panel"], fg=C["accent"],
                 font=("Courier", 14, "bold")).pack(side="left", padx=8)
        self._header_sub = tk.Label(self.header, text="",
                                    bg=C["panel"], fg=C["muted"],
                                    font=("Courier", 10))
        self._header_sub.pack(side="right", padx=12)

        # ── Screens ──
        self.session = None
        self._current_screen = None

        self.setup_screen  = SetupScreen(self.root, self)
        self.ends_screen   = EndsListScreen(self.root, self)
        self.entry_screen  = ScoreEntryScreen(self.root, self)
        self.complete_screen = CompleteScreen(self.root, self)

        self._back_map = {}  # screen → back action
        self.show_setup()

    def _set_screen(self, screen, sub="", back_action=None):
        if self._current_screen:
            self._current_screen.hide()
        screen.show()
        self._current_screen = screen
        self._header_sub.config(text=sub)
        self._back_action_fn = back_action
        self._back_btn.config(state="normal" if back_action else "disabled",
                              fg=C["muted"] if back_action else C["panel"])

    def _back_action(self):
        if self._back_action_fn:
            self._back_action_fn()

    def show_setup(self):
        self.session = None
        for w in self.setup_screen.winfo_children():
            w.destroy()
        self.setup_screen._build()
        self._set_screen(self.setup_screen, sub="", back_action=None)

    def start_session(self, rnd, archer):
        total_ends = get_total_ends(rnd)
        self.session = {
            "round": rnd,
            "archer": archer,
            "end_scores": [None] * total_ends,
        }
        self.show_ends()

    def show_ends(self):
        self.ends_screen.refresh()
        sub = self.session["round"]["name"] if self.session else ""
        self._set_screen(self.ends_screen, sub=sub, back_action=self.show_setup)

    def show_entry(self, end_idx):
        total = get_total_ends(self.session["round"])
        self.entry_screen.load_end(end_idx)
        self._set_screen(self.entry_screen,
                         sub=f"End {end_idx + 1} of {total}",
                         back_action=self.show_ends)

    def save_end(self, end_idx, arrows):
        self.session["end_scores"][end_idx] = arrows
        self.show_ends()

    def show_complete(self):
        self.complete_screen.refresh()
        self._set_screen(self.complete_screen,
                         sub="Session complete", back_action=None)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ArcheryApp()
    app.run()
