"""
AUTO FILE ORGANIZER v2.0 - Pure Python Desktop Application
Features: Recycle Bin, Progress Bar, Folder Size, Duplicate Finder
"""
import os
import sys
import shutil
import pathlib
import time
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from threading import Thread
from send2trash import send2trash

# ==================== CORE LOGIC ====================

I18N = {
    'en': {
        'title': "NexOrganize v2.0",
        'path': "Path:",
        'explorer': "File Explorer",
        'properties': "Properties",
        'name': "Name",
        'size': "Size",
        'importance': "Importance",
        'date_mod': "Date Modified",
        'btn_browse': "Browse",
        'btn_analyze': "Analyze",
        'btn_organize': "Organize",
        'btn_recycle': "Recycle",
        'btn_delete': "Delete",
        'btn_duplicates': "Find Duplicates",
        'btn_lang': "Lang: EN",
        'btn_theme': "Mode: Dark",
        'status_ready': "Ready.",
        'status_scanning': "Scanning all subfolders...",
        'status_finished': "Scan Finished | {count} files | Total: {size}",
        'info_select': "Select an item to view properties...",
        'importance_high': "High",
        'importance_medium': "Medium",
        'importance_low': "Low",
        'advice_keep': "High priority. Keep it.",
        'advice_delete': "Optional. Delete if not needed.",
        'confirm_organize': "Organize all files in:\n{path}?",
        'success_organize': "Moved {count} files and cleaned up empty folders.",
        'warning_no_select': "No files selected.",
        'confirm_delete': "Are you sure you want to {action} {count} files?",
        'prop_dir': "DIRECTORY",
        'prop_file': "FILE",
        'prop_capacity': "CAPACITY",
        'prop_total_files': "Total Files",
        'prop_subfolders': "Sub-folders",
        'prop_created': "CREATED",
        'prop_modified': "MODIFIED",
        'prop_importance': "IMPORTANCE",
        'prop_advice': "ADVICE",
        'dup_title': "Find Duplicate Files",
        'dup_found': "Found {count} groups with duplicate names",
        'dup_base': "Base Name",
        'dup_file': "Filename",
        'dup_path': "Path",
        'dup_btn_move': "Organize to Category folders",
        'dup_btn_recycle': "Recycle (Restoreable)",
        'dup_btn_delete': "Delete (Permanent)",
        'dup_btn_close': "Close"
    },
    'vi': {
        'title': "NexOrganize v2.0",
        'path': "Đường dẫn:",
        'explorer': "Trình quản lý File",
        'properties': "Thông tin Chi tiết",
        'name': "Tên",
        'size': "Dung lượng",
        'importance': "Độ quan trọng",
        'date_mod': "Ngày thay đổi",
        'btn_browse': "Chọn",
        'btn_analyze': "Phân tích",
        'btn_organize': "Dọn dẹp",
        'btn_recycle': "Thùng rác",
        'btn_delete': "Xóa bỏ",
        'btn_duplicates': "Tìm Duplicate",
        'btn_lang': "Ngôn ngữ: VI",
        'btn_theme': "Giao diện: Tối",
        'status_ready': "Sẵn sàng.",
        'status_scanning': "Đang quét toàn bộ thư mục con...",
        'status_finished': "Đã quét xong | {count} file | Tổng: {size}",
        'info_select': "Chọn một mục để xem chi tiết...",
        'importance_high': "Cao",
        'importance_medium': "Trung bình",
        'importance_low': "Thấp",
        'advice_keep': "Ưu tiên cao. Nên giữ lại.",
        'advice_delete': "Có thể xóa nếu không cần thiết.",
        'confirm_organize': "Bắt đầu dọn dẹp các file trong:\n{path}?",
        'success_organize': "Đã di chuyển {count} file và dọn dẹp thư mục rỗng.",
        'warning_no_select': "Chưa chọn file nào.",
        'confirm_delete': "Bạn có chắc muốn {action} {count} file?",
        'prop_dir': "THƯ MỤC",
        'prop_file': "TẬP TIN",
        'prop_capacity': "SỨC CHỨA",
        'prop_total_files': "Tổng số file",
        'prop_subfolders': "Thư mục con",
        'prop_created': "NGÀY TẠO",
        'prop_modified': "NGÀY SỬA",
        'prop_importance': "ĐỘ QUAN TRỌNG",
        'prop_advice': "LỜI KHUYÊN",
        'dup_title': "Tìm kiếm File Trùng lặp",
        'dup_found': "Tìm thấy {count} nhóm file trùng tên/hậu tố",
        'dup_base': "Tên gốc",
        'dup_file': "Tên file",
        'dup_path': "Đường dẫn",
        'dup_btn_move': "Gom vào thư mục Thể loại",
        'dup_btn_recycle': "Bỏ vào Thùng rác",
        'dup_btn_delete': "Xóa Vĩnh viễn",
        'dup_btn_close': "Đóng"
    }
}

