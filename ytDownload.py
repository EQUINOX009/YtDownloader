import tkinter as tk from tkinter import filedialog, messagebox, ttk from PIL import Image, ImageTk import subprocess import os import threading import urllib.request import json import io import uuid import re

def toggle_theme(): global dark_mode dark_mode = not dark_mode bg_color = "#2e2e2e" if dark_mode else "#f0f4f7" fg_color = "white" if dark_mode else "black" root.configure(bg=bg_color) for widget in root.winfo_children(): if isinstance(widget, (tk.Label, tk.Checkbutton)): widget.configure(bg=bg_color, fg=fg_color) if isinstance(widget, tk.Button) and widget != theme_button: widget.configure(bg="#4CAF50", fg="white")

def fetch_thumbnail(): url = url_entry.get().strip() if 'watch?v=' in url: video_id = url.split('watch?v=')[-1].split('&')[0] elif 'youtu.be/' in url: video_id = url.split('youtu.be/')[-1].split('?')[0] else: return thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" try: with urllib.request.urlopen(thumbnail_url) as u: raw_data = u.read() im = Image.open(io.BytesIO(raw_data)) im = im.resize((160, 90)) thumbnail_img = ImageTk.PhotoImage(im) thumbnail_label.configure(image=thumbnail_img) thumbnail_label.image = thumbnail_img except: pass

def update_yt_dlp(): subprocess.run(["yt-dlp", "-U"]) messagebox.showinfo("Update", "yt-dlp has been updated.")

def sanitize_filename(name): return re.sub(r'[\/*?:"<>|]', "_", name)

def download_video(): url = url_entry.get().strip() output_dir = path_var.get().strip() or os.getcwd() if not url: messagebox.showerror("Error", "Please enter a YouTube URL.") return

format_type = format_var.get()
if format_type == "MP4 (4K Video)":
    format_code = 'bv[height<=1080]+ba/bestvideo[height<=1080]+bestaudio'
    merge_format = 'mp4'
    extension = 'mp4'
else:
    format_code = 'bestaudio[ext=m4a]/bestaudio'
    merge_format = 'mp3'
    extension = 'mp3'

progress_label.config(text="Downloading...")
progress_bar.start()
download_btn.config(state=tk.DISABLED)

def run_download():
    try:
        metadata = subprocess.run([
            'yt-dlp', '-j', '--no-playlist', url
        ], capture_output=True, text=True, check=True)
        info = json.loads(metadata.stdout)
        title = sanitize_filename(info['title'])
        output_path = os.path.join(output_dir, f"{title}.{extension}")

        command = [
            'yt-dlp',
            '-f', format_code,
            '--merge-output-format', merge_format,
            '-o', output_path,
            url
        ]

        if format_type == "MP3 (Audio Only)":
            command += ['--extract-audio', '--audio-format', 'mp3', '--audio-quality', '0']

        if playlist_var.get():
            command.append('--yes-playlist')
        else:
            command.append('--no-playlist')

        subprocess.run(command, check=True)
        messagebox.showinfo("Success", f"Download complete. File saved to:\n{output_path}")

    except FileNotFoundError:
        messagebox.showerror("Error", "yt-dlp not found. Please ensure it is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Download Failed", f"An error occurred:\n\n{str(e)}")
    finally:
        progress_label.config(text="")
        progress_bar.stop()
        download_btn.config(state=tk.NORMAL)

threading.Thread(target=run_download).start()

def choose_directory(): directory = filedialog.askdirectory() if directory: path_var.set(directory)

GUI Setup

root = tk.Tk() root.title("YouTube 4K/MP3 Downloader") root.geometry("600x500") root.configure(bg="#f0f4f7")

dark_mode = False path_var = tk.StringVar() format_var = tk.StringVar(value="MP4 (4K Video)") playlist_var = tk.BooleanVar()

style = ttk.Style() style.configure("TButton", font=("Segoe UI", 10)) style.configure("TLabel", font=("Segoe UI", 10), background="#f0f4f7")

YouTube URL Entry

tk.Label(root, text="YouTube URL:", bg="#f0f4f7", font=("Segoe UI", 10)).pack(pady=(10, 0)) url_entry = tk.Entry(root, width=60, font=("Segoe UI", 10)) url_entry.pack(pady=5) url_entry.bind("<FocusOut>", lambda e: fetch_thumbnail())

Thumbnail Preview

thumbnail_label = tk.Label(root, bg="#f0f4f7") thumbnail_label.pack(pady=5)

Directory Picker

tk.Label(root, text="Save to Folder:", bg="#f0f4f7").pack() directory_frame = tk.Frame(root, bg="#f0f4f7") directory_frame.pack(pady=5) tk.Entry(directory_frame, textvariable=path_var, width=45, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5)) tk.Button(directory_frame, text="Browse", command=choose_directory).pack(side=tk.LEFT)

Format Selection

tk.Label(root, text="Choose Format:", bg="#f0f4f7").pack(pady=(10, 0)) tk.OptionMenu(root, format_var, "MP4 (4K Video)", "MP3 (Audio Only)").pack(pady=5)

Playlist Option

tk.Checkbutton(root, text="Download entire playlist (if URL is a playlist)", variable=playlist_var, bg="#f0f4f7").pack(pady=5)

Progress Label and Bar

progress_label = tk.Label(root, text="", bg="#f0f4f7") progress_label.pack(pady=5) progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300) progress_bar.pack(pady=5)

Buttons

button_frame = tk.Frame(root, bg="#f0f4f7") button_frame.pack(pady=15) download_btn = tk.Button(button_frame, text="Download", command=download_video, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"), width=15) download_btn.grid(row=0, column=0, padx=10) theme_button = tk.Button(button_frame, text="Toggle Dark Mode", command=toggle_theme, width=15) theme_button.grid(row=0, column=1, padx=10) tk.Button(button_frame, text="Update yt-dlp", command=update_yt_dlp, width=15).grid(row=0, column=2, padx=10)

root.mainloop()

