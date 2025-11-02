import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Downloader (with Sound)")

url = st.text_input("Enter YouTube video URL:")

if st.button("Download Video"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Output path template
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            # yt-dlp options
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",   # get both streams
                "merge_output_format": "mp4",           # final container
                "outtmpl": output_template,
                "postprocessors": [
                    {
                        "key": "FFmpegMerger"  # <-- ensures video + audio merge
                    }
                ],
            }

            try:
                st.info("⬇️ Downloading and merging video + audio...")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    base = ydl.prepare_filename(info)
                    final_path = os.path.splitext(base)[0] + ".mp4"

                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success("✅ Download ready with sound!")
                        st.download_button(
                            label="📥 Click to download",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ Merge failed. File not found.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