THEMES = {
    'dark': {
        'bg_main': "#1a1a2e",
        'bg_sec': "#16213e",
        'bg_header': "#0f3460",
        'fg_main': "#e0e0e0",
        'fg_accent': "#00f2ff",
        'btn_bg': "#0f3460",
        'btn_active': "#16213e"
    },
    'light': {
        'bg_main': "#f0f2f5",
        'bg_sec': "#ffffff",
        'bg_header': "#e1e1e1",
        'fg_main': "#333333",
        'fg_accent': "#0056b3",
        'btn_bg': "#e1e1e1",
        'btn_active': "#d1d1d1"
    }
}

EXTENSION_MAP = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
    'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.pptx', '.csv', '.md'],
    'Videos': ['.mp4', '.mov', '.avi', '.mkv', '.wmv'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Apps': ['.exe', '.msi', '.apk']
}

def get_importance(file_path):
    """Analyze file importance based on heuristics."""
    try:
        stat = os.stat(file_path)
        ext = pathlib.Path(file_path).suffix.lower()
        size_mb = stat.st_size / (1024 * 1024)
        age_days = (time.time() - stat.st_mtime) / (24 * 3600)
        
        if age_days < 7:
            return "High", "Recently updated this week."
        if ext in ['.config', '.ini', '.json', '.dll', '.exe']:
            return "High", f"System/Config file ({ext}). Be careful!"
        if size_mb > 500:
            return "Medium", "Large file (>500MB)."
        if ext in ['.log', '.tmp', '.bak', '.cache']:
            return "Low", "Temporary/Cache file, safe to delete."
        if age_days > 365:
            return "Low", "Old file (over 1 year)."
        return "Medium", "Regular data file."
    except Exception:
        return "N/A", "Unable to analyze."

def format_size(bytes_size):
    """Format bytes to human readable."""
    if bytes_size is None:
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

def format_date(timestamp):
    """Format timestamp to readable date."""
    return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')

