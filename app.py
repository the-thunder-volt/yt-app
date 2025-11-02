import streamlit as st
import yt_dlp
import os
import tempfile
import glob

st.title("🎬 YouTube Downloader (with Sound)")

url = st.text_input("Enter YouTube video URL:")

if st.button("Download Video"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {"key": "FFmpegMerger"}  # ensures audio + video merge
                ],
            }

            try:
                st.info("⬇️ Downloading and merging video + audio...")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")

                # Find any mp4 in the temp directory (the merged one)
                mp4_files = glob.glob(os.path.join(tmpdir, "*.mp4"))

                if not mp4_files:
                    st.error("❌ Merge failed or file not found.")
                else:
                    final_path = mp4_files[0]  # get the first (usually only) MP4 file
                    with open(final_path, "rb") as f:
                        st.success(f"✅ Download ready: {title}")
                        st.download_button(
                            label="📥 Click to download video",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4",
                        )

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
