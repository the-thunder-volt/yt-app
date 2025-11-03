import streamlit as st
import yt_dlp
import os
import tempfile
import time

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 Smart YouTube Downloader")

url = st.text_input("Enter YouTube video URL:")

# ---- Progress callback ----
def hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        st.session_state.progress_text = f"⬇️ Downloading... {percent}"
    elif d['status'] == 'finished':
        st.session_state.progress_text = "✅ Download complete. Finalizing..."

if st.button("✅ Confirm"):
    if not url.strip():
        st.error("❌ Please enter a YouTube URL.")
    else:
        st.session_state.progress_text = "Starting download..."
        st.empty()
        progress_placeholder = st.empty()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ydl_opts = {
                "format": "bv*+ba/b",
                "merge_output_format": "mp4",
                "outtmpl": output_template,
                "progress_hooks": [hook],
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }]
            }

            try:
                progress_placeholder.info("⬇️ Attempting best quality (video + audio merged)...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    filename = ydl.prepare_filename(info)
                    merged_file = os.path.splitext(filename)[0] + ".mp4"

                # Update progress status
                progress_placeholder.success("✅ Download complete with sound!")

                if os.path.exists(merged_file):
                    # Step 3: Show single download button
                    with open(merged_file, "rb") as f:
                        st.download_button(
                            label="📥 Download to Device",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4"
                        )
                else:
                    progress_placeholder.warning("⚠️ Merging failed (no FFmpeg). Downloading separately...")

                    video_path = os.path.join(tmpdir, f"{title}_video.mp4")
                    audio_path = os.path.join(tmpdir, f"{title}_audio.m4a")

                    # Download video only
                    st.info("🎥 Downloading video stream...")
                    with yt_dlp.YoutubeDL({"format": "bestvideo", "outtmpl": video_path, "progress_hooks": [hook]}) as ydl:
                        ydl.download([url])

                    # Download audio only
                    st.info("🎵 Downloading audio stream...")
                    with yt_dlp.YoutubeDL({"format": "bestaudio", "outtmpl": audio_path, "progress_hooks": [hook]}) as ydl:
                        ydl.download([url])

                    progress_placeholder.success("✅ Video and audio downloaded separately.")
                    st.download_button(
                        label="📹 Download Video (no sound)",
                        data=open(video_path, "rb").read(),
                        file_name=os.path.basename(video_path),
                        mime="video/mp4"
                    )
                    st.download_button(
                        label="🎧 Download Audio (M4A)",
                        data=open(audio_path, "rb").read(),
                        file_name=os.path.basename(audio_path),
                        mime="audio/m4a"
                    )

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

# Display live progress text
if "progress_text" in st.session_state:
    st.write(st.session_state.progress_text)