def get_folder_size(path):
    """Calculate total size of a folder."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_folder_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total



# ==================== PROGRESS DIALOG ====================

class ProgressDialog(tk.Toplevel):
    def __init__(self, parent, title, total):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x120")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")
        self.transient(parent)
        self.grab_set()
        
        self.total = total
        self.current = 0
        
        ttk.Label(self, text=title, font=("Segoe UI", 11, "bold")).pack(pady=(15, 5))
        
        self.progress = ttk.Progressbar(self, length=350, mode='determinate', maximum=total)
        self.progress.pack(pady=10)
        
        self.status_var = tk.StringVar(value="Preparing...")
        ttk.Label(self, textvariable=self.status_var, font=("Consolas", 9)).pack()
        
        self.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing
    
    def update_progress(self, current, status_text):
        self.current = current
        self.progress['value'] = current
        self.status_var.set(f"{status_text} ({current}/{self.total})")
        self.update()
    
    def complete(self):
        self.destroy()

# ==================== DUPLICATE FINDER DIALOG ====================

import re

def get_base_name(filename):
    """Extract base name without suffixes like (1), - Copy, _copy. E.g., 'photo - Copy (1).jpg' -> 'photo'"""
    name, ext = os.path.splitext(filename)
    # 1. Remove (1), (2) suffixes
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    # 2. Remove " - Copy", " _copy", etc.
    name = re.sub(r'[\s_-]+[Cc]opy\s*$', '', name)
    # 3. Clean up trailing spaces or dashes
    name = name.strip().rstrip('-_ ')
    return name, ext

class DuplicateFinderDialog(tk.Toplevel):
    def __init__(self, parent, all_files, parent_app=None):
        super().__init__(parent)
        self.parent_app = parent_app
        self.lang = parent_app.lang if parent_app else 'en'
        self.theme = parent_app.theme if parent_app else 'dark'
        
        t = I18N[self.lang]
        colors = THEMES[self.theme]
        
        self.title(t['dup_title'])
        self.geometry("800x500")
        self.configure(bg=colors['bg_main'])
        self.transient(parent)
        self.grab_set()
        
        # Group by base name
        self.name_groups = {}
        for fp in all_files:
            filename = os.path.basename(fp)
            base, ext = get_base_name(filename)
            key = (base + ext).lower()
            if key not in self.name_groups:
                self.name_groups[key] = []
            self.name_groups[key].append(fp)
        
        # Filter only groups with duplicates
        self.name_groups = {k: v for k, v in self.name_groups.items() if len(v) > 1}
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header, text=t['dup_found'].format(count=len(self.name_groups)), 
                  font=("Segoe UI", 12, "bold"), foreground=colors['fg_accent']).pack(side=tk.LEFT)
        
        # Treeview
        columns = ("base_name", "file", "size", "path")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15, selectmode="extended")
        self.tree.heading("base_name", text=t['dup_base'])
        self.tree.heading("file", text=t['dup_file'])
        self.tree.heading("size", text=I18N[self.lang]['size'])
        self.tree.heading("path", text=t['dup_path'])
        self.tree.column("base_name", width=120)
        self.tree.column("file", width=200)
        self.tree.column("size", width=80)
        self.tree.column("path", width=380)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for base_key, files in sorted(self.name_groups.items()):
            for fp in files:
                size = format_size(os.path.getsize(fp) if os.path.exists(fp) else 0)
                self.tree.insert("", tk.END, values=(
                    os.path.basename(files[0]),
                    os.path.basename(fp),
                    size,
                    fp
                ), tags=(fp,))
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text=t['dup_btn_move'], 
                   command=self._move_to_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=t['dup_btn_recycle'], 
                   command=lambda: self._delete_selected(False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=t['dup_btn_delete'], 
                   command=lambda: self._delete_selected(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=t['dup_btn_close'], command=self.destroy).pack(side=tk.RIGHT)
    
    def _get_selected_files(self):
        """Get selected files from the tree."""
        files = []
        for item in self.tree.selection():
            tags = self.tree.item(item, "tags")
            if tags:
                files.append(tags[0])
        return files
    
    def _move_to_folder(self):
        """Move selected duplicates to folders with base name inside category folders."""
        t = I18N[self.lang]
        files = self._get_selected_files()
        if not files:
            messagebox.showwarning(t['dup_title'], t['warning_no_select'])
            return
        
        # Group files by base name
        groups = {}
        for fp in files:
            filename = os.path.basename(fp)
            base, ext = get_base_name(filename)
            key = (base + ext).lower()
            if key not in groups:
                groups[key] = []
            groups[key].append(fp)
            
        progress = ProgressDialog(self, t['btn_organize'], len(files))
        Thread(target=self._run_move_to_folder, args=(groups, progress), daemon=True).start()

    def _run_move_to_folder(self, groups, progress):
        """Background worker for moving duplicates."""
        parent_dir = os.path.dirname(list(groups.values())[0][0])
        moved = 0
        
        for key, file_list in groups.items():
            fp_sample = file_list[0]
            ext_raw = pathlib.Path(fp_sample).suffix.lower()
            target_cat = "Others"
            for cat, exts in EXTENSION_MAP.items():
                if ext_raw in exts:
                    target_cat = cat
                    break
            
            base, ext = get_base_name(os.path.basename(fp_sample))
            final_dir = os.path.join(parent_dir, target_cat, base)
            os.makedirs(final_dir, exist_ok=True)
            
            for fp in file_list:
                self.after(0, lambda f=fp, m=moved: progress.update_progress(m + 1, os.path.basename(f)[:30]))
                dest = os.path.join(final_dir, os.path.basename(fp))
                if os.path.exists(dest):
                    name, ext_part = os.path.splitext(os.path.basename(fp))
                    counter = 1
                    while os.path.exists(dest):
                        dest = os.path.join(final_dir, f"{name}_{counter}{ext_part}")
                        counter += 1
                try:
                    shutil.move(fp, dest)
                    moved += 1
                except Exception:
                    pass
        
        # Finalize
        if self.parent_app and hasattr(self.parent_app, "_cleanup_empty_folders"):
            self.parent_app._cleanup_empty_folders(parent_dir)
            
        self.after(0, lambda: self._on_move_complete(progress, moved))

    def _on_move_complete(self, progress, moved):
        """Close dialog and show success after background move."""
        t = I18N[self.lang]
        progress.complete()
        messagebox.showinfo(t['dup_title'], t['success_organize'].format(count=moved))
        self.destroy()
    
    def _delete_selected(self, permanent):
        t = I18N[self.lang]
        files = self._get_selected_files()
        if not files:
            messagebox.showwarning(t['dup_title'], t['warning_no_select'])
            return
        
        action = t['btn_delete'].upper() if permanent else t['btn_recycle'].lower()
        if not messagebox.askyesno(t['dup_title'], t['confirm_delete'].format(action=action, count=len(files))):
            return
        
        deleted = 0
        for f in files:
            try:
                if permanent:
                    os.remove(f)
                else:
                    send2trash(f)
                deleted += 1
            except Exception:
                pass
        
        messagebox.showinfo("Hoàn tất", f"Đã xử lý {deleted} file.")
        self.destroy()

# ==================== MAIN APPLICATION ====================

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.lang = 'en'
        self.theme = 'dark'
        
        self.root.title(I18N[self.lang]['title'])
        self.root.geometry("1200x750")
        
        self.current_path = os.path.expanduser("~")
        self.scanned_files = []
        self.all_items = []  # Store all items including folders
        
        self.setup_styles()
        self.create_widgets()
        self.update_ui_text()
        self.browse_path(self.current_path)
    
    def setup_styles(self):
        """Configure ttk styles based on current theme."""
        style = ttk.Style()
        style.theme_use('clam')
        colors = THEMES[self.theme]
        
        style.configure(".", background=colors['bg_main'], foreground=colors['fg_main'])
        style.configure("TFrame", background=colors['bg_main'])
        style.configure("TLabel", background=colors['bg_main'], foreground=colors['fg_main'], font=("Segoe UI", 10))
        # Custom styles for highlighting
        style.configure("Header.TLabel", background=colors['bg_main'], foreground=colors['fg_accent'], font=("Segoe UI", 12, "bold"))
        style.configure("Path.TLabel", background=colors['bg_main'], foreground=colors['fg_main'], font=("Segoe UI", 11, "bold"))
        
        style.configure("TButton", background=colors['btn_bg'], foreground=colors['fg_main'], font=("Segoe UI", 10, "bold"), padding=8)
        style.map("TButton", background=[("active", colors['btn_active'])])
        
        # Tool buttons (smaller)
        style.configure("Tool.TButton", padding=4)
        
        style.configure("Treeview", background=colors['bg_sec'], foreground=colors['fg_main'], fieldbackground=colors['bg_sec'], font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=colors['bg_header'], foreground=colors['fg_accent'], font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", colors['bg_header'])])
        
        style.configure("TProgressbar", troughcolor=colors['bg_sec'], background=colors['fg_accent'])
        
        self.root.configure(bg=colors['bg_main'])
    
    def create_widgets(self):
        """Build the main UI."""
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.lbl_path = ttk.Label(top_frame, text="Path:", style="Path.TLabel")
        self.lbl_path.pack(side=tk.LEFT, padx=(0, 5))
        
        self.path_var = tk.StringVar(value=self.current_path)
        self.path_entry = ttk.Entry(top_frame, textvariable=self.path_var, width=60, font=("Consolas", 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.path_entry.bind("<Return>", lambda e: self.browse_path(self.path_var.get()))
        
        self.btn_browse = ttk.Button(top_frame, text="📂 Browse", command=self.pick_folder)
        self.btn_browse.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="⬆️", command=self.go_up).pack(side=tk.LEFT)

        # Toolbar for Language and Theme
        toolbar = ttk.Frame(top_frame)
        toolbar.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.btn_lang = ttk.Button(toolbar, text="Lang: EN", width=12, style="Tool.TButton", command=self.toggle_lang)
        self.btn_lang.pack(side=tk.LEFT, padx=2)
        
        self.btn_theme = ttk.Button(toolbar, text="Mode: Dark", width=12, style="Tool.TButton", command=self.toggle_theme)
        self.btn_theme.pack(side=tk.LEFT, padx=2)
        
        # Main content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left pane: File browser
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.lbl_explorer = ttk.Label(left_frame, text="File Explorer", style="Header.TLabel")
        self.lbl_explorer.pack(anchor=tk.W)
        
        columns = ("name", "size", "importance", "date")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=22, selectmode="extended")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
        
        # Right pane: Info panel
        right_frame = ttk.Frame(main_frame, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        self.lbl_properties = ttk.Label(right_frame, text="Properties", style="Header.TLabel")
        self.lbl_properties.pack(anchor=tk.W, pady=(0, 10))
        
        self.info_text = tk.Text(right_frame, wrap=tk.WORD, height=18, font=("Consolas", 10), relief=tk.FLAT)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.apply_theme_to_widgets() # Initial theme for Text widget
        
        # Bottom bar: Action buttons
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.btn_analyze = ttk.Button(bottom_frame, text="Analyze", command=self.scan_folder)
        self.btn_analyze.pack(side=tk.LEFT, padx=3)
        self.btn_organize = ttk.Button(bottom_frame, text="Organize", command=self.organize_files)
        self.btn_organize.pack(side=tk.LEFT, padx=3)
        self.btn_recycle = ttk.Button(bottom_frame, text="Recycle", command=lambda: self.delete_selected(permanent=False))
        self.btn_recycle.pack(side=tk.LEFT, padx=3)
        self.btn_delete = ttk.Button(bottom_frame, text="Delete", command=lambda: self.delete_selected(permanent=True))
        self.btn_delete.pack(side=tk.LEFT, padx=3)
        self.btn_duplicates = ttk.Button(bottom_frame, text="Find Duplicates", command=self.find_duplicates)
        self.btn_duplicates.pack(side=tk.LEFT, padx=3)
        
        self.status_var = tk.StringVar()
        ttk.Label(bottom_frame, textvariable=self.status_var, font=("Consolas", 9)).pack(side=tk.RIGHT)

    def update_ui_text(self):
        """Update all UI text based on current language."""
        t = I18N[self.lang]
        self.root.title(t['title'])
        self.lbl_path.config(text=t['path'])
        self.btn_browse.config(text=f"{t['btn_browse']}")
        self.lbl_explorer.config(text=f"{t['explorer']}")
        self.lbl_properties.config(text=f"{t['properties']}")
        
        # Tree columns
        self.tree.heading("name", text=t['name'])
        self.tree.heading("size", text=t['size'])
        self.tree.heading("importance", text=t['importance'])
        self.tree.heading("date", text=t['date_mod'])
        
        # Buttons
        self.btn_analyze.config(text=f"{t['btn_analyze']}")
        self.btn_organize.config(text=f"{t['btn_organize']}")
        self.btn_recycle.config(text=f"{t['btn_recycle']}")
        self.btn_delete.config(text=f"{t['btn_delete']}")
        self.btn_duplicates.config(text=f"{t['btn_duplicates']}")
        self.btn_lang.config(text=t['btn_lang'])
        self.btn_theme.config(text=t['btn_theme'])
        
        if not self.status_var.get() or "Ready" in self.status_var.get() or "Sẵn sàng" in self.status_var.get():
            self.status_var.set(t['status_ready'])

    def apply_theme_to_widgets(self):
        """Update non-ttk widgets to match theme."""
        colors = THEMES[self.theme]
        self.info_text.config(bg=colors['bg_sec'], fg=colors['fg_main'])

    def toggle_lang(self):
        self.lang = 'vi' if self.lang == 'en' else 'en'
        self.update_ui_text()
        self.on_item_select(None) # Refresh info panel text if item selected

    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.setup_styles()
        self.apply_theme_to_widgets()
        self.update_ui_text()
    
    def pick_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_path)
        if folder:
            self.browse_path(folder)
    
    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent:
            self.browse_path(parent)
    
    def browse_path(self, path):
        """List immediate files in UI, then scan recursively in background."""
        try:
            path = os.path.abspath(path)
            if not os.path.isdir(path):
                messagebox.showerror("Lỗi", "Đường dẫn không hợp lệ.")
                return
            
            self.current_path = path
            self.path_var.set(path)
            self.tree.delete(*self.tree.get_children())
            
            self.all_items = []
            self.scanned_files = [] 
            
            # 1. UI Tree: Show immediate entries first (Fast)
            entries = list(os.scandir(path))
            for entry in entries:
                try:
                    if entry.is_dir():
                        # Initially show folder without size to avoid blocking
                        item_id = self.tree.insert("", tk.END, values=(f"📁 {entry.name}", "Đang tính...", "", ""), tags=("dir", entry.path))
                        self.all_items.append({"id": item_id, "path": entry.path, "is_dir": True, "size": 0})
                    else:
                        stat = entry.stat()
                        imp, _ = get_importance(entry.path)
                        item_id = self.tree.insert("", tk.END, values=(f"📄 {entry.name}", format_size(stat.st_size), imp, format_date(stat.st_mtime)), tags=("file", entry.path))
                        self.all_items.append({"id": item_id, "path": entry.path, "is_dir": False, "size": stat.st_size})
                except Exception:
                    pass
            
            # 2. Background Scan: Start thread for folder sizes and recursive search
            self.status_var.set("🔍 Đang quét toàn bộ thư mục con...")
            Thread(target=self._background_scan, args=(path,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _background_scan(self, path):
        """Heavy lifting inside a thread."""
        temp_scanned = []
        folder_size_map = {}
        
        # Recursive Scan for scanned_files list
        for root, dirs, files in os.walk(path):
            for f in files:
                temp_scanned.append(os.path.join(root, f))
        
        # Calculate sizes for visible folders
        for item in self.all_items:
            if item["is_dir"]:
                folder_size_map[item["id"]] = get_folder_size(item["path"])

        # Update UI safely
        self.root.after(0, lambda: self._scan_complete(temp_scanned, folder_size_map))

    def _scan_complete(self, scanned_files, folder_sizes):
        """Update UI with final scan results."""
        self.scanned_files = scanned_files
        
        # Update folder sizes in tree
        for item_id, size in folder_sizes.items():
            if self.tree.exists(item_id):
                current_values = list(self.tree.item(item_id, "values"))
                current_values[1] = format_size(size)
                self.tree.item(item_id, values=tuple(current_values))
        
        total_size = sum(os.path.getsize(f) for f in scanned_files if os.path.exists(f))
        self.status_var.set(f"📂 Quét xong | {len(scanned_files)} file | Tổng: {format_size(total_size)}")
        self.scan_folder()
    
    def on_item_double_click(self, event):
        item = self.tree.selection()
        if item:
            tags = self.tree.item(item[0], "tags")
            if tags and len(tags) > 1:
                full_path = tags[1]
                if os.path.isdir(full_path):
                    self.browse_path(full_path)
    
    def on_item_select(self, event):
        item_id = self.tree.selection()
        if not item_id:
            return
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        t = I18N[self.lang]
        
        try:
            target = self.tree.item(item_id[0], 'tags')[1]
            stat = os.stat(target)
            is_dir = os.path.isdir(target)
            
            if is_dir:
                folder_size = get_folder_size(target)
                file_count = sum(1 for root, dirs, files in os.walk(target) for _ in files)
                dir_count = sum(1 for root, dirs, files in os.walk(target) for _ in dirs)
                
                info = f"""[{t['prop_dir']}]
{os.path.basename(target)}

