import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
import glob

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 YouTube Downloader — Auto merge or fallback")

url = st.text_input("Enter YouTube video URL:")

if "status" not in st.session_state:
    st.session_state.status = ""
if "progress" not in st.session_state:
    st.session_state.progress = 0

progress_bar = st.progress(0)
status_placeholder = st.empty()

def hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '').strip()
        try:
            val = float(p.replace('%', ''))
            progress_bar.progress(int(val))
        except:
            pass
        st.session_state.status = f"⬇️ Downloading... {p}"
    elif d['status'] == 'finished':
        progress_bar.progress(100)
        st.session_state.status = "✅ Download finished — merging..."

if st.button("✅ Confirm"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            st.session_state.status = "Starting download..."
            status_placeholder.info(st.session_state.status)
            ffmpeg_path = shutil.which("ffmpeg")

            outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ydl_opts = {
                "outtmpl": outtmpl,
                "format": ""bv*+ba/b",
                "progress_hooks": [hook],
                "quiet": True,
            }

            if ffmpeg_path:
                ydl_opts.update({
                    "merge_output_format": "mp4",
                    "ffmpeg_location": ffmpeg_path,
                    "postprocessors": [{"key": "FFmpegMerger"}],
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    base = ydl.prepare_filename(info)

                # find all files
                all_files = glob.glob(os.path.join(tmpdir, "*"))
                mp4_files = [f for f in all_files if f.lower().endswith(".mp4")]
                audio_files = [f for f in all_files if f.lower().endswith((".m4a", ".webm", ".opus"))]
                video_files = [f for f in all_files if f.lower().endswith((".mp4", ".webm"))]

                if mp4_files:
                    # merged file found
                    file_path = mp4_files[0]
                    st.success("✅ Video (with audio) ready to download!")
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📥 Download MP4 (with sound)",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4",
                        )
                elif audio_files and video_files:
                    # fallback to separate audio + video
                    st.warning("⚠️ FFmpeg not available — downloading audio & video separately.")
                    with open(video_files[0], "rb") as vf:
                        st.download_button(
                            label="📺 Download Video (no sound)",
                            data=vf,
                            file_name=os.path.basename(video_files[0]),
                            mime="video/mp4",
                        )
                    with open(audio_files[0], "rb") as af:
                        st.download_button(
                            label="🎧 Download Audio",
                            data=af,
                            file_name=os.path.basename(audio_files[0]),
                            mime="audio/mp4",
                        )
                else:
                    st.error("❌ Could not find downloaded files. Try again.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

if st.session_state.status:
    status_placeholder.info(st.session_state.status)
