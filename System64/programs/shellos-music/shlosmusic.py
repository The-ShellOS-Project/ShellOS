import customtkinter as ctk
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image, ImageDraw
import os
from pathlib import Path
import time
import io
import json
import shutil
from tkinter import filedialog, messagebox, Menu, simpledialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("ShellOS Music Player")
        self.root.geometry("1100x820")
        
        # Proper UI Scaling
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        
        # Paths
        self.base_dir = Path("MusicLibrary")
        self.playlist_dir = self.base_dir / "Playlists"
        self.base_dir.mkdir(exist_ok=True)
        self.playlist_dir.mkdir(exist_ok=True)
        
        pygame.mixer.init()
        
        # State
        self.playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.total_duration = 0
        self.loop_mode = 0  # 0: No Loop, 1: Loop One, 2: Loop All
        self.is_seeking = False 
        self.current_view = "Library"
        
        self.setup_ui()
        self.load_library_view()
        self.update_ui_loop()

    def setup_ui(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="ShellOS Music", font=("Arial", 22, "bold"), text_color="#0096FF").pack(pady=25)
        
        ctk.CTkButton(self.sidebar, text="🏠 My Library", fg_color="transparent", anchor="w", 
                     command=self.load_library_view).pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.sidebar, text="➕ New Playlist", fg_color="#1f1f1f", 
                     command=self.create_new_playlist).pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="PLAYLISTS", font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15, 5))
        self.playlist_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.playlist_scroll.pack(fill="both", expand=True, padx=5)
        self.refresh_sidebar_playlists()

        # --- Main View ---
        self.main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#121212")
        self.main_container.pack(side="top", fill="both", expand=True)

        self.list_header = ctk.CTkLabel(self.main_container, text="Library", font=("Arial", 26, "bold"), anchor="w")
        self.list_header.pack(fill="x", padx=30, pady=20)

        self.songs_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.songs_frame.pack(fill="both", expand=True, padx=20)

        # --- Bottom Player Bar ---
        self.player_bar = ctk.CTkFrame(self.root, height=115, corner_radius=0, fg_color="#181818", border_width=1, border_color="#252525")
        self.player_bar.pack(side="bottom", fill="x")
        self.player_bar.pack_propagate(False)

        # Left: Info + Metadata Art
        self.info_frame = ctk.CTkFrame(self.player_bar, fg_color="transparent", width=320)
        self.info_frame.pack(side="left", padx=20, fill="y")
        
        self.art_label = ctk.CTkLabel(self.info_frame, text="", width=60, height=60, fg_color="#000", corner_radius=5)
        self.art_label.place(x=0, y=25)
        
        self.track_label = ctk.CTkLabel(self.info_frame, text="Not Playing", font=("Arial", 14, "bold"), anchor="sw", width=240)
        self.track_label.place(x=70, y=30)
        self.artist_label = ctk.CTkLabel(self.info_frame, text="-", font=("Arial", 12), text_color="gray", anchor="nw", width=240)
        self.artist_label.place(x=70, y=55)

        # Center: Controls
        self.ctrl_frame = ctk.CTkFrame(self.player_bar, fg_color="transparent", width=450)
        self.ctrl_frame.pack(side="left", expand=True, fill="both")

        self.loop_btn = ctk.CTkButton(self.ctrl_frame, text="🔁", width=35, fg_color="transparent", text_color="gray", command=self.toggle_loop)
        self.loop_btn.place(relx=0.25, rely=0.35, anchor="center")

        self.prev_btn = ctk.CTkButton(self.ctrl_frame, text="⏮", width=40, fg_color="transparent", command=self.previous_song)
        self.prev_btn.place(relx=0.4, rely=0.35, anchor="center")

        self.play_btn = ctk.CTkButton(self.ctrl_frame, text="▶", width=54, height=54, corner_radius=27, command=self.play_pause)
        self.play_btn.place(relx=0.5, rely=0.35, anchor="center")

        self.next_btn = ctk.CTkButton(self.ctrl_frame, text="⏭", width=40, fg_color="transparent", command=self.next_song)
        self.next_btn.place(relx=0.6, rely=0.35, anchor="center")

        self.progress_bar = ctk.CTkSlider(self.ctrl_frame, from_=0, to=100, width=380, height=14, command=self.seek_position)
        self.progress_bar.place(relx=0.5, rely=0.8, anchor="center")
        self.progress_bar.set(0)
        self.progress_bar.bind("<Button-1>", lambda e: self.set_seeking(True))
        self.progress_bar.bind("<ButtonRelease-1>", lambda e: self.set_seeking(False))

        # Right: Volume & Time
        self.right_frame = ctk.CTkFrame(self.player_bar, fg_color="transparent", width=220)
        self.right_frame.pack(side="right", padx=20, fill="y")

        self.time_label = ctk.CTkLabel(self.right_frame, text="00:00 / 00:00", font=("Consolas", 12))
        self.time_label.place(x=10, y=25)

        self.vol_slider = ctk.CTkSlider(self.right_frame, from_=0, to=1, width=90, command=lambda v: pygame.mixer.music.set_volume(v))
        self.vol_slider.place(x=100, y=60)
        self.vol_slider.set(0.7)

        # Old Status Bar Restored
        self.status_bar = ctk.CTkLabel(self.root, text="Ready", anchor="w", fg_color="#000", padx=20, height=25)
        self.status_bar.pack(side="bottom", fill="x")

    # --- Metadata Engine ---
    def get_metadata(self, path):
        try:
            audio = MP3(path)
            tags = ID3(path)
            cover = None
            for frame in tags.values():
                if hasattr(frame, 'data'):
                    cover = frame.data
                    break
            return {
                "title": str(tags.get("TIT2", Path(path).stem)),
                "artist": str(tags.get("TPE1", "Unknown Artist")),
                "duration": int(audio.info.length),
                "cover_art": cover
            }
        except:
            return {"title": Path(path).stem, "artist": "Unknown", "duration": 0, "cover_art": None}

    def update_song_info(self):
        track = self.playlist[self.current_track_index]
        meta = self.get_metadata(track)
        self.total_duration = meta["duration"]
        self.track_label.configure(text=meta["title"][:40])
        self.artist_label.configure(text=meta["artist"][:40])
        
        # Album Art
        img_data = meta["cover_art"]
        if img_data:
            img = Image.open(io.BytesIO(img_data)).resize((60, 60))
        else:
            img = Image.new('RGB', (60, 60), color='#252525')
        self.art_label.configure(image=ctk.CTkImage(img, size=(60, 60)))
        self.set_status(f"Playing: {meta['title']}")

    # --- Library & Management ---
    def create_new_playlist(self):
        name = simpledialog.askstring("New Playlist", "Playlist Name:")
        if name:
            p_path = self.playlist_dir / f"{name}.json"
            if not p_path.exists():
                with open(p_path, 'w') as f: json.dump([], f)
                self.refresh_sidebar_playlists()
                self.set_status(f"Created playlist '{name}'")

    def refresh_sidebar_playlists(self):
        for w in self.playlist_scroll.winfo_children(): w.destroy()
        for p in self.playlist_dir.glob("*.json"):
            ctk.CTkButton(self.playlist_scroll, text=f"📂 {p.stem}", fg_color="transparent", anchor="w",
                         command=lambda f=p.name: self.load_playlist_view(f)).pack(fill="x")

    def load_library_view(self):
        self.current_view = "Library"
        self.list_header.configure(text="My Library")
        self.playlist = [str(f) for f in self.base_dir.glob("*.mp3")]
        self.update_playlist_display()
        self.set_status("Viewing Library")

    def load_playlist_view(self, filename):
        self.current_view = filename
        with open(self.playlist_dir / filename, 'r') as f: self.playlist = json.load(f)
        self.list_header.configure(text=Path(filename).stem)
        self.update_playlist_display()
        self.set_status(f"Viewing Playlist: {Path(filename).stem}")

    def update_playlist_display(self):
        for w in self.songs_frame.winfo_children(): w.destroy()
        for idx, track in enumerate(self.playlist):
            meta = self.get_metadata(track)
            row = ctk.CTkFrame(self.songs_frame, fg_color="transparent", height=45)
            row.pack(fill="x", pady=1)
            
            btn = ctk.CTkButton(row, text=f"  {meta['title']} - {meta['artist']}", fg_color="transparent", 
                               anchor="w", hover_color="#1e1e1e", command=lambda i=idx: self.play_track(i))
            btn.pack(side="left", fill="both", expand=True)
            btn.bind("<Button-3>", lambda e, t=track, i=idx: self.show_context_menu(e, t, i))

    def show_context_menu(self, event, track_path, index):
        menu = Menu(self.root, tearoff=0, bg="#222", fg="white", borderwidth=0)
        add_menu = Menu(menu, tearoff=0, bg="#222", fg="white")
        for p_file in self.playlist_dir.glob("*.json"):
            add_menu.add_command(label=p_file.stem, command=lambda f=p_file: self.add_to_playlist(track_path, f))
        
        menu.add_cascade(label="Add to Playlist", menu=add_menu)
        if self.current_view == "Library":
            menu.add_command(label="Delete from Disk", command=lambda: self.delete_from_library(track_path))
        else:
            menu.add_command(label="Remove from Playlist", command=lambda: self.remove_from_playlist(index))
        menu.tk_popup(event.x_root, event.y_root)

    def add_to_playlist(self, track_path, playlist_file):
        with open(playlist_file, 'r') as f: data = json.load(f)
        if track_path not in data:
            data.append(track_path)
            with open(playlist_file, 'w') as f: json.dump(data, f)
            self.set_status("Song added to playlist.")

    def remove_from_playlist(self, index):
        self.playlist.pop(index)
        with open(self.playlist_dir / self.current_view, 'w') as f: json.dump(self.playlist, f)
        self.update_playlist_display()
        self.set_status("Removed from playlist.")

    def delete_from_library(self, track_path):
        if messagebox.askyesno("Confirm", "Delete file from disk?"):
            pygame.mixer.music.stop()
            os.remove(track_path)
            self.load_library_view()

    # --- Playback Logic ---
    def toggle_loop(self):
        self.loop_mode = (self.loop_mode + 1) % 3
        modes = {0: ("🔁", "gray"), 1: ("🔂", "#0096FF"), 2: ("🔁", "#0096FF")}
        icon, color = modes[self.loop_mode]
        self.loop_btn.configure(text=icon, text_color=color)

    def set_seeking(self, state): self.is_seeking = state

    def update_ui_loop(self):
        if self.is_playing and not self.is_paused and not self.is_seeking:
            if not pygame.mixer.music.get_busy():
                if self.loop_mode == 1: self.play_track(self.current_track_index)
                else: self.next_song()
            else:
                curr_pos = pygame.mixer.music.get_pos() / 1000
                if self.total_duration > 0:
                    self.progress_bar.set((curr_pos / self.total_duration) * 100)
                    self.time_label.configure(text=f"{time.strftime('%M:%S', time.gmtime(curr_pos))} / {time.strftime('%M:%S', time.gmtime(self.total_duration))}")
        self.root.after(500, self.update_ui_loop)

    def play_track(self, index):
        if not self.playlist: return
        self.current_track_index = index
        try:
            pygame.mixer.music.load(self.playlist[index])
            pygame.mixer.music.play()
            self.is_playing, self.is_paused = True, False
            self.play_btn.configure(text="⏸")
            self.update_song_info()
        except: pass

    def play_pause(self):
        if not self.is_playing: self.play_track(self.current_track_index)
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_btn.configure(text="⏸")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_btn.configure(text="▶")

    def next_song(self):
        if self.current_track_index + 1 < len(self.playlist):
            self.play_track(self.current_track_index + 1)
        elif self.loop_mode == 2: self.play_track(0)

    def previous_song(self):
        self.play_track(max(0, self.current_track_index - 1))

    def seek_position(self, val):
        if self.is_playing: pygame.mixer.music.play(start=(val/100)*self.total_duration)

    def set_status(self, msg):
        self.status_bar.configure(text=msg)

if __name__ == "__main__":
    root = ctk.CTk()
    player = MusicPlayer(root)
    root.mainloop()