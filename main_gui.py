
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pipeline_adapter import run_simulation

APP_TITLE = "Rapid Ground Motion 1.3"

SECTION_COLORS = {
    "eq": "#F0F7FF",
    "data": "#F7FFF2",
    "opt": "#FFF7F0",
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x800")
        self.minsize(820, 640)
        self.configure(bg="#f5f6f9")
        self._init_style()

        self.var_name    = tk.StringVar()
        self.var_lon     = tk.StringVar()
        self.var_lat     = tk.StringVar()
        self.var_magval  = tk.StringVar()
        self.var_magtype = tk.StringVar(value="Mw")
        self.var_event   = tk.StringVar()
        self.var_depth   = tk.StringVar()
        self.var_radius  = tk.StringVar()
        self.var_vs30    = tk.StringVar()
        self.var_outdir  = tk.StringVar()
        self.var_convert = tk.StringVar(value="No")
        self.var_gmpe_mode = tk.StringVar(value="Use default")
        self.var_save_per_model = tk.StringVar(value="No")
        self.selected_gmpes = []

        outer = ttk.Frame(self, padding=16)
        outer.pack(fill=tk.BOTH, expand=True)

        eq_frame = self._section(outer, "Earthquake Info", SECTION_COLORS["eq"])
        eq_content = ttk.Frame(eq_frame, padding=8); eq_content.pack(fill=tk.X, expand=True)

        self._row(eq_content, "Event name", ttk.Entry(eq_content, textvariable=self.var_name, width=58), r=0)
        self._row(eq_content, "Longitude",  ttk.Entry(eq_content, textvariable=self.var_lon,  width=24), r=1)
        self._row(eq_content, "Latitude",   ttk.Entry(eq_content, textvariable=self.var_lat,  width=24), r=2)
        self._row(eq_content, "Magnitude value", ttk.Entry(eq_content, textvariable=self.var_magval, width=24), r=3)
        self._row(eq_content, "Magnitude type",  ttk.Combobox(eq_content, textvariable=self.var_magtype, values=["Ms","Mw"], state="readonly", width=8), r=4)
        self._row(eq_content, "Event date (DDMMYYYY)", ttk.Entry(eq_content, textvariable=self.var_event, width=24), r=5)
        self._row(eq_content, "Depth (km)",  ttk.Entry(eq_content, textvariable=self.var_depth, width=24), r=6)
        self._row(eq_content, "Radius (km)", ttk.Entry(eq_content, textvariable=self.var_radius, width=24), r=7)

        data_frame = self._section(outer, "Data", SECTION_COLORS["data"])
        data_content = ttk.Frame(data_frame, padding=8); data_content.pack(fill=tk.X, expand=True)

        vs30_line = ttk.Frame(data_content)
        ttk.Entry(vs30_line, textvariable=self.var_vs30, width=64).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(vs30_line, text="Browse", command=self.choose_vs30).pack(side=tk.LEFT)
        self._row(data_content, "VS30 GeoTIFF", vs30_line, r=0)

        out_line = ttk.Frame(data_content)
        ttk.Entry(out_line, textvariable=self.var_outdir, width=64).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(out_line, text="Browse", command=self.choose_dir).pack(side=tk.LEFT)
        self._row(data_content, "Output folder", out_line, r=1)

        opt_frame = self._section(outer, "Options", SECTION_COLORS["opt"])
        opt_content = ttk.Frame(opt_frame, padding=8); opt_content.pack(fill=tk.X, expand=True)

        self._row(opt_content, "Convert to intensity", ttk.Combobox(opt_content, textvariable=self.var_convert, values=["Yes","No"], state="readonly", width=10), r=0)

        gmpe_line = ttk.Frame(opt_content)
        ttk.Combobox(gmpe_line, textvariable=self.var_gmpe_mode, values=["Use default","Choose from list"], state="readonly", width=20).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(gmpe_line, text="Select GMPE...", command=self.open_gmpe_selector).pack(side=tk.LEFT)
        self._row(opt_content, "GMPE selection", gmpe_line, r=1)

        self._row(opt_content, "Save per-GMPE maps", ttk.Combobox(opt_content, textvariable=self.var_save_per_model, values=["Yes","No"], state="readonly", width=10), r=2)

        run = ttk.Frame(outer, padding=(0,8)); run.pack(fill=tk.X, pady=(8,0))
        self.status = tk.StringVar(value="Ready")
        ttk.Label(run, textvariable=self.status, foreground="#1b7f2a").pack(side=tk.LEFT)
        ttk.Button(run, text="Run", command=self.on_start).pack(side=tk.RIGHT)

    def _init_style(self):
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(10,6))
        style.configure("TEntry", padding=(6,4))
        style.configure("TLabelframe.Label", font=("Segoe UI Semibold", 11))

    def _section(self, parent, title, bg):
        frame = tk.LabelFrame(parent, text=title, bg=bg, fg="#333", padx=8, pady=8, font=("Segoe UI Semibold", 11))
        frame.pack(fill=tk.X, pady=8)
        return frame

    def _row(self, parent, label, widget, r):
        lbl = ttk.Label(parent, text=label, width=24, anchor="e")
        lbl.grid(row=r, column=0, sticky="e", padx=(0,10), pady=4)
        widget.grid(row=r, column=1, sticky="w", pady=4)

    def choose_dir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d: self.var_outdir.set(d)

    def choose_vs30(self):
        path = filedialog.askopenfilename(title="Choose VS30 GeoTIFF", filetypes=[("GeoTIFF",".tif .tiff"), ("All files","*.*")])
        if path: self.var_vs30.set(path)

    def open_gmpe_selector(self):
        try:
            import gmpe_registry
            names = gmpe_registry.list_gmpes()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot list GMPEs: {e}")
            return
        win = tk.Toplevel(self); win.title("Choose GMPE"); win.resizable(False, False)
        frm = ttk.Frame(win, padding=12); frm.pack(fill=tk.BOTH, expand=True)

        fline = ttk.Frame(frm); fline.pack(fill=tk.X, pady=(0,6))
        q = tk.StringVar()
        ttk.Label(fline, text="Filter:").pack(side=tk.LEFT, padx=(0,6))
        ent = ttk.Entry(fline, textvariable=q, width=24); ent.pack(side=tk.LEFT)

        box = ttk.Frame(frm); box.pack(fill=tk.BOTH, expand=True)
        vars_map = {}
        def render():
            for w in box.winfo_children(): w.destroy()
            kw = q.get().strip().lower()
            row = 0
            for n in names:
                if kw and kw not in n.lower(): continue
                v = vars_map.get(n) or tk.BooleanVar(value=(n in self.selected_gmpes))
                vars_map[n] = v
                ttk.Checkbutton(box, text=n, variable=v).grid(row=row, column=0, sticky='w', padx=4, pady=2)
                row += 1
        render()
        ent.bind("<KeyRelease>", lambda e: render())

        ttk.Separator(frm).pack(fill=tk.X, pady=6)
        ttk.Button(frm, text="OK", command=lambda: (setattr(self, "selected_gmpes", [n for n,v in vars_map.items() if v.get()]), win.destroy())).pack(side=tk.RIGHT)

    def on_start(self):
        try:
            name = self.var_name.get().strip() or "event"
            lon = float(self.var_lon.get()); lat = float(self.var_lat.get())
            mag_value = float(self.var_magval.get())
            mag_type  = self.var_magtype.get().strip()
            event_date = self.var_event.get().strip()
            depth = float(self.var_depth.get())
            radius_km = float(self.var_radius.get())
            vs30_path = self.var_vs30.get().strip()
            outdir    = self.var_outdir.get().strip()
            convert_flag = (self.var_convert.get() == "Yes")
            # Always pass selected subset if user checked any; otherwise None => use all
            selected = self.selected_gmpes if self.selected_gmpes else None
        except Exception as e:
            messagebox.showerror("Input error", str(e)); return

        self.status.set("Running...")
        def task():
            try:
                (pga_path, intensity_path, weights_txt, per_model_paths, weights_list) = run_simulation(
                    name=name, lon=lon, lat=lat, mag_value=mag_value, mag_type=mag_type, event_date=event_date,
                    depth_km=depth, radius_km=radius_km, vs30_path=vs30_path, out_dir=outdir,
                    convert_to_intensity=convert_flag, selected_gmpes=selected,
                    save_per_model=(self.var_save_per_model.get()=="Yes")
                )
                msg = (
                    f"PGA saved to:\n{pga_path}\n\n"
                    "GMPE weights (also saved to file):\n"
                    + "\n".join([f"  {name}: {w:.4f}" for name, w in weights_list])
                    + f"\n\nWeights file:\n{weights_txt}"
                )
                if per_model_paths:
                    msg += "\n\nPer-GMPE maps:\n" + "\n".join([f"  {p}" for p in per_model_paths])
                if intensity_path:
                    msg += f"\n\nIntensity saved to:\n{intensity_path} (and class map)"
                self.status.set("Done")
                messagebox.showinfo("Finished", msg)
            except Exception as e:
                self.status.set("Failed"); messagebox.showerror("Error", str(e))
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
