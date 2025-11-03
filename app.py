import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="YouTube Downloader")
st.title("YouTube Downloader — Best Quality Video + Audio")

url = st.text_input("Enter YouTube Video URL:")

if st.button("Confirm & Prepare Download"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Analyzing video streams... please wait"):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

                    # Best possible quality video + audio
                    ydl_opts = {
                        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                        "merge_output_format": "mp4",
                        "outtmpl": output_template,
                        "noplaylist": True,
                        "prefer_ffmpeg": True,
                        "quiet": True,
                        "postprocessor_args": ["-c:v", "copy", "-c:a", "aac"]
                    }

                    # Extract video info
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info.get("title", "video")
                        filesize = info.get("filesize_approx") or 0
                        size_mb = round(filesize / (1024 * 1024), 2)
                        quality = info.get("resolution") or f"{info.get('height', '?')}p"

                    st.info(f"Title: {title}\nQuality: {quality}\nEstimated Size: {size_mb} MB")

                    # Start download
                    if st.button("Start Download"):
                        st.info("Downloading best quality video and audio...")
                        progress = st.progress(0)
                        status_text = st.empty()

                        # Progress hook
                        def hook(d):
                            if d['status'] == 'downloading':
                                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                                done = d.get('downloaded_bytes', 0)
                                percent = int(done / total * 100) if total else 0
                                progress.progress(percent)
                                status_text.text(f"Downloading... {percent}%")
                            elif d['status'] == 'finished':
                                status_text.text("Merging audio and video with FFmpeg...")

                        ydl_opts["progress_hooks"] = [hook]

                        try:
                            # Download merged video
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                info = ydl.extract_info(url, download=True)
                                video_path = ydl.prepare_filename(info)
                                merged_path = os.path.splitext(video_path)[0] + ".mp4"

                            progress.progress(100)
                            status_text.text("Download completed!")

                            # Video Download Button
                            if os.path.exists(merged_path):
                                with open(merged_path, "rb") as f:
                                    st.success("Video (with audio) ready for download.")
                                    st.download_button(
                                        label="Download Video (MP4)",
                                        data=f,
                                        file_name=os.path.basename(merged_path),
                                        mime="video/mp4"
                                    )

                            # Separate Audio Download
                            st.info("Preparing high-quality audio separately...")

                            audio_path = os.path.splitext(video_path)[0] + ".m4a"
                            ydl_opts_audio = {
                                "format": "bestaudio[ext=m4a]/bestaudio",
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
                                        label="Download Audio Only (M4A)",
                                        data=a,
                                        file_name=os.path.basename(audio_path),
                                        mime="audio/mp4"
                                    )
                            else:
                                st.warning("Could not extract separate audio.")

                        except Exception as err:
                            st.error(f"Download error: {err}")

            except Exception as e:
                st.error(f"Error preparing download: {e}")
