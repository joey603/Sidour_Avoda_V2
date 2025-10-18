import tkinter as tk
try:
    import ttkbootstrap as ttk
except Exception:  # Fallback si ttkbootstrap indisponible
    import tkinter.ttk as ttk


class CoachMarks:
    """Guided tour overlay: met en avant des widgets par étapes avec un panneau d'explication.

    steps: liste de dicts { 'widget': widget, 'title': str, 'text': str, 'placement': 'right'|'left'|'top'|'bottom' }
    """

    def __init__(self, root: tk.Misc, steps: list, on_finish=None):
        self.root = root
        self.steps = [s for s in (steps or []) if s.get('widget') is not None]
        self.index = 0
        self.overlay = None
        self.panel = None
        self.canvas = None
        self.on_finish = on_finish
        self._keys_bound = False
        self._nav_lock = False
        self._is_paused = False
        self._cfg_after = None  # throttle pour <Configure>

    def start(self):
        if not self.steps:
            return
        self._create_overlay()
        # Délai court pour laisser le layout se stabiliser (Windows)
        try:
            self.root.after(140, lambda: self._show_step(0))
        except Exception:
            self._show_step(0)
        # Navigation clavier globale (fonctionne même si une popup a le focus)
        self._bind_global_keys()
        # Exposer l'instance pour que l'interface puisse la mettre en pause/reprendre
        try:
            setattr(self.root, '_coach_instance', self)
        except Exception:
            pass

    def _create_overlay(self):
        # Créer une fenêtre overlay semi-transparente au-dessus de l'app
        ov = tk.Toplevel(self.root)
        ov.withdraw()
        try:
            # Opacité plus faible pour renforcer le contraste du highlight
            ov.attributes('-alpha', 0.12)
            # Lier au root sans topmost global (meilleure interactivité macOS)
            ov.transient(self.root)
        except Exception:
            pass
        ov.overrideredirect(True)
        ov.configure(bg='black')
        self.overlay = ov

        # Canvas couvrant tout l'écran pour dessiner un cadre autour de la cible
        cv = tk.Canvas(ov, highlightthickness=0, bd=0, bg='black')
        cv.pack(fill='both', expand=True)
        self.canvas = cv

        # Panneau d'info (enfant de l'overlay pour garantir le clic au-dessus)
        pnl = tk.Toplevel(self.overlay)
        try:
            pnl.attributes('-topmost', True)
        except Exception:
            pass
        pnl.overrideredirect(True)
        # Fond opaque pour l'infobulle
        try:
            pnl.wm_attributes('-alpha', 1.0)
        except Exception:
            pass
        pnl.configure(bg='white')
        # Lier visuellement au root (améliore le focus/stacking)
        try:
            pnl.transient(self.overlay)
        except Exception:
            pass
        self.panel = pnl

        # Ne pas utiliser de grab pour éviter de bloquer les clics entre étapes

        # Navigation clavier (locale au panneau) - seulement Escape; flèches gérées globalement pour éviter doubles appels
        try:
            self.panel.bind('<Escape>', lambda e: self._finish())
        except Exception:
            pass

        # Repositionner l'overlay sur l'écran principal
        self._resize_to_screen()
        try:
            # Reagir aux changements de taille de la fenêtre principale
            self.root.bind('<Configure>', self._on_configure, add='+')
        except Exception:
            pass

    def _resize_to_screen(self):
        # Couvrir tout l'écran (ou au minimum la fenêtre root)
        try:
            sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        except Exception:
            sw, sh = 1600, 900
        self.overlay.geometry(f"{int(sw)}x{int(sh)}+0+0")
        self.overlay.deiconify()

    def _on_configure(self, _event=None):
        # Throttle des rafraîchissements pour éviter le clignotement (Windows)
        if self._is_paused:
            return
        try:
            if self._cfg_after is not None:
                self.root.after_cancel(self._cfg_after)
        except Exception:
            pass
        def _do_update():
            try:
                self._resize_to_screen()
                self._redraw()
            finally:
                self._cfg_after = None
        try:
            self._cfg_after = self.root.after(140, _do_update)
        except Exception:
            # Fallback sans throttle
            self._resize_to_screen(); self._redraw()

    def _current(self):
        if 0 <= self.index < len(self.steps):
            return self.steps[self.index]
        return None

    def _get_widget_bbox(self, w: tk.Misc):
        try:
            w.update_idletasks()
            x = w.winfo_rootx(); y = w.winfo_rooty()
            width = max(w.winfo_width(), w.winfo_reqwidth())
            height = max(w.winfo_height(), w.winfo_reqheight())
            return x, y, width, height
        except Exception:
            return 100, 100, 200, 80

    def _show_step(self, idx: int):
        if self._is_paused:
            return
        self.index = max(0, min(idx, len(self.steps)-1))
        self._redraw()

    def _redraw(self):
        if self._is_paused:
            return
        step = self._current()
        if step is None:
            self._finish()
            return
        # Pas de grab: éviter de bloquer l'UI
        # Hook d'entrée d'étape (permet d'ouvrir une popup, etc.)
        try:
            on_enter = step.get('on_enter')
            if callable(on_enter):
                on_enter()
        except Exception:
            pass
        widget = step.get('widget')
        try:
            if callable(widget):
                widget = widget()
        except Exception:
            pass
        title = step.get('title') or ''
        text = step.get('text') or ''
        placement = (step.get('placement') or 'right').lower()

        # Dessiner le cadre autour du widget ciblé
        x, y, w, h = self._get_widget_bbox(widget)
        self.canvas.delete('all')
        # Bordure cyan renforcée + halo pour un highlight plus prononcé
        pad = 8
        self.canvas.create_rectangle(x-pad, y-pad, x+w+pad, y+h+pad, outline='#00E5FF', width=8)
        # Halo extérieur secondaire plus saturé
        self.canvas.create_rectangle(x-pad-4, y-pad-4, x+w+pad+4, y+h+pad+4, outline='#00BCD4', width=4)

        # Construire le panneau d'info
        for child in list(self.panel.children.values()):
            try:
                child.destroy()
            except Exception:
                pass
        frame = tk.Frame(self.panel, bg='white')
        frame.pack(fill='both', expand=True, padx=12, pady=12)
        # Titre avec icône tutoriel
        header = tk.Frame(frame, bg='white')
        header.pack(fill='x')
        tk.Label(header, text='🎓', font=('Helvetica', 14, 'bold'), bg='white', fg='#222222').pack(side='left', padx=(0,6))
        tk.Label(header, text=title.replace('Guided Tour', 'Tutorial'), font=('Helvetica', 12, 'bold'), bg='white', fg='#222222').pack(side='left')
        body = tk.Label(frame, text=text, wraplength=360, justify='left', bg='white', fg='#222222')
        body.pack(fill='x', pady=(6, 10))
        btns = ttk.Frame(frame)
        btns.pack(fill='x')
        def _call_cb(cb):
            try:
                cb(self)
            except TypeError:
                try:
                    cb()
                except Exception:
                    pass
        def _next():
            try:
                st = self._current() or {}
                cb = st.get('on_next')
                if callable(cb):
                    _call_cb(cb)
                # Si on est à la dernière étape, fermer le tutoriel
                if self.index >= len(self.steps) - 1:
                    self._finish()
                else:
                    self._show_step(self.index+1)
            except Exception:
                pass
        def _prev():
            try:
                st = self._current() or {}
                cb = st.get('on_prev')
                if callable(cb):
                    _call_cb(cb)
                target_idx = st.get('prev_index')
                if isinstance(target_idx, int):
                    self._show_step(target_idx)
                else:
                    self._show_step(self.index-1)
            except Exception:
                pass
        ttk.Button(btns, text='Close', command=self._finish).pack(side='left')
        ttk.Button(btns, text='Next ▶', command=_next).pack(side='right')
        ttk.Button(btns, text='◀ Previous', command=_prev).pack(side='right', padx=6)

        # Dimensionner et positionner le panneau autour du widget selon placement
        try:
            self.panel.update_idletasks()
            pw = max(self.panel.winfo_reqwidth(), 420)
            ph = max(self.panel.winfo_reqheight(), 140)
        except Exception:
            pw, ph = 420, 160
        # Position par défaut à droite
        px, py = x + w + 12, y
        if placement == 'left':
            px, py = x - pw - 12, y
        elif placement == 'top':
            px = x + (w - pw) // 2
            py = y - ph - 12
        elif placement == 'bottom':
            px = x + (w - pw) // 2
            py = y + h + 12
        elif placement == 'center':
            px = x + (w - pw) // 2
            py = y + (h - ph) // 2
        # Garde-fous pour rester à l'écran
        try:
            sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        except Exception:
            sw, sh = 1600, 900
        px = max(8, min(px, sw - pw - 8))
        py = max(8, min(py, sh - ph - 8))
        self.panel.geometry(f"{int(pw)}x{int(ph)}+{int(px)}+{int(py)}")
        try:
            # Z-order minimal pour éviter le clignotement: lever uniquement le panneau
            try:
                self.panel.lift()
            except Exception:
                pass
            try:
                self.panel.focus_force()
            except Exception:
                pass
            try:
                self.panel.update_idletasks()
                self.canvas.update_idletasks()
            except Exception:
                pass
        except Exception:
            pass

    def _finish(self):
        try:
            self._unbind_global_keys()
        except Exception:
            pass
        # Fermer toutes les popups du tuto (Add Site, Manage Site, etc.) si ouvertes
        try:
            try:
                # Si l'interface a exposé des fenêtres du tuto
                if hasattr(self.root, 'winfo_children'):
                    for w in list(self.root.winfo_children()):
                        try:
                            if isinstance(w, tk.Toplevel) and w.winfo_exists():
                                title = ''
                                try:
                                    title = w.title()
                                except Exception:
                                    pass
                                if title in ('Add Site', 'Manage Site'):
                                    w.destroy()
                        except Exception:
                            pass
            except Exception:
                pass
        except Exception:
            pass
        try:
            if self.panel is not None:
                self.panel.destroy()
        except Exception:
            pass
        try:
            if self.overlay is not None:
                self.overlay.destroy()
        except Exception:
            pass
        try:
            self.root.unbind('<Configure>')
        except Exception:
            pass
        # Déclarer la fin du guided tour côté interface si disponible
        try:
            if hasattr(self.root, 'nametowidget'):
                # Chercher un attribut de l'interface pour flag
                # On suppose que l'interface a mis self._guided_tour_active = True
                # Impossible d'accéder direct; c'est géré dans interface_2 avec on_finish
                pass
        except Exception:
            pass
        # Callback de fin (pour nettoyage externe)
        try:
            if callable(self.on_finish):
                self.on_finish()
        except Exception:
            pass

    def _call_callback(self, cb):
        try:
            cb(self)
        except TypeError:
            try:
                cb()
            except Exception:
                pass

    def _go_next(self, _event=None):
        try:
            if self._nav_lock:
                return
            if self._is_paused:
                return
            self._nav_lock = True
            try:
                st = (self._current() or {})
                cb = st.get('on_next')
                if callable(cb):
                    self._call_callback(cb)
                # Si dernière étape → fermer, sinon avancer
                if self.index >= len(self.steps) - 1:
                    self._finish()
                else:
                    self._show_step(self.index + 1)
            finally:
                try:
                    # Débloquer après un court délai pour éviter double déclenchement
                    self.root.after(120, lambda: setattr(self, '_nav_lock', False))
                except Exception:
                    self._nav_lock = False
        except Exception:
            pass

    def _go_prev(self, _event=None):
        try:
            if self._nav_lock:
                return
            if self._is_paused:
                return
            self._nav_lock = True
            try:
                st = (self._current() or {})
                cb = st.get('on_prev')
                if callable(cb):
                    self._call_callback(cb)
                target_idx = st.get('prev_index')
                if isinstance(target_idx, int):
                    self._show_step(target_idx)
                else:
                    self._show_step(self.index - 1)
            finally:
                try:
                    self.root.after(120, lambda: setattr(self, '_nav_lock', False))
                except Exception:
                    self._nav_lock = False
        except Exception:
            pass

    def _bind_global_keys(self):
        if self._keys_bound:
            return
        try:
            self.root.bind_all('<Escape>', lambda e: self._finish())
            self.root.bind_all('<Right>', self._go_next)
            self.root.bind_all('<Left>', self._go_prev)
            self._keys_bound = True
        except Exception:
            pass

    def _unbind_global_keys(self):
        if not self._keys_bound:
            return
        try:
            self.root.unbind_all('<Escape>')
            self.root.unbind_all('<Right>')
            self.root.unbind_all('<Left>')
        except Exception:
            pass
        self._keys_bound = False


