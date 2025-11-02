import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Video Downloader with Sound")

# === Input field ===
url = st.text_input("Enter YouTube video URL:")

# === Download button ===
if st.button("Download Video"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            ydl_opts = {
                "format": "bestvideo+bestaudio/best",   # ensures both audio + video
                "merge_output_format": "mp4",           # final format
                "outtmpl": output_template,             # where to save temp file
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }]
            }

            try:
                st.info("⬇️ Downloading video with sound... please wait.")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    video_filename = ydl.prepare_filename(info)
                    final_path = os.path.splitext(video_filename)[0] + ".mp4"

                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success("✅ Download complete with sound!")
                        st.download_button(
                            label="📥 Click to download",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ Something went wrong. File not found.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
