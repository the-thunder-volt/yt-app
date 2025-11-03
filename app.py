import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎞️ YouTube Downloader — Best Video + Audio")

url = st.text_input("🔗 Enter YouTube Video URL:")

if st.button("Confirm & Prepare Download"):
    if not url.strip():
        st.error("❌ Please enter a valid YouTube URL.")
    else:
        with st.spinner("Analyzing video... please wait."):
            try:
                # Temporary directory for safe handling
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

                    ydl_opts = {
                        "format": "bv*+ba/b",          # best video + audio
                        "merge_output_format": "mp4",  # final output
                        "outtmpl": output_template,
                        "noplaylist": True,
                        "quiet": True
                    }

                    # Get info first
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info.get("title", "video")
                        filesize = info.get("filesize_approx") or 0
                        size_mb = round(filesize / (1024 * 1024), 2)

                    st.info(f"🎥 **{title}**  |  💾 ~{size_mb} MB (approx)")
                    
                    # Show progress bar while downloading
                    progress = st.progress(0)
                    status_text = st.empty()

                    # Progress hook
                    def progress_hook(d):
                        if d['status'] == 'downloading':
                            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                            downloaded = d.get('downloaded_bytes', 0)
                            percent = int(downloaded / total_bytes * 100) if total_bytes else 0
                            progress.progress(percent)
                            status_text.text(f"⬇️ Downloading... {percent}%")

                    # Actual download
                    ydl_opts["progress_hooks"] = [progress_hook]

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        video_path = ydl.prepare_filename(info)
                        merged_path = os.path.splitext(video_path)[0] + ".mp4"

                    progress.progress(100)
                    status_text.text("✅ Download completed!")

                    # Provide buttons for both video and audio
                    if os.path.exists(merged_path):
                        with open(merged_path, "rb") as v:
                            st.download_button(
                                label="📽️ Download Video (MP4)",
                                data=v,
                                file_name=os.path.basename(merged_path),
                                mime="video/mp4"
                            )

                    # Extract audio separately (mp4/m4a)
                    audio_path = os.path.splitext(video_path)[0] + ".m4a"
                    ydl_opts_audio = {
                        "format": "bestaudio/best",
                        "outtmpl": audio_path,
                        "quiet": True,
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "m4a"
                        }]
                    }

                    with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl_audio:
                        ydl_audio.download([url])

                    if os.path.exists(audio_path):
                        with open(audio_path, "rb") as a:
                            st.download_button(
                                label="🎧 Download Audio Only",
                                data=a,
                                file_name=os.path.basename(audio_path),
                                mime="audio/mp4"
                            )

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
