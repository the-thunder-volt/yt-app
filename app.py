import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Downloader (Video + Audio)")

# === Input field ===
url = st.text_input("Enter YouTube video URL:")

# === Buttons side by side ===
col1, col2 = st.columns(2)

# ====== VIDEO DOWNLOAD ======
with col1:
    if st.button("🎥 Download Video"):
        if not url.strip():
            st.error("Please enter a YouTube URL.")
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": output_template,
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
                            st.success("✅ Video ready with sound!")
                            st.download_button(
                                label="📥 Download Video",
                                data=f,
                                file_name=f"{title}.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("❌ File not found after download.")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")

# ====== AUDIO DOWNLOAD ======
with col2:
    if st.button("🎵 Download Audio"):
        if not url.strip():
            st.error("Please enter a YouTube URL.")
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": output_template,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",  # or "m4a" if you prefer
                        "preferredquality": "192"
                    }]
                }

                try:
                    st.info("🎧 Downloading audio... please wait.")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title", "audio")
                        audio_filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"

                    if os.path.exists(audio_filename):
                        with open(audio_filename, "rb") as f:
                            st.success("✅ Audio ready!")
                            st.download_button(
                                label="🎶 Download Audio",
                                data=f,
                                file_name=f"{title}.mp3",
                                mime="audio/mpeg"
                            )
                    else:
                        st.error("❌ File not found after download.")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
