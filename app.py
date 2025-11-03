import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Downloader — Auto with/without Sound Merge")

url = st.text_input("Enter YouTube video URL:")

if st.button("Download Video"):
    if not url.strip():
        st.error("❌ Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            # Default: try to merge best video+audio
            ydl_opts = {
                "format": "bv*+ba/b",  # Best video + best audio
                "merge_output_format": "mp4",
                "outtmpl": output_template,
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }]
            }

            try:
                st.info("⬇️ Downloading best quality (video + audio merged)...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    filename = ydl.prepare_filename(info)
                    merged_file = os.path.splitext(filename)[0] + ".mp4"

                # ✅ CASE 1: merged successfully
                if os.path.exists(merged_file):
                    with open(merged_file, "rb") as f:
                        st.success("✅ Download complete with sound!")
                        st.download_button(
                            label="📥 Download Video",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4"
                        )

                # ❌ CASE 2: ffmpeg missing → fallback to separate downloads
                else:
                    st.warning("⚠️ Merging failed (FFmpeg missing). Downloading separately...")
                    video_path = os.path.join(tmpdir, f"{title}_video.mp4")
                    audio_path = os.path.join(tmpdir, f"{title}_audio.m4a")

                    # Download video only
                    st.info("🎥 Downloading video...")
                    video_opts = {
                        "format": "bestvideo",
                        "outtmpl": video_path,
                    }
                    with yt_dlp.YoutubeDL(video_opts) as ydl:
                        ydl.download([url])

                    # Download audio only
                    st.info("🎵 Downloading audio...")
                    audio_opts = {
                        "format": "bestaudio",
                        "outtmpl": audio_path,
                    }
                    with yt_dlp.YoutubeDL(audio_opts) as ydl:
                        ydl.download([url])

                    # Offer both downloads
                    if os.path.exists(video_path) and os.path.exists(audio_path):
                        st.success("✅ Downloads complete! (Video + Audio separate)")
                        with open(video_path, "rb") as v, open(audio_path, "rb") as a:
                            st.download_button(
                                label="📹 Download Video Only",
                                data=v,
                                file_name=os.path.basename(video_path),
                                mime="video/mp4"
                            )
                            st.download_button(
                                label="🎧 Download Audio Only",
                                data=a,
                                file_name=os.path.basename(audio_path),
                                mime="audio/m4a"
                            )
                    else:
                        st.error("❌ Failed to download video or audio.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
