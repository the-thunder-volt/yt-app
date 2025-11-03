import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="YouTube Downloader")
st.title("YouTube Downloader — Best Video + Separate Audio")

url = st.text_input("Enter YouTube video URL:")

if st.button("Confirm & Start Download"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Preparing download options..."):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Output template
                    output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

                    # Best quality video + audio merged
                    ydl_opts_video = {
                        "format": "bv*+ba/b",
                        "merge_output_format": "mp4",
                        "outtmpl": output_template,
                        "noplaylist": True,
                        "quiet": True,
                        "prefer_ffmpeg": True,
                    }

                    # Extract video info (just to show name and size)
                    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info.get("title", "video")
                        filesize = info.get("filesize_approx") or 0
                        size_mb = round(filesize / (1024 * 1024), 2)
                        st.info(f"Title: {title}\nEstimated Size: {size_mb} MB")

                    progress = st.progress(0)
                    status = st.empty()

                    def progress_hook(d):
                        if d["status"] == "downloading":
                            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                            done = d.get("downloaded_bytes", 0)
                            percent = int(done / total * 100) if total else 0
                            progress.progress(percent)
                            status.text(f"Downloading... {percent}%")
                        elif d["status"] == "finished":
                            status.text("Merging audio and video using FFmpeg...")

                    ydl_opts_video["progress_hooks"] = [progress_hook]

                    st.info("Downloading best quality video with audio...")
                    merged_file = None

                    try:
                        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                            info = ydl.extract_info(url, download=True)
                            video_path = ydl.prepare_filename(info)
                            merged_file = os.path.splitext(video_path)[0] + ".mp4"

                        progress.progress(100)
                        status.text("Merged file ready.")

                        # === SEPARATE AUDIO FILE ===
                        audio_path = os.path.splitext(video_path)[0] + ".m4a"
                        ydl_opts_audio = {
                            "format": "bestaudio[ext=m4a]/bestaudio",
                            "outtmpl": audio_path,
                            "quiet": True,
                            "noplaylist": True,
                            "postprocessors": [{
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "m4a"
                            }],
                        }

                        st.info("Extracting separate audio file...")
                        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl_audio:
                            ydl_audio.download([url])

                        # === DOWNLOAD BUTTONS ===
                        if os.path.exists(merged_file):
                            with open(merged_file, "rb") as vf:
                                st.success("Video with audio ready for download.")
                                st.download_button(
                                    label="Download Merged Video (MP4)",
                                    data=vf,
                                    file_name=os.path.basename(merged_file),
                                    mime="video/mp4"
                                )

                        if os.path.exists(audio_path):
                            with open(audio_path, "rb") as af:
                                st.download_button(
                                    label="Download Separate Audio (M4A)",
                                    data=af,
                                    file_name=os.path.basename(audio_path),
                                    mime="audio/mp4"
                                )
                        else:
                            st.warning("Audio extraction failed.")

                    except Exception as err:
                        st.error(f"Error during download: {err}")

            except Exception as e:
                st.error(f"Error preparing video: {e}")
