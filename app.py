import streamlit as st
import yt_dlp
import os
import time
import tempfile
import shutil

st.title("🎬 YouTube Video Downloader (with Sound)")

url = st.text_input("🔗 Enter YouTube URL:")

if st.button("Download"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
    else:
        # Temporary folder (auto-deletes after session)
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"video_{int(time.time())}.mp4")

        # Locate ffmpeg
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            st.error("❌ FFmpeg not found. Make sure it's installed via packages.txt.")
            st.stop()

        # yt-dlp options
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": output_path,
            "ffmpeg_location": ffmpeg_path,
            "postprocessors": [{"key": "FFmpegMerger"}],
            "quiet": False
        }

        try:
            st.info("📥 Downloading with sound... Please wait ⏳")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(output_path):
                st.success("✅ Done! Ready to download.")
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download to your device",
                        data=f,
                        file_name=os.path.basename(output_path),
                        mime="video/mp4"
                    )
            else:
                st.error("❌ Video file not found.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
