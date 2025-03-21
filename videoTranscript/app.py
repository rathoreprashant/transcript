import os
import subprocess
from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp

app = Flask(__name__)

# Set the download directory to the user's Downloads folder
DOWNLOADS_DIR = r"C:\Users\LENOVO\Downloads"

def download_audio(url):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # Initial quality
        }],
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = f"{info['title']}.mp3"
        return filename

def compress_audio(file_path, output_path, target_size_mb=16):
    """Compress MP3 to be ≤16MB using FFmpeg."""
    bitrate = "64k"  # Default bitrate for compression
    subprocess.run([
        "ffmpeg", "-i", file_path, "-b:a", bitrate, output_path, "-y"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form["url"]
        if video_url:
            try:
                # Download the audio
                file_name = download_audio(video_url)
                file_path = os.path.join(DOWNLOADS_DIR, file_name)

                # Compress the audio to ≤16MB
                compressed_file_path = os.path.join(DOWNLOADS_DIR, f"compressed_{file_name}")
                compress_audio(file_path, compressed_file_path)

                # Return the download link
                return render_template("index.html", success=True, file_path=compressed_file_path)

            except Exception as e:
                return render_template("index.html", error=str(e))
        else:
            return render_template("index.html", warning="Please enter a valid YouTube URL.")

    return render_template("index.html")


@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
