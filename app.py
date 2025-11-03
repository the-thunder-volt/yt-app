import streamlit as st
import yt_dlp
import os
import tempfile
import glob
import shutil

st.set_page_config(page_title="🎬 YouTube Downloader", page_icon="🎥")
st.title("🎬 YouTube Downloader (All Formats)")

url = st.text_input("Enter YouTube video URL:")

if "formats" not in st.session_state:
    st.session_state.formats = []
if "selected_format" not in st.session_state:
    st.session_state.selected_format = None

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


# ========== STEP 1: FETCH FORMATS ==========
if st.button("🔍 Fetch Available Qualities"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                for f in info["formats"]:
                    filesize = f.get("filesize") or f.get("filesize_approx")
                    height = f.get("height", 0)
                    resolution = f.get("resolution") or (f"{height}p" if height else "audio")
                    vcodec = f.get("vcodec")
                    acodec = f.get("acodec")
                    type_str = (
                        "🎞️ Video+Audio" if vcodec != "none" and acodec != "none" else
                        "🎥 Video-only" if vcodec != "none" else
                        "🎧 Audio-only"
                    )

                    formats.append({
                        "format_id": f["format_id"],
                        "ext": f["ext"],
                        "resolution": resolution,
                        "fps": f.get("fps", ""),
                        "filesize": filesize,
                        "vcodec": vcodec,
                        "acodec": acodec,
                        "height": height,
                        "type": type_str,
                    })

                if not formats:
                    st.warning("⚠️ No formats found for this video.")
                else:
                    st.session_state.formats = sorted(formats, key=lambda x: (x["height"] or 0))
                    st.success("✅ All available qualities fetched successfully!")

        except Exception as e:
            st.error(f"⚠️ Error fetching formats: {e}")


# ========== STEP 2: SELECT FORMAT ==========
if st.session_state.formats:
    options = [
        f"{f['resolution']} | {f['type']} | {f['ext']} | "
        f"{round((f['filesize'] or 0)/1024/1024, 1)} MB"
        for f in st.session_state.formats
    ]
    selected_index = st.selectbox(
        "🎚️ Choose format to download:",
        range(len(options)),
        format_func=lambda i: options[i],
    )
    st.session_state.selected_format = st.session_state.formats[selected_index]


# ========== STEP 3: DOWNLOAD ==========
if st.button("✅ Confirm & Download"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    elif not st.session_state.selected_format:
        st.error("Please fetch and select a format first.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            st.info("Preparing download...")

            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ffmpeg_path = shutil.which("ffmpeg")

            ydl_opts = {
                "format": st.session_state.selected_format["format_id"],
                "outtmpl": output_template,
                "progress_hooks": [progress_hook],
                "quiet": True,
            }

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

                all_files = glob.glob(os.path.join(tmpdir, "*"))
                media_files = [f for f in all_files if os.path.isfile(f)]

                if media_files:
                    file_path = media_files[0]
                    with open(file_path, "rb") as f:
                        mime = "audio/mp4" if "audio" in st.session_state.selected_format["type"].lower() else "video/mp4"
                        st.success(f"✅ {st.session_state.selected_format['type']} ready!")
                        st.download_button(
                            label="📥 Download to Device",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime=mime,
                        )
                else:
                    st.error("❌ File not found after download. Try again.")
            except Exception as e:
                st.error(f"⚠️ Error during download: {e}")
