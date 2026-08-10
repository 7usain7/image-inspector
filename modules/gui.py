"""
Image Inspector GUI Module
==========================
Modern Tkinter Graphical User Interface for Image Inspector.
Uses the core backend functions from the modules package.
"""

import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any, List, Tuple

from PIL import Image, ImageTk

from modules.metadata import extract_metadata_dict
from modules.key_extractor import extract_keys, format_key_report, key_extractor


# Theme Color Palette (Modern Dark Theme)
BG_DARK = "#181825"
BG_CARD = "#1e1e2e"
BG_CARD_LIGHT = "#25263a"
BG_INPUT = "#313244"
TEXT_MAIN = "#cdd6f4"
TEXT_MUTED = "#a6adc8"
ACCENT_BLUE = "#89b4fa"
ACCENT_GREEN = "#a6e3a1"
ACCENT_RED = "#f38ba8"
BORDER_COLOR = "#45475a"
BTN_HOVER = "#585b70"


class ImageInspectorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Inspector - OSINT & Forensic Analysis")
        self.root.geometry("1050x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG_DARK)

        self.current_image_path: Optional[str] = None
        self.current_thumbnail: Optional[ImageTk.PhotoImage] = None
        self.extracted_metadata: Dict[str, Any] = {}
        self.extracted_key_report: str = ""
        self.extracted_keys_raw: str = ""
        self.google_maps_url: Optional[str] = None
        self.osm_url: Optional[str] = None

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure General TTK Widgets
        style.configure("TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("CardLight.TFrame", background=BG_CARD_LIGHT)

        style.configure(
            "TLabel",
            background=BG_DARK,
            foreground=TEXT_MAIN,
            font=("Helvetica", 11),
        )
        style.configure(
            "Card.TLabel",
            background=BG_CARD,
            foreground=TEXT_MAIN,
            font=("Helvetica", 11),
        )
        style.configure(
            "CardMuted.TLabel",
            background=BG_CARD,
            foreground=TEXT_MUTED,
            font=("Helvetica", 10),
        )
        style.configure(
            "Header.TLabel",
            background=BG_DARK,
            foreground=ACCENT_BLUE,
            font=("Helvetica", 16, "bold"),
        )
        style.configure(
            "SectionHeader.TLabel",
            background=BG_CARD,
            foreground=ACCENT_BLUE,
            font=("Helvetica", 12, "bold"),
        )

        # Notebook (Tabs) Styling
        style.configure(
            "TNotebook",
            background=BG_DARK,
            borderwidth=0,
            tabmargins=[2, 5, 2, 0],
        )
        style.configure(
            "TNotebook.Tab",
            background=BG_INPUT,
            foreground=TEXT_MUTED,
            padding=[16, 8],
            font=("Helvetica", 11, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BG_CARD), ("active", BTN_HOVER)],
            foreground=[("selected", ACCENT_BLUE), ("active", TEXT_MAIN)],
        )

        # Buttons Styling
        style.configure(
            "Primary.TButton",
            background=ACCENT_BLUE,
            foreground="#11111b",
            font=("Helvetica", 11, "bold"),
            padding=[14, 6],
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#b4befe"), ("pressed", "#74c7ec")],
        )

        style.configure(
            "Action.TButton",
            background=BG_INPUT,
            foreground=TEXT_MAIN,
            font=("Helvetica", 10, "bold"),
            padding=[10, 5],
            borderwidth=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", BTN_HOVER), ("pressed", "#6c7086")],
            foreground=[("active", ACCENT_BLUE)],
        )

    def _build_ui(self):
        # 1. Top Header Bar
        header_frame = tk.Frame(self.root, bg=BG_DARK, pady=10, padx=20)
        header_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            header_frame,
            text="🔍 IMAGE INSPECTOR",
            style="Header.TLabel",
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_frame,
            text="Digital Forensics & OSINT Reconnaissance Tool",
            bg=BG_DARK,
            fg=TEXT_MUTED,
            font=("Helvetica", 10, "italic"),
        )
        subtitle_label.pack(side=tk.LEFT, padx=(12, 0), pady=(4, 0))

        # 2. File Selection Bar
        file_bar = tk.Frame(self.root, bg=BG_CARD, pady=10, padx=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        file_bar.pack(fill=tk.X, padx=15, pady=(0, 10))

        lbl_path = tk.Label(file_bar, text="Target Image:", bg=BG_CARD, fg=TEXT_MAIN, font=("Helvetica", 11, "bold"))
        lbl_path.pack(side=tk.LEFT, padx=(0, 10))

        self.entry_path = tk.Entry(
            file_bar,
            bg=BG_INPUT,
            fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            relief=tk.FLAT,
            font=("Helvetica", 11),
            highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE,
            highlightthickness=1,
        )
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=4)
        self.entry_path.bind("<Return>", lambda e: self.inspect_image())

        btn_browse = ttk.Button(file_bar, text="📁 Browse...", style="Action.TButton", command=self.browse_file)
        btn_browse.pack(side=tk.LEFT, padx=(0, 8))

        btn_inspect = ttk.Button(file_bar, text="⚡ Inspect Image", style="Primary.TButton", command=self.inspect_image)
        btn_inspect.pack(side=tk.LEFT)

        # 3. Main Horizontal Split Area
        main_container = tk.Frame(self.root, bg=BG_DARK)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        # --- LEFT PANE (Image Preview & File Specs) ---
        left_pane = tk.Frame(main_container, bg=BG_CARD, width=280, highlightbackground=BORDER_COLOR, highlightthickness=1)
        left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_pane.pack_propagate(False)

        lbl_preview_title = ttk.Label(left_pane, text="🖼️ IMAGE PREVIEW", style="SectionHeader.TLabel")
        lbl_preview_title.pack(anchor="w", padx=15, pady=(12, 8))

        # Thumbnail Box
        self.thumb_canvas = tk.Canvas(left_pane, width=240, height=220, bg=BG_CARD_LIGHT, highlightthickness=0)
        self.thumb_canvas.pack(padx=15, pady=(0, 10))
        self.thumb_canvas_text = self.thumb_canvas.create_text(
            120, 110, text="No Image Loaded", fill=TEXT_MUTED, font=("Helvetica", 11)
        )

        # Quick Facts Box
        facts_frame = tk.Frame(left_pane, bg=BG_CARD_LIGHT, padx=12, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        facts_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        self.lbl_fact_filename = tk.Label(facts_frame, text="File: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10, "bold"), anchor="w")
        self.lbl_fact_filename.pack(fill=tk.X, pady=2)

        self.lbl_fact_format = tk.Label(facts_frame, text="Format: -", bg=BG_CARD_LIGHT, fg=TEXT_MUTED, font=("Helvetica", 10), anchor="w")
        self.lbl_fact_format.pack(fill=tk.X, pady=2)

        self.lbl_fact_dims = tk.Label(facts_frame, text="Dimensions: -", bg=BG_CARD_LIGHT, fg=TEXT_MUTED, font=("Helvetica", 10), anchor="w")
        self.lbl_fact_dims.pack(fill=tk.X, pady=2)

        self.lbl_fact_size = tk.Label(facts_frame, text="File Size: -", bg=BG_CARD_LIGHT, fg=TEXT_MUTED, font=("Helvetica", 10), anchor="w")
        self.lbl_fact_size.pack(fill=tk.X, pady=2)

        # --- RIGHT PANE (Tabbed Inspection Notebook) ---
        right_pane = tk.Frame(main_container, bg=BG_DARK)
        right_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(right_pane)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # TAB 1: Structured Metadata Cards
        self.tab_metadata = tk.Frame(self.notebook, bg=BG_CARD, padx=15, pady=15)
        self.notebook.add(self.tab_metadata, text=" 📊 Metadata (EXIF & GPS) ")
        self._build_metadata_tab()

        # TAB 2: Key & Steganography Extractor
        self.tab_stego = tk.Frame(self.notebook, bg=BG_CARD, padx=15, pady=15)
        self.notebook.add(self.tab_stego, text=" 🔐 Keys (PGP / SSH) ")
        self._build_stego_tab()

        # TAB 3: Complete Raw Report
        self.tab_report = tk.Frame(self.notebook, bg=BG_CARD, padx=15, pady=15)
        self.notebook.add(self.tab_report, text=" 📄 Complete Report ")
        self._build_report_tab()

        # 4. Status Bar
        self.status_bar = tk.Frame(self.root, bg=BG_CARD, height=28, padx=15, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = tk.Label(self.status_bar, text="Status: Ready", bg=BG_CARD, fg=TEXT_MUTED, font=("Helvetica", 9))
        self.lbl_status.pack(side=tk.LEFT, pady=3)

    def _build_metadata_tab(self):
        canvas = tk.Canvas(self.tab_metadata, bg=BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_metadata, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_CARD)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=680)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Card 1: 📅 Date & Time
        card_dt = tk.LabelFrame(
            scrollable_frame,
            text=" 📅 DATE & TIME ",
            bg=BG_CARD_LIGHT,
            fg=ACCENT_BLUE,
            font=("Helvetica", 11, "bold"),
            padx=15,
            pady=10,
            relief=tk.GROOVE,
            highlightbackground=BORDER_COLOR,
        )
        card_dt.pack(fill=tk.X, pady=(0, 12))

        self.lbl_dt_taken = tk.Label(card_dt, text="• Date/Time Taken: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dt_taken.pack(fill=tk.X, pady=2)
        self.lbl_dt_offset = tk.Label(card_dt, text="• Timezone Offset: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dt_offset.pack(fill=tk.X, pady=2)
        self.lbl_dt_modified = tk.Label(card_dt, text="• Date Modified: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dt_modified.pack(fill=tk.X, pady=2)
        self.lbl_dt_gps = tk.Label(card_dt, text="• GPS UTC Timestamp: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dt_gps.pack(fill=tk.X, pady=2)

        # Card 2: 📱 Device & Camera Details
        card_dev = tk.LabelFrame(
            scrollable_frame,
            text=" 📱 DEVICE & CAMERA HARDWARE ",
            bg=BG_CARD_LIGHT,
            fg=ACCENT_BLUE,
            font=("Helvetica", 11, "bold"),
            padx=15,
            pady=10,
            relief=tk.GROOVE,
            highlightbackground=BORDER_COLOR,
        )
        card_dev.pack(fill=tk.X, pady=(0, 12))

        self.lbl_dev_make = tk.Label(card_dev, text="• Camera Make: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dev_make.pack(fill=tk.X, pady=2)
        self.lbl_dev_model = tk.Label(card_dev, text="• Camera Model: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dev_model.pack(fill=tk.X, pady=2)
        self.lbl_dev_software = tk.Label(card_dev, text="• OS / Software: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dev_software.pack(fill=tk.X, pady=2)
        self.lbl_dev_lens = tk.Label(card_dev, text="• Lens Model: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dev_lens.pack(fill=tk.X, pady=2)
        self.lbl_dev_host = tk.Label(card_dev, text="• Host Computer: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dev_host.pack(fill=tk.X, pady=2)
        self.lbl_dev_owner = tk.Label(card_dev, text="• Artist / Owner: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_dev_owner.pack(fill=tk.X, pady=2)

        # Card 3: 📍 Geolocation (GPS)
        card_geo = tk.LabelFrame(
            scrollable_frame,
            text=" 📍 GEOLOCATION (GPS) ",
            bg=BG_CARD_LIGHT,
            fg=ACCENT_BLUE,
            font=("Helvetica", 11, "bold"),
            padx=15,
            pady=10,
            relief=tk.GROOVE,
            highlightbackground=BORDER_COLOR,
        )
        card_geo.pack(fill=tk.X, pady=(0, 12))

        self.lbl_geo_dms = tk.Label(card_geo, text="• DMS Coordinates: No GPS Data", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_geo_dms.pack(fill=tk.X, pady=2)
        self.lbl_geo_dec = tk.Label(card_geo, text="• Decimal Coordinates: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_geo_dec.pack(fill=tk.X, pady=2)
        self.lbl_geo_alt = tk.Label(card_geo, text="• Altitude: -", bg=BG_CARD_LIGHT, fg=TEXT_MAIN, font=("Helvetica", 10), anchor="w")
        self.lbl_geo_alt.pack(fill=tk.X, pady=2)

        # Interactive Map Buttons
        map_btn_frame = tk.Frame(card_geo, bg=BG_CARD_LIGHT)
        map_btn_frame.pack(anchor="w", pady=(8, 4))

        self.btn_gmaps = ttk.Button(map_btn_frame, text="🌐 Open in Google Maps", style="Action.TButton", command=self.open_google_maps, state=tk.DISABLED)
        self.btn_gmaps.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_osm = ttk.Button(map_btn_frame, text="🗺️ Open in OpenStreetMap", style="Action.TButton", command=self.open_osm, state=tk.DISABLED)
        self.btn_osm.pack(side=tk.LEFT)

    def _build_stego_tab(self):
        top_bar = tk.Frame(self.tab_stego, bg=BG_CARD)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        self.lbl_stego_status = tk.Label(
            top_bar,
            text="Detected: 0 Cryptographic Keys (PGP / SSH)",
            bg=BG_CARD,
            fg=ACCENT_BLUE,
            font=("Helvetica", 12, "bold"),
        )
        self.lbl_stego_status.pack(side=tk.LEFT)

        btn_copy_keys = ttk.Button(top_bar, text="📋 Copy Key Content", style="Action.TButton", command=self.copy_key_content)
        btn_copy_keys.pack(side=tk.RIGHT, padx=(6, 0))

        btn_save_key = ttk.Button(top_bar, text="💾 Save Key to File", style="Action.TButton", command=self.save_key_file)
        btn_save_key.pack(side=tk.RIGHT)

        self.txt_keys = tk.Text(
            self.tab_stego,
            bg=BG_CARD_LIGHT,
            fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            font=("Menlo", 10),
            relief=tk.FLAT,
            padx=12,
            pady=12,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self.txt_keys.pack(fill=tk.BOTH, expand=True)

    def _build_report_tab(self):
        top_bar = tk.Frame(self.tab_report, bg=BG_CARD)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        lbl_title = tk.Label(top_bar, text="Generated Analysis Report", bg=BG_CARD, fg=TEXT_MAIN, font=("Helvetica", 11, "bold"))
        lbl_title.pack(side=tk.LEFT)

        btn_copy_rep = ttk.Button(top_bar, text="📋 Copy Full Report", style="Action.TButton", command=self.copy_full_report)
        btn_copy_rep.pack(side=tk.RIGHT, padx=(6, 0))

        btn_save_rep = ttk.Button(top_bar, text="💾 Export Report (.txt)", style="Action.TButton", command=self.export_report)
        btn_save_rep.pack(side=tk.RIGHT)

        self.txt_report = tk.Text(
            self.tab_report,
            bg=BG_CARD_LIGHT,
            fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            font=("Menlo", 10),
            relief=tk.FLAT,
            padx=12,
            pady=12,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self.txt_report.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        filetypes = [
            ("All Supported Images", "*.jpg *.jpeg *.png *.tiff *.tif *.webp *.bmp"),
            ("JPEG Images", "*.jpg *.jpeg"),
            ("PNG Images", "*.png"),
            ("TIFF Images", "*.tiff *.tif"),
            ("All Files", "*.*"),
        ]
        chosen = filedialog.askopenfilename(
            title="Select Image to Inspect",
            initialdir=os.path.join(os.getcwd(), "image-examples") if os.path.exists("image-examples") else os.getcwd(),
            filetypes=filetypes,
        )
        if chosen:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, chosen)
            self.inspect_image()

    def inspect_image(self):
        image_path = self.entry_path.get().strip()
        if not image_path:
            messagebox.showwarning("No Image Selected", "Please select or enter an image path to inspect.")
            return

        if not os.path.isfile(image_path):
            messagebox.showerror("File Not Found", f"The file '{image_path}' does not exist.")
            return

        self.current_image_path = image_path
        self.lbl_status.config(text=f"Status: Inspecting '{os.path.basename(image_path)}'...")
        self.root.update_idletasks()

        # 1. Update Preview Thumbnail & File Specs
        self._load_thumbnail(image_path)

        # 2. Extract Metadata using module function
        self.extracted_metadata = extract_metadata_dict(image_path)
        self._populate_metadata_tab(self.extracted_metadata)

        # 3. Extract Cryptographic Keys (PGP / SSH) using module function
        found_keys = extract_keys(image_path)
        self.extracted_key_report = format_key_report(found_keys)
        self._populate_stego_tab(found_keys)

        # 4. Populate Full Report Tab
        combined_report = []
        if "report" in self.extracted_metadata:
            combined_report.append(self.extracted_metadata["report"])
        if self.extracted_key_report:
            combined_report.append(self.extracted_key_report)

        full_text = "\n\n".join(combined_report)
        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert(tk.END, full_text)

        self.lbl_status.config(text=f"Status: Analysis complete for '{os.path.basename(image_path)}'.")

    def _load_thumbnail(self, image_path: str):
        try:
            with Image.open(image_path) as img:
                fmt = img.format or "Unknown"
                w, h = img.width, img.height
                size_bytes = os.path.getsize(image_path)

                self.lbl_fact_filename.config(text=f"File: {os.path.basename(image_path)}")
                self.lbl_fact_format.config(text=f"Format: {fmt}")
                self.lbl_fact_dims.config(text=f"Dimensions: {w} x {h} px")
                self.lbl_fact_size.config(text=f"File Size: {size_bytes:,} bytes")

                thumb_img = img.copy()
                thumb_img.thumbnail((230, 210), Image.Resampling.LANCZOS)
                self.current_thumbnail = ImageTk.PhotoImage(thumb_img)

                self.thumb_canvas.delete("all")
                cx = 120
                cy = 110
                self.thumb_canvas.create_image(cx, cy, image=self.current_thumbnail, anchor="center")

        except Exception:
            self.thumb_canvas.delete("all")
            self.thumb_canvas.create_text(120, 110, text="Preview Unavailable", fill=ACCENT_RED, font=("Helvetica", 10))

    def _populate_metadata_tab(self, data: Dict[str, Any]):
        dt = data.get("date_time", {})
        self.lbl_dt_taken.config(text=f"• Date/Time Taken: {dt.get('Date & Time Taken', 'Not available')}")
        self.lbl_dt_offset.config(text=f"• Timezone Offset: {dt.get('Timezone Offset', 'Not available')}")
        self.lbl_dt_modified.config(text=f"• Date Modified: {dt.get('Date & Time Modified', 'Not available')}")
        self.lbl_dt_gps.config(text=f"• GPS UTC Timestamp: {dt.get('GPS UTC Timestamp', 'Not available')}")

        dev = data.get("device_info", {})
        self.lbl_dev_make.config(text=f"• Camera Make: {dev.get('Camera Make', 'Not available')}")
        self.lbl_dev_model.config(text=f"• Camera Model: {dev.get('Camera Model', 'Not available')}")
        self.lbl_dev_software.config(text=f"• OS / Software: {dev.get('Software / Firmware', 'Not available')}")
        self.lbl_dev_lens.config(text=f"• Lens Model: {dev.get('Lens Model', 'Not available')}")
        self.lbl_dev_host.config(text=f"• Host Computer: {dev.get('Host Computer', 'Not available')}")
        self.lbl_dev_owner.config(text=f"• Artist / Owner: {dev.get('Artist / Author', dev.get('Camera Owner', 'Not available'))}")

        geo = data.get("geolocation", {})
        if geo and ("decimal_coordinates" in geo or "latitude_dd" in geo):
            self.lbl_geo_dms.config(text=f"• DMS Coordinates: {geo.get('dms_coordinates', 'N/A')}")
            self.lbl_geo_dec.config(text=f"• Decimal Coordinates: {geo.get('decimal_coordinates', 'N/A')}")
            self.lbl_geo_alt.config(text=f"• Altitude: {geo.get('altitude', 'N/A')}")

            self.google_maps_url = geo.get("google_maps_url")
            self.osm_url = geo.get("openstreetmap_url")

            self.btn_gmaps.config(state=tk.NORMAL if self.google_maps_url else tk.DISABLED)
            self.btn_osm.config(state=tk.NORMAL if self.osm_url else tk.DISABLED)
        else:
            self.lbl_geo_dms.config(text="• DMS Coordinates: No GPS Metadata Found")
            self.lbl_geo_dec.config(text="• Decimal Coordinates: -")
            self.lbl_geo_alt.config(text="• Altitude: -")
            self.google_maps_url = None
            self.osm_url = None
            self.btn_gmaps.config(state=tk.DISABLED)
            self.btn_osm.config(state=tk.DISABLED)

    def _populate_stego_tab(self, found_keys: List[Tuple[str, str, str]]):
        self.txt_keys.delete("1.0", tk.END)
        if found_keys:
            self.extracted_keys_raw = "\n\n".join(content for _, _, content in found_keys)
            types_summary = ", ".join(set(category for category, _, _ in found_keys))
            self.lbl_stego_status.config(
                text=f"✅ Detected {len(found_keys)} Key(s) ({types_summary})",
                fg=ACCENT_GREEN,
            )
            self.txt_keys.insert(tk.END, self.extracted_keys_raw)
        else:
            self.extracted_keys_raw = ""
            self.lbl_stego_status.config(
                text="❌ No Cryptographic Keys Detected",
                fg=TEXT_MUTED,
            )
            self.txt_keys.insert(tk.END, "[-] No PGP, SSH, or PEM cryptographic keys detected in image.")

    def open_google_maps(self):
        if self.google_maps_url:
            webbrowser.open(self.google_maps_url)

    def open_osm(self):
        if self.osm_url:
            webbrowser.open(self.osm_url)

    def copy_key_content(self):
        if self.extracted_keys_raw:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.extracted_keys_raw)
            messagebox.showinfo("Copied", "Extracted cryptographic key content copied to clipboard!")
        else:
            messagebox.showinfo("Nothing to Copy", "No keys were detected in this image.")

    def save_key_file(self):
        if not self.extracted_keys_raw:
            messagebox.showinfo("Nothing to Save", "No cryptographic key content to save.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("PGP Armor File", "*.asc"), ("SSH Key", "*.pub *.key"), ("All Files", "*.*")],
            title="Save Extracted Cryptographic Key",
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.extracted_keys_raw + "\n")
                messagebox.showinfo("Saved", f"Key content saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def copy_full_report(self):
        report_text = self.txt_report.get("1.0", tk.END).strip()
        if report_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(report_text)
            messagebox.showinfo("Copied", "Full analysis report copied to clipboard!")

    def export_report(self):
        report_text = self.txt_report.get("1.0", tk.END).strip()
        if not report_text:
            messagebox.showinfo("Nothing to Export", "No report content generated yet.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
            title="Export Analysis Report",
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(report_text + "\n")
                messagebox.showinfo("Saved", f"Report saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")


def launch_gui():
    """Launches the Tkinter Graphical User Interface."""
    root = tk.Tk()
    app = ImageInspectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
