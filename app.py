import streamlit as st
import yt_dlp
import os
import tempfile
import glob
import shutil

st.set_page_config(page_title="🎬 YouTube Downloader", page_icon="🎥")
st.title("🎬 YouTube Downloader with Quality Selector")

# ========================
# Input for YouTube URL
# ========================
url = st.text_input("Enter YouTube video URL:")

# Session state to store info
if "formats" not in st.session_state:
    st.session_state.formats = []
if "selected_format" not in st.session_state:
    st.session_state.selected_format = None

progress_bar = st.progress(0)
status_placeholder = st.empty()


def progress_hook(d):
    """Progress bar updater"""
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


# ========================
# STEP 1: Fetch formats
# ========================
if st.button("🔍 Fetch Available Qualities"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = [
                    {
                        "format_id": f["format_id"],
                        "ext": f["ext"],
                        "resolution": f.get("resolution") or f"{f.get('height', '')}p",
                        "fps": f.get("fps", ""),
                        "filesize": f.get("filesize") or f.get("filesize_approx"),
                        "vcodec": f.get("vcodec"),
                        "acodec": f.get("acodec"),
                    }
                    for f in info["formats"]
                    if f.get("vcodec") != "none" and f.get("acodec") != "none"
                ]

                # Filter only video+audio combined formats
                st.session_state.formats = sorted(formats, key=lambda x: x["height"] if x["height"] else 0)
                st.success("✅ Fetched available qualities successfully!")
        except Exception as e:
            st.error(f"⚠️ Error fetching formats: {e}")

# ========================
# STEP 2: Select format
# ========================
if st.session_state.formats:
    options = [
        f"{f['resolution']} ({f['ext']}) - {round((f['filesize'] or 0)/1024/1024, 1)} MB"
        for f in st.session_state.formats
    ]
    selected_index = st.selectbox("🎚️ Choose quality to download:", range(len(options)), format_func=lambda i: options[i])
    selected_format = st.session_state.formats[selected_index]
    st.session_state.selected_format = selected_format

# ========================
# STEP 3: Download
# ========================
if st.button("✅ Confirm & Download"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    elif not st.session_state.selected_format:
        st.error("Please fetch and select a video quality first.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            st.info("Preparing your download...")

            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ffmpeg_path = shutil.which("ffmpeg")

            ydl_opts = {
                "format": st.session_state.selected_format["format_id"],
                "outtmpl": output_template,
                "progress_hooks": [progress_hook],
                "quiet": True,
            }

            # Add ffmpeg options if available
            if ffmpeg_path:
                ydl_opts.update({
                    "merge_output_format": "mp4",
                    "ffmpeg_location": ffmpeg_path,
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    base = ydl.prepare_filename(info)

                # Look for downloaded files
                all_files = glob.glob(os.path.join(tmpdir, "*"))
                mp4_files = [f for f in all_files if f.lower().endswith(".mp4")]
                audio_files = [f for f in all_files if f.lower().endswith((".m4a", ".webm", ".opus"))]
                video_files = [f for f in all_files if f.lower().endswith((".mp4", ".webm"))]

                if mp4_files:
                    file_path = mp4_files[0]
                    with open(file_path, "rb") as f:
                        st.success("✅ Video with sound ready!")
                        st.download_button(
                            label="📥 Download to Device",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4",
                        )
                elif audio_files and video_files:
                    st.warning("⚠️ FFmpeg not available — downloading separately.")
                    with open(video_files[0], "rb") as vf:
                        st.download_button("📺 Download Video (no sound)", vf, os.path.basename(video_files[0]), mime="video/mp4")
                    with open(audio_files[0], "rb") as af:
                        st.download_button("🎧 Download Audio", af, os.path.basename(audio_files[0]), mime="audio/mp4")
                else:
                    st.error("❌ File not found after download. Try again.")
            except Exception as e:
                st.error(f"⚠️ Error during download: {e}")
