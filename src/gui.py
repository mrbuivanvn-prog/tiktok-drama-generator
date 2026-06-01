"""
GUI module for TikTok Drama Generator
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import subprocess
import sys
from typing import Optional
from src.utils import logger
from src.generator import IdeaGenerator, fetch_all_trends
from src.video_creator import VideoCreator


class TikTokDramaGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTok Drama Generator - Quét Tin Hot & Tạo Video")
        self.root.geometry("1000x750")
        self.root.configure(bg='#1a1a2e')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#1a1a2e')
        self.style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'), foreground='#ff6b6b')
        self.style.configure('Subheader.TLabel', font=('Arial', 12), foreground='#4ecdc4')

        self.config = load_config()
        self.current_trends = []
        self.current_ideas = []
        self.video_paths = []

        self._configure_icon()
        self._build_ui()
        self._load_today_data()

    def _configure_icon(self):
        icon_path = Path('assets/icon.png')
        if icon_path.exists():
            try:
                img = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, img)
            except Exception:
                pass

    def _build_ui(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(header_frame, text="🎬 TikTok Drama Generator", style='Header.TLabel').pack()
        ttk.Label(header_frame, text="Quét tin hot từ mạng xã hội & Tạo video TikTok hàng ngày", style='Subheader.TLabel').pack(pady=2)

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, width=280)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)

        ttk.Label(left_panel, text="📋 Điều khiển", font=('Arial', 12, 'bold'), foreground='#4ecdc4').pack(anchor='w', pady=(0, 10))

        # Date selector
        date_frame = ttk.Frame(left_panel)
        date_frame.pack(fill='x', pady=5)
        ttk.Label(date_frame, text="📅 Ngày:").pack(anchor='w')
        self.date_var = tk.StringVar(value=get_today_string())
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
        date_entry.pack(fill='x', pady=2)

        # Social media sources
        ttk.Label(left_panel, text="🌐 Nguồn tin hot:", font=('Arial', 11, 'bold'), foreground='#4ecdc4').pack(anchor='w', pady=(15, 5))
        sources_frame = ttk.Frame(left_panel)
        sources_frame.pack(fill='x', pady=5)
        self.selected_sources = {
            'google_trends': tk.BooleanVar(value=False),
            'reddit': tk.BooleanVar(value=False),
            'twitter': tk.BooleanVar(value=False),
            'facebook': tk.BooleanVar(value=False),
            'rss': tk.BooleanVar(value=True),
            'web_scraping': tk.BooleanVar(value=True),
        }
        ttk.Checkbutton(sources_frame, text="Google Trends", variable=self.selected_sources['google_trends']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="Reddit", variable=self.selected_sources['reddit']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="X (Twitter)", variable=self.selected_sources['twitter']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="Facebook", variable=self.selected_sources['facebook']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="RSS báo Việt Nam", variable=self.selected_sources['rss']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="Web scraping", variable=self.selected_sources['web_scraping']).pack(anchor='w')

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill='x', pady=15)

        ttk.Button(btn_frame, text="🔥 Quét tin hot ngay", command=self._scan_trends).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="📝 Tạo kịch bản & Tóm tắt", command=self._generate_scripts).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="🎬 Tạo video từ tin hot", command=self._create_videos).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="📂 Mở thư mục video", command=self._open_video_folder).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="🔃 Reload dữ liệu", command=self._load_today_data).pack(fill='x', pady=3)

        # Status
        ttk.Label(left_panel, text="📊 Trạng thái", font=('Arial', 12, 'bold'), foreground='#4ecdc4').pack(anchor='w', pady=(20, 5))
        self.status_label = ttk.Label(left_panel, text="Sẵn sàng", foreground='#95e1d3')
        self.status_label.pack(anchor='w')

        self.progress = ttk.Progressbar(left_panel, mode='determinate', length=240)
        self.progress.pack(pady=10)

        # Right panel - Content
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill='both', expand=True)

        # Trends tab
        trends_tab = ttk.Frame(self.notebook)
        self.notebook.add(trends_tab, text='🔥 Tin Hot / Trends')

        ttk.Label(trends_tab, text="Danh sách tin hot vừa quét:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5, padx=5)
        trends_list_frame = ttk.Frame(trends_tab)
        trends_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(trends_list_frame)
        scrollbar.pack(side='right', fill='y')
        self.trends_listbox = tk.Listbox(trends_list_frame, yscrollcommand=scrollbar.set, bg='#16213e', fg='white',
                                         font=('Arial', 10), selectbackground='#0f3460', selectforeground='white',
                                         relief='flat', bd=0, highlightthickness=0, height=15)
        self.trends_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.trends_listbox.yview)

        # Scripts tab
        scripts_tab = ttk.Frame(self.notebook)
        self.notebook.add(scripts_tab, text='📝 Kịch bản & Tóm tắt')

        ttk.Label(scripts_tab, text="Kịch bản video được tóm tắt từ tin hot:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5, padx=5)
        scripts_list_frame = ttk.Frame(scripts_tab)
        scripts_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar2 = ttk.Scrollbar(scripts_list_frame)
        scrollbar2.pack(side='right', fill='y')
        self.scripts_listbox = tk.Listbox(scripts_list_frame, yscrollcommand=scrollbar2.set, bg='#16213e', fg='white',
                                          font=('Arial', 10), selectbackground='#0f3460', selectforeground='white',
                                          relief='flat', bd=0, highlightthickness=0, height=15)
        self.scripts_listbox.pack(fill='both', expand=True)
        scrollbar2.config(command=self.scripts_listbox.yview)

        # Videos tab
        videos_tab = ttk.Frame(self.notebook)
        self.notebook.add(videos_tab, text='🎥 Video TikTok')

        ttk.Label(videos_tab, text="Video đã tạo:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5, padx=5)
        videos_list_frame = ttk.Frame(videos_tab)
        videos_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar3 = ttk.Scrollbar(videos_list_frame)
        scrollbar3.pack(side='right', fill='y')
        self.videos_listbox = tk.Listbox(videos_list_frame, yscrollcommand=scrollbar3.set, bg='#16213e', fg='white',
                                         font=('Arial', 10), selectbackground='#0f3460', selectforeground='white',
                                         relief='flat', bd=0, highlightthickness=0, height=10)
        self.videos_listbox.pack(fill='both', expand=True)
        scrollbar3.config(command=self.videos_listbox.yview)

        preview_frame = ttk.Frame(videos_tab)
        preview_frame.pack(fill='x', pady=5)
        self.preview_label = ttk.Label(preview_frame, text="Chọn video để xem", foreground='#888')
        self.preview_label.pack()
        ttk.Button(preview_frame, text="▶️ Mở video", command=self._play_selected_video).pack(pady=5)

    def _load_today_data(self):
        date_str = self.date_var.get()
        # Load trends
        trends_path = Path(f"data/trends/trends_{date_str}.json")
        if trends_path.exists():
            import json
            with open(trends_path, 'r', encoding='utf-8') as f:
                trends_data = json.load(f)
            self.trends_listbox.delete(0, tk.END)
            self.current_trends = []
            for i, t in enumerate(trends_data, 1):
                topic = t.get('topic', 'N/A')
                source = t.get('source', '')
                self.trends_listbox.insert(tk.END, f"{i}. [{source}] {topic}")
                self.current_trends.append(t)
            self.status_label.config(text=f"✅ {len(trends_data)} tin hot")
        else:
            self.trends_listbox.delete(0, tk.END)
            self.trends_listbox.insert(tk.END, "Chưa có tin hot cho ngày này. Nhấn 'Quét tin hot ngay'")
            self.status_label.config(text="⚠️ Chưa có dữ liệu")

        # Load scripts
        ideas_path = Path(f"data/ideas/ideas_{date_str}.json")
        if ideas_path.exists():
            import json
            with open(ideas_path, 'r', encoding='utf-8') as f:
                ideas_data = json.load(f)
            self.scripts_listbox.delete(0, tk.END)
            self.current_ideas = []
            for i, idea in enumerate(ideas_data, 1):
                text = idea.get('idea', 'N/A')
                self.scripts_listbox.insert(tk.END, f"{i}. {text}")
                self.current_ideas.append(idea)

        # Load videos
        videos_path = Path(f"data/videos/videos_{date_str}.json")
        if videos_path.exists():
            import json
            with open(videos_path, 'r', encoding='utf-8') as f:
                videos_data = json.load(f)
            self.videos_listbox.delete(0, tk.END)
            self.video_paths = []
            for i, v in enumerate(videos_data, 1):
                path = v.get('path', '')
                idea = v.get('idea', 'Unknown')
                self.videos_listbox.insert(tk.END, f"{i}. {Path(path).name}")
                self.video_paths.append(path)

    def _scan_trends(self):
        self.status_label.config(text="🔥 Đang quét tin hot...")
        self.progress['value'] = 20
        self.root.update()

        try:
            selected = {name: var.get() for name, var in self.selected_sources.items()}
            active = [name for name, flag in selected.items() if flag]
            if not active:
                messagebox.showwarning("Cảnh báo", "Hãy chọn ít nhất 1 nguồn tin!")
                self.status_label.config(text="⚠️ Chưa chọn nguồn")
                return

            self.progress['value'] = 40
            self.root.update()

            trends = fetch_all_trends(self.config)
            if not trends:
                from src.utils import TrendItem
                fallbacks = [
                    "Bóng đá Việt Nam đang thi đấu thành công?",
                    "Học sinh lớp 10 chuẩn bị kỳ thi quan trọng",
                    "Giá xăng dầu biến động mạnh",
                    "Sao Việt gây sốt với phong cách mới",
                    "Xu hướng mạng xã hội hôm nay",
                ]
                trends = [TrendItem(topic=t, source="fallback", score=60) for t in fallbacks]

            self.progress['value'] = 70
            self.root.update()

            self.current_trends = [t if isinstance(t, dict) else t.to_dict() for t in trends]
            self.trends_listbox.delete(0, tk.END)
            for i, t in enumerate(self.current_trends, 1):
                topic = t.get('topic', 'N/A') if isinstance(t, dict) else str(t)
                source = t.get('source', '') if isinstance(t, dict) else ''
                self.trends_listbox.insert(tk.END, f"{i}. [{source}] {topic}")

            self.progress['value'] = 100
            self.status_label.config(text=f"✅ Quét được {len(trends)} tin hot")
            messagebox.showinfo("Thành công", f"Đã quét được {len(trends)} tin hot từ {', '.join(active)}!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể quét tin:\n{e}")
            self.status_label.config(text="❌ Lỗi")
        finally:
            self.progress['value'] = 0

    def _generate_scripts(self):
        if not self.current_trends:
            messagebox.showwarning("Cảnh báo", "Hãy quét tin hot trước!")
            return

        self.status_label.config(text="📝 Đang tóm tắt...")
        self.root.update()

        try:
            from src.summarizer import build_script
            scripts = build_script(self.current_trends)

            self.scripts_listbox.delete(0, tk.END)
            self.current_ideas = []
            for i, s in enumerate(scripts, 1):
                text = f"{s['headline']}\n   → {s['script']}"
                self.scripts_listbox.insert(tk.END, text)
                self.current_ideas.append(s)

            self.status_label.config(text=f"✅ Đã tạo {len(scripts)} kịch bản")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo kịch bản:\n{e}")

    def _create_videos(self):
        if not self.current_trends:
            messagebox.showwarning("Cảnh báo", "Hãy quét tin hot trước!")
            return

        self.status_label.config(text="🎬 Đang tạo video...")
        self.progress['value'] = 10
        self.root.update()

        try:
            from src.advanced_video_creator import create_news_videos
            self.video_paths = create_news_videos(self.current_trends[:5], self.config)

            self.videos_listbox.delete(0, tk.END)
            for i, path in enumerate(self.video_paths, 1):
                self.videos_listbox.insert(tk.END, f"{i}. {Path(path).name}")

            self.progress['value'] = 100
            self.status_label.config(text=f"✅ Đã tạo {len(self.video_paths)} video")
            messagebox.showinfo("Thành công", f"Đã tạo {len(self.video_paths)} video TikTok!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo video:\n{e}")
        finally:
            self.progress['value'] = 0

    def _open_video_folder(self):
        videos_dir = Path("data/videos").absolute()
        if videos_dir.exists():
            try:
                subprocess.run(['xdg-open', str(videos_dir)], check=False)
            except Exception:
                messagebox.showinfo("Thư mục video", str(videos_dir))

    def _play_selected_video(self):
        selection = self.videos_listbox.curselection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Chưa chọn video!")
            return

        index = selection[0]
        if index < len(self.video_paths):
            video_path = self.video_paths[index]
            candidates = ["vlc", "ffplay", "mpv"]
            player = None
            for candidate in candidates:
                try:
                    if subprocess.run(["which", candidate], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
                        player = candidate
                        break
                except Exception:
                    continue

            try:
                if player:
                    subprocess.Popen([player, video_path])
                else:
                    subprocess.Popen(["xdg-open", video_path])
                self.preview_label.config(text=f"Đang mở: {Path(video_path).name}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở video:\n{e}")

    def run(self):
        self.root.mainloop()


def main():
    app = TikTokDramaGUI()
    app.run()


if __name__ == "__main__":
    main()
