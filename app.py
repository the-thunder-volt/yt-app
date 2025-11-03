import streamlit as st
import yt_dlp
import os
import tempfile
import glob
import shutil

st.set_page_config(page_title="🎬 YouTube Downloader", page_icon="🎥")
st.title("🎬 YouTube Downloader – Best Quality (Auto Merge)")

url = st.text_input("Enter YouTube video URL:")

progress_bar = st.progress(0)
status_placeholder = st.empty()

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '').strip()
        try:
            val = float(p.replace('%', ''))
            progress_bar.progress(int(val))
        except:
            pass
        status_placeholder.info(f"⬇️ Downloading... {p}")
    elif d['status'] == 'finished':
        progress_bar.progress(100)
        status_placeholder.info("✅ Download complete — processing...")


if st.button("🚀 Download Best Quality"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            st.info("🔍 Fetching best video and audio streams...")

            # Detect FFmpeg
            ffmpeg_path = shutil.which("ffmpeg")
            ffmpeg_available = ffmpeg_path is not None

            # yt-dlp options
            ydl_opts = {
                "format": "bv*+ba/best",   # best video + best audio, fallback best
                "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True,
            }

            if ffmpeg_available:
                ydl_opts["merge_output_format"] = "mp4"
                ydl_opts["ffmpeg_location"] = ffmpeg_path
            else:
                st.warning("⚠️ FFmpeg not found — downloading video and audio separately.")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    base_filename = ydl.prepare_filename(info)
                    final_path = os.path.splitext(base_filename)[0] + ".mp4"

                all_files = glob.glob(os.path.join(tmpdir, "*"))
                media_files = [f for f in all_files if os.path.isfile(f)]

                # Fallback: find the largest file if merged one not found
                if not os.path.exists(final_path) and media_files:
                    final_path = max(media_files, key=os.path.getsize)

                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success("✅ Best quality video ready!")
                        st.download_button(
                            label="📥 Download to Device",
                            data=f,
                            file_name=os.path.basename(final_path),
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ Download failed or merged file not found.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