{t['prop_capacity']}:
{format_size(folder_size)}

{t['prop_total_files']}: {file_count}
{t['prop_subfolders']}: {dir_count}

{t['prop_created']}:
{format_date(stat.st_ctime)}

{t['prop_modified']}:
{format_date(stat.st_mtime)}
"""
            else:
                imp, reason = get_importance(target)
                # Translate importance label
                imp_label = t[f'importance_{imp.lower()}'] if f'importance_{imp.lower()}' in t else imp
                advice = t['advice_keep'] if imp == "High" else t['advice_delete']
                
                info = f"""[{t['prop_file']}]
{os.path.basename(target)}

{t['size'].upper()}:
{format_size(stat.st_size)}

{t['prop_created']}:
{format_date(stat.st_ctime)}

{t['prop_modified']}:
{format_date(stat.st_mtime)}

{t['prop_importance']}: {imp_label}
{reason}

{t['prop_advice']}:
{advice}
"""
            
            self.info_text.insert(tk.END, info)
        except Exception:
            self.info_text.insert(tk.END, t['info_select'])
            
        self.info_text.config(state=tk.DISABLED)
    
    def scan_folder(self):
        categories = {cat: 0 for cat in EXTENSION_MAP.keys()}
        categories["Khác"] = 0
        
        for fp in self.scanned_files:
            ext = pathlib.Path(fp).suffix.lower()
            found = False
            for cat, exts in EXTENSION_MAP.items():
                if ext in exts:
                    categories[cat] += 1
                    found = True
                    break
            if not found:
                categories["Khác"] += 1
        
        report = "📊 KẾT QUẢ QUÉT\n" + "="*30 + "\n"
        for cat, count in categories.items():
            report += f"  • {cat}: {count} file\n"
        report += f"\n📁 Tổng cộng: {len(self.scanned_files)} file"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, report)
        self.info_text.config(state=tk.DISABLED)
    
    def organize_files(self):
        """Smart organize: starts a background thread."""
        t = I18N[self.lang]
        if not messagebox.askyesno(t['title'], t['confirm_organize'].format(path=self.current_path)):
            return
        
        # Group by base name to detect duplicates
        name_groups = {}
        for fp in self.scanned_files:
            base, ext = get_base_name(os.path.basename(fp))
            key = (base + ext).lower()
            if key not in name_groups:
                name_groups[key] = []
            name_groups[key].append(fp)
            
        progress = ProgressDialog(self.root, t['btn_organize'], len(self.scanned_files))
        Thread(target=self._run_organize, args=(name_groups, progress), daemon=True).start()

    def _run_organize(self, name_groups, progress):
        """Background worker for organizing files."""
        moved = 0
        total_files = sum(len(files) for files in name_groups.values())
        
        for key, file_list in name_groups.items():
            fp_sample = file_list[0]
            ext_raw = pathlib.Path(fp_sample).suffix.lower()
            target_cat = "Others"
            for cat, exts in EXTENSION_MAP.items():
                if ext_raw in exts:
                    target_cat = cat
                    break
            
            cat_dir = os.path.join(self.current_path, target_cat)
            
            if len(file_list) > 1:
                base, ext = get_base_name(os.path.basename(fp_sample))
                target_dir = os.path.join(cat_dir, base)
            else:
                target_dir = cat_dir
            
            os.makedirs(target_dir, exist_ok=True)
            
            for fp in file_list:
                # Update progress safely
                self.root.after(0, lambda f=fp, m=moved: progress.update_progress(m + 1, os.path.basename(f)[:30]))
                
                destination = os.path.join(target_dir, os.path.basename(fp))
                if os.path.exists(destination):
                    b, e = os.path.splitext(os.path.basename(fp))
                    counter = 1
                    while os.path.exists(destination):
                        destination = os.path.join(target_dir, f"{b}_{counter}{e}")
                        counter += 1
                
                try:
                    shutil.move(fp, destination)
                    moved += 1
                except Exception:
                    pass
        
        # Cleanup and Refresh UI
        self._cleanup_empty_folders(self.current_path)
        self.root.after(0, lambda: self._on_organize_complete(progress, moved))

    def _on_organize_complete(self, progress, moved):
        """Finalize UI after organization."""
        t = I18N[self.lang]
        progress.complete()
        messagebox.showinfo(t['title'], t['success_organize'].format(count=moved))
        self.browse_path(self.current_path)

    def _cleanup_empty_folders(self, path):
        """Recursively remove empty folders."""
        for root, dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                full_p = os.path.join(root, name)
                # Don't delete our main category folders even if empty
                if name in EXTENSION_MAP.keys() or name == "Others":
                    continue
                try:
                    if not os.listdir(full_p):
                        os.rmdir(full_p)
                except Exception:
                    pass
    
    def delete_selected(self, permanent=False):
        """Delete selected items. If permanent=False, move to Recycle Bin."""
        t = I18N[self.lang]
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t['title'], t['warning_no_select'])
            return
        
        items_to_delete = []
        for item in selected:
            tags = self.tree.item(item, "tags")
            if tags and len(tags) > 1:
                items_to_delete.append(tags[1])
        
        if not items_to_delete:
            return
        
        action_label = t['btn_delete'].upper() if permanent else t['btn_recycle'].lower()
        if not messagebox.askyesno(t['title'], t['confirm_delete'].format(action=action_label, count=len(items_to_delete))):
            return
        
        progress_title = t['btn_delete'] if permanent else t['btn_recycle']
        progress = ProgressDialog(self.root, progress_title, len(items_to_delete))
        Thread(target=self._run_delete, args=(items_to_delete, permanent, progress), daemon=True).start()

    def _run_delete(self, items, permanent, progress):
        """Background worker for deleting files."""
        deleted = 0
        errors = []
        
        for i, path in enumerate(items):
            self.root.after(0, lambda p=path, idx=i: progress.update_progress(idx + 1, os.path.basename(p)[:30]))
            try:
                if permanent:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                else:
                    send2trash(path)
                deleted += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {str(e)}")
        
        self.root.after(0, lambda: self._on_delete_complete(progress, deleted, len(items), errors))

    def _on_delete_complete(self, progress, deleted, total, errors):
        """Finalize UI after deletion."""
        t = I18N[self.lang]
        progress.complete()
        
        # Simple translation based on language
        success_title = "Hoàn tất" if self.lang == 'vi' else "Finished"
        result_msg = f"Đã xử lý {deleted}/{total} mục." if self.lang == 'vi' else f"Processed {deleted}/{total} items."
        
        if errors:
            err_title = "\n\nLỗi:" if self.lang == 'vi' else "\n\nErrors:"
            result_msg += f"{err_title}\n" + "\n".join(errors[:3])
        
        messagebox.showinfo(success_title, result_msg)
        self.browse_path(self.current_path)
    
    def find_duplicates(self):
        """Find duplicate files based on name grouping."""
        if len(self.scanned_files) < 2:
            messagebox.showinfo("Thông báo", "Không đủ file để tìm trùng lặp.")
            return
        
        DuplicateFinderDialog(self.root, self.scanned_files, parent_app=self)

# ==================== MAIN ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
