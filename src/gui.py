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

from .utils import load_config, save_data, get_today_string, VideoIdea, TrendItem
from .generator import IdeaGenerator
from .fetcher import (
    GoogleTrendsFetcher,
    RedditFetcher,
    TwitterFetcher,
    WebScrapingFetcher,
)
from .video_creator import VideoCreator


class TikTokDramaGUI:
    """Main GUI application for TikTok Drama Generator."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTok Drama Generator")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#1a1a2e')
        self.style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'), foreground='#ff6b6b')
        self.style.configure('Subheader.TLabel', font=('Arial', 12), foreground='#4ecdc4')
        
         # Data
        self.config = load_config()
        self.current_ideas = []
        self.video_paths = []
        self.selected_sources = {
            'google_trends': tk.BooleanVar(value=self.config.get('sources', {}).get('google_trends', {}).get('enabled', False)),
            'reddit': tk.BooleanVar(value=self.config.get('sources', {}).get('reddit', {}).get('enabled', False)),
            'twitter': tk.BooleanVar(value=self.config.get('sources', {}).get('twitter', {}).get('enabled', False)),
            'facebook': tk.BooleanVar(value=self.config.get('sources', {}).get('facebook', {}).get('enabled', False)),
            'web_scraping': tk.BooleanVar(value=self.config.get('sources', {}).get('web_scraping', {}).get('enabled', True)),
        }

        self._configure_icon()
        self._build_ui()
        self._load_today_data()

    def _configure_icon(self):
        """Set app icon if available."""
        icon_path = Path('assets/icon.png')
        if icon_path.exists():
            try:
                img = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, img)
            except Exception:
                pass
    
    def _build_ui(self):
        """Build the GUI interface."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="🎬 TikTok Drama Generator", style='Header.TLabel').pack()
        ttk.Label(header_frame, text="Tạo video TikTok tự động từ trend hằng ngày", style='Subheader.TLabel').pack(pady=2)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        ttk.Label(left_panel, text="📋 Controls", font=('Arial', 12, 'bold'), foreground='#4ecdc4').pack(anchor='w', pady=(0, 10))
        
        # Date selector
        date_frame = ttk.Frame(left_panel)
        date_frame.pack(fill='x', pady=5)
        ttk.Label(date_frame, text="Ngày:").pack(anchor='w')
        self.date_var = tk.StringVar(value=get_today_string())
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
        date_entry.pack(fill='x', pady=2)

        # Social media source selection
        ttk.Label(left_panel, text="🌐 Nguồn tìm trend / drama:", font=('Arial', 11, 'bold'), foreground='#4ecdc4').pack(anchor='w', pady=(15, 5))
        sources_frame = ttk.Frame(left_panel)
        sources_frame.pack(fill='x', pady=5)
        ttk.Checkbutton(sources_frame, text="Google Trends", variable=self.selected_sources['google_trends']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="Reddit", variable=self.selected_sources['reddit']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="X (Twitter)", variable=self.selected_sources['twitter']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="Facebook", variable=self.selected_sources['facebook']).pack(anchor='w')
        ttk.Checkbutton(sources_frame, text="Web scraping", variable=self.selected_sources['web_scraping']).pack(anchor='w')
        
        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="🔄 Tạo trend mới", command=self._generate_new).pack(fill='x', pady=2)
        ttk.Button(btn_frame, text="🎥 Tạo video", command=self._create_videos).pack(fill='x', pady=2)
        ttk.Button(btn_frame, text="📂 Mở thư mục video", command=self._open_video_folder).pack(fill='x', pady=2)
        ttk.Button(btn_frame, text="🔃 Reload", command=self._load_today_data).pack(fill='x', pady=2)
        
        # Status
        ttk.Label(left_panel, text="📊 Status", font=('Arial', 12, 'bold'), foreground='#4ecdc4').pack(anchor='w', pady=(20, 5))
        self.status_label = ttk.Label(left_panel, text="Ready", foreground='#95e1d3')
        self.status_label.pack(anchor='w')
        
        # Right panel - Content
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill='both', expand=True)
        
        # Ideas tab
        ideas_tab = ttk.Frame(self.notebook)
        self.notebook.add(ideas_tab, text='💡 Video Ideas')
        
        ttk.Label(ideas_tab, text="Danh sách ý tưởng video hôm nay:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5, padx=5)
        
        # Ideas list with scrollbar
        ideas_list_frame = ttk.Frame(ideas_tab)
        ideas_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(ideas_list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.ideas_listbox = tk.Listbox(ideas_list_frame, yscrollcommand=scrollbar.set, bg='#16213e', fg='white',
                                        font=('Arial', 10), selectbackground='#0f3460', selectforeground='white',
                                        relief='flat', bd=0, highlightthickness=0)
        self.ideas_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.ideas_listbox.yview)
        
        # Videos tab
        videos_tab = ttk.Frame(self.notebook)
        self.notebook.add(videos_tab, text='🎥 Videos')
        
        ttk.Label(videos_tab, text="Danh sách video đã tạo:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5, padx=5)
        
        videos_list_frame = ttk.Frame(videos_tab)
        videos_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar2 = ttk.Scrollbar(videos_list_frame)
        scrollbar2.pack(side='right', fill='y')
        
        self.videos_listbox = tk.Listbox(videos_list_frame, yscrollcommand=scrollbar2.set, bg='#16213e', fg='white',
                                         font=('Arial', 10), selectbackground='#0f3460', selectforeground='white',
                                         relief='flat', bd=0, highlightthickness=0)
        self.videos_listbox.pack(fill='both', expand=True)
        scrollbar2.config(command=self.videos_listbox.yview)
        
        # Video preview frame
        preview_frame = ttk.Frame(videos_tab)
        preview_frame.pack(fill='x', pady=5)
        
        self.preview_label = ttk.Label(preview_frame, text="Chọn video để xem", foreground='#888')
        self.preview_label.pack()
        
        ttk.Button(preview_frame, text="▶️ Mở video", command=self._play_selected_video).pack(pady=5)
    
    def _load_today_data(self):
        """Load today's ideas and videos."""
        date_str = self.date_var.get()
        
        # Load ideas
        ideas_path = Path(f"data/ideas/ideas_{date_str}.json")
        if ideas_path.exists():
            import json
            with open(ideas_path, 'r', encoding='utf-8') as f:
                ideas_data = json.load(f)
            
            self.ideas_listbox.delete(0, tk.END)
            self.current_ideas = []
            
            for i, idea_data in enumerate(ideas_data, 1):
                text = f"{i}. {idea_data.get('idea', 'N/A')}"
                self.ideas_listbox.insert(tk.END, text)
                self.current_ideas.append(idea_data)
            
            self.status_label.config(text=f"✅ Đã load {len(ideas_data)} ý tưởng")
        else:
            self.ideas_listbox.delete(0, tk.END)
            self.ideas_listbox.insert(tk.END, "Chưa có dữ liệu cho ngày này")
            self.status_label.config(text="⚠️ Không có dữ liệu")
        
        # Load videos
        videos_path = Path(f"data/videos/videos_{date_str}.json")
        if videos_path.exists():
            import json
            with open(videos_path, 'r', encoding='utf-8') as f:
                videos_data = json.load(f)
            
            self.videos_listbox.delete(0, tk.END)
            self.video_paths = []
            
            for i, video_data in enumerate(videos_data, 1):
                path = video_data.get('path', '')
                idea_text = video_data.get('idea', 'Unknown')
                text = f"{i}. {Path(path).name} - {idea_text[:40]}..."
                self.videos_listbox.insert(tk.END, text)
                self.video_paths.append(path)
            
            self.status_label.config(text=f"✅ Đã load {len(videos_data)} video")
        else:
            self.videos_listbox.delete(0, tk.END)
            self.videos_listbox.insert(tk.END, "Chưa có video cho ngày này")
    
    def _generate_new(self):
        """Generate new trends and ideas."""
        self.status_label.config(text="🔄 Đang tạo trend...")
        self.root.update()

        try:
            selected = {name: var.get() for name, var in self.selected_sources.items()}
            active_sources = [name for name, flag in selected.items() if flag]

            if not active_sources:
                messagebox.showwarning("Cảnh báo", "Hãy chọn ít nhất 1 nguồn tìm trend / drama.")
                self.status_label.config(text="⚠️ Chưa chọn nguồn")
                return

            fetcher_map = {
                'google_trends': GoogleTrendsFetcher,
                'reddit': RedditFetcher,
                'twitter': TwitterFetcher,
                'facebook': FacebookFetcher,
                'web_scraping': WebScrapingFetcher,
            }

            trends = []
            for source_name in active_sources:
                try:
                    fetcher = fetcher_map[source_name](self.config)
                    trends.extend(fetcher.fetch())
                except Exception as fetch_error:
                    messagebox.showerror("Lỗi nguồn", f"Lỗi lấy trend từ {source_name}:\n{fetch_error}")
                    self.status_label.config(text="❌ Lỗi nguồn")
                    return

            if not trends:
                from .utils import TrendItem
                fallback_topics = [
                    "Drama hot hôm nay", "Xu hướng TikTok Việt Nam",
                    "Giai trí 24h", "Sao Việt đang nói gì?", "Xu hướng mạng hôm nay"
                ]
                trends = [TrendItem(topic=t, source="fallback", score=70) for t in fallback_topics]
            
            # Generate ideas
            generator = IdeaGenerator(self.config)
            self.current_ideas = [idea.to_dict() for idea in generator.generate_ideas(trends, count=5)]
            
            # Update display
            self.ideas_listbox.delete(0, tk.END)
            for i, idea in enumerate(self.current_ideas, 1):
                self.ideas_listbox.insert(tk.END, f"{i}. {idea['idea']}")
            
            self.status_label.config(text=f"✅ Đã tạo {len(self.current_ideas)} ý tưởng")
            messagebox.showinfo("Thành công", f"Đã tạo {len(self.current_ideas)} ý tưởng video từ {', '.join(active_sources)}!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo trend:\n{e}")
            self.status_label.config(text="❌ Lỗi")
    
    def _create_videos(self):
        """Create videos from current ideas."""
        if not self.current_ideas:
            messagebox.showwarning("Cảnh báo", "Chưa có ý tưởng video! Hãy tạo trend trước.")
            return
        
        self.status_label.config(text="🎥 Đang tạo video...")
        self.root.update()
        
        try:
            # Convert dict back to VideoIdea objects
            from .utils import VideoIdea, TrendItem
            
            ideas = []
            for idea_data in self.current_ideas:
                trend_data = idea_data.get('source_trend', {})
                trend = TrendItem(
                    topic=trend_data.get('topic', ''),
                    source=trend_data.get('source', ''),
                    score=trend_data.get('score', 0),
                    metadata=trend_data.get('metadata', {})
                )
                idea = VideoIdea(
                    idea=idea_data['idea'],
                    source_trend=trend,
                    template_used=idea_data.get('template_used')
                )
                ideas.append(idea)
            
            # Create videos
            creator = VideoCreator(self.config)
            self.video_paths = creator.create_videos_from_ideas(ideas, prefix="daily")
            
            # Update display
            self.videos_listbox.delete(0, tk.END)
            for i, path in enumerate(self.video_paths, 1):
                if path and path != "/dummy/path.mp4":
                    self.videos_listbox.insert(tk.END, f"{i}. {Path(path).name}")
                else:
                    self.videos_listbox.insert(tk.END, f"{i}. [Video placeholder]")
            
            self.status_label.config(text=f"✅ Đã tạo {len(self.video_paths)} video")
            messagebox.showinfo("Thành công", f"Đã tạo {len(self.video_paths)} video!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo video:\n{e}")
            self.status_label.config(text="❌ Lỗi")
    
    def _open_video_folder(self):
        """Open the videos folder in file manager."""
        videos_dir = Path("data/videos").absolute()
        if videos_dir.exists():
            try:
                subprocess.run(['xdg-open', str(videos_dir)], check=False)
            except Exception:
                messagebox.showinfo("Thư mục video", str(videos_dir))
        else:
            messagebox.showwarning("Cảnh báo", "Chưa có thư mục video!")
    
    def _play_selected_video(self):
        """Play selected video with VLC if available, otherwise fallback."""
        selection = self.videos_listbox.curselection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Chưa chọn video!")
            return
        
        index = selection[0]
        if index < len(self.video_paths):
            video_path = self.video_paths[index]
            if not video_path or video_path == "/dummy/path.mp4":
                messagebox.showinfo("Thông báo", "Video này chưa được tạo thật (placeholder)")
                return
            
            candidates = [
                "vlc",
                "ffplay",
                "mpv",
            ]
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
        """Run the application."""
        self.root.mainloop()


def main():
    """Launch the GUI."""
    app = TikTokDramaGUI()
    app.run()


if __name__ == "__main__":
    main()
