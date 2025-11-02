import streamlit as st
import yt_dlp
import os
import time
import shutil

st.title("🎬 YouTube Video Downloader (with Sound)")

url = st.text_input("🔗 Enter YouTube URL:")

if st.button("Download"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
    else:
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)

        filename = f"video_{int(time.time())}.mp4"
        output_path = os.path.join(download_dir, filename)

        # Locate ffmpeg automatically
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            st.error("❌ FFmpeg not found. Make sure it's installed or added via packages.txt.")
            st.stop()

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",  # merge highest quality video + audio
            "merge_output_format": "mp4",
            "outtmpl": output_path,
            "ffmpeg_location": ffmpeg_path,        # <-- Ensures yt-dlp uses ffmpeg
            "postprocessors": [{
                "key": "FFmpegMerger",             # Merges video+audio properly
            }],
            "quiet": False
        }

        try:
            st.info("📥 Downloading video with sound... Please wait ⏳")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(output_path):
                st.success("✅ Download complete with sound!")
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download to your device",
                        data=f,
                        file_name=filename,
                        mime="video/mp4"
                    )
            else:
                st.error("❌ File not found after download.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
