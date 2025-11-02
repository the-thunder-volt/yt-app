import streamlit as st
import yt_dlp
import os
import time

# === App title ===
st.title("🎬 YouTube Video Downloader")

# === Input field ===
url = st.text_input("Enter YouTube video URL:")

# === When user clicks button ===
if st.button("Download Video"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # Generate filename with title placeholder
        timestamp = int(time.time())
        filename = f"video_{timestamp}.mp4"
        output_path = os.path.join(downloads_path, filename)

        # yt-dlp options
        ydl_opts = {
            "format": "bv*+ba/b",
            "outtmpl": output_path,
            "merge_output_format": "mp4",
        }

        # Download
        try:
            st.info("Downloading... please wait.")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(output_path):
                st.success(f"✅ Download complete! Saved to:\n{output_path}")
            else:
                st.error("❌ Download failed.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
