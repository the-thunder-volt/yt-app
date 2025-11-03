import streamlit as st
import yt_dlp
import os
import tempfile
import time
import shutil
import glob

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 YouTube Downloader — Confirm → Progress → Download (with sound)")

url = st.text_input("Enter YouTube video URL:")

# initialize session state keys
if "status_text" not in st.session_state:
    st.session_state.status_text = ""
if "progress" not in st.session_state:
    st.session_state.progress = 0

progress_bar = st.progress(0)
status_placeholder = st.empty()

def progress_hook(d):
    # Called by yt-dlp during download; update progress text & bar
    status = d.get("status")
    if status == "downloading":
        pct = d.get("_percent_str") or d.get("percent")
        # percent might come like "23.4%" or None
        if isinstance(pct, str):
            try:
                num = float(pct.strip().replace("%", ""))
                st.session_state.progress = max(0, min(100, int(num)))
                progress_bar.progress(st.session_state.progress)
                st.session_state.status_text = f"⬇️ Downloading: {pct.strip()}"
            except Exception:
                st.session_state.status_text = f"⬇️ Downloading: {pct}"
        else:
            st.session_state.status_text = "⬇️ Downloading..."
    elif status == "finished":
        st.session_state.status_text = "🔁 Download finished; finalizing/merging..."
        progress_bar.progress(100)

# Confirm button starts everything
if st.button("✅ Confirm"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        st.session_state.status_text = "Starting..."
        progress_bar.progress(0)
        status_placeholder.info(st.session_state.status_text)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            # detect ffmpeg binary (if available in environment)
            ffmpeg_path = shutil.which("ffmpeg")

            # try merged download first (preferred)
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": out_template,
                "progress_hooks": [progress_hook],
                "quiet": True
            }

            # If ffmpeg is available, tell yt-dlp to merge via FFmpegMerger
            if ffmpeg_path:
                ydl_opts["merge_output_format"] = "mp4"
                ydl_opts["postprocessors"] = [{"key": "FFmpegMerger"}]
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            try:
                status_placeholder.info("⬇️ Attempting best quality (video+audio)...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    # sometimes yt-dlp returns different filename patterns; search for mp4
                    # prepare_filename may point to a file without .mp4 if merge postproc not used
                    base = ydl.prepare_filename(info)
                # find any mp4 created in tmpdir (robust)
                mp4_candidates = glob.glob(os.path.join(tmpdir, "*.mp4"))
                if mp4_candidates:
                    final_path = mp4_candidates[0]
                    status_placeholder.success("✅ Merged file ready with audio!")
                    # read bytes and show single download button
                    with open(final_path, "rb") as fh:
                        data_bytes = fh.read()
                    st.download_button(
                        label="📥 Download MP4 (with audio)",
                        data=data_bytes,
                        file_name=os.path.basename(final_path),
                        mime="video/mp4"
                    )
                else:
                    # no merged mp4 found — fall back to separate downloads automatically
                    status_placeholder.warning("⚠️ Merged MP4 not found. Downloading video and audio separately...")
                    # reset progress
                    progress_bar.progress(0)
                    st.session_state.status_text = "Downloading video stream..."
                    status_placeholder.info(st.session_state.status_text)
                    video_path = os.path.join(tmpdir, "video_only.%(ext)s")
                    audio_path = os.path.join(tmpdir, "audio_only.%(ext)s")

                    # download video-only (prefer mp4)
                    with yt_dlp.YoutubeDL({"format": "bestvideo[ext=mp4]/bestvideo", "outtmpl": video_path, "progress_hooks": [progress_hook], "quiet": True}) as ydlv:
                        info_v = ydlv.extract_info(url, download=True)
                    # download audio-only (m4a preferred)
                    progress_bar.progress(30)
                    st.session_state.status_text = "Downloading audio stream..."
                    status_placeholder.info(st.session_state.status_text)
                    with yt_dlp.YoutubeDL({"format": "bestaudio[ext=m4a]/bestaudio", "outtmpl": audio_path, "progress_hooks": [progress_hook], "quiet": True}) as ydla:
                        info_a = ydla.extract_info(url, download=True)

                    # locate downloaded files
                    vid_files = glob.glob(os.path.join(tmpdir, "video_only.*"))
                    aud_files = glob.glob(os.path.join(tmpdir, "audio_only.*"))
                    if vid_files and aud_files:
                        # read bytes for each and provide single pair of buttons (not two-step)
                        with open(vid_files[0], "rb") as vf:
                            vbytes = vf.read()
                        with open(aud_files[0], "rb") as af:
                            abytes = af.read()
                        status_placeholder.success("✅ Video and audio ready (separate files).")
                        # Provide two buttons but they appear together once ready
                        st.download_button(
                            label="📥 Download Video (no audio)",
                            data=vbytes,
                            file_name=os.path.basename(vid_files[0]),
                            mime="video/mp4"
                        )
                        st.download_button(
                            label="📥 Download Audio",
                            data=abytes,
                            file_name=os.path.basename(aud_files[0]),
                            mime="audio/mp4"
                        )
                    else:
                        st.error("❌ Fallback download failed. Try again.")
            except Exception as err:
                st.error(f"⚠️ Error during download: {err}")

# show live text status under the UI
if st.session_state.status_text:
    status_placeholder.info(st.session_state.status_text)
