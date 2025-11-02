import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Video Downloader")

url = st.text_input("Enter YouTube video URL:")

if st.button("Download Video"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ydl_opts = {
                "format": "bv*+ba/b",
                "outtmpl": output_path,
                "merge_output_format": "mp4",
            }

            try:
                st.info("⬇️ Downloading... please wait.")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, download=True)
                    title = result.get("title", "video")
                    final_path = os.path.join(tmpdir, f"{title}.mp4")

                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success("✅ Download complete!")
                        st.download_button(
                            label="📥 Click to download video",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4",
                        )
                else:
                    st.error("❌ Download failed. Try again.")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
