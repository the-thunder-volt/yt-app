import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="🎬 Smart YouTube Downloader", layout="centered")
st.title("🎬 Smart YouTube Downloader — Best Quality Only")

url = st.text_input("Enter YouTube video URL:")

if st.button("⬇️ Download Best Quality"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("🎥 Fetching and downloading best quality video..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Define output template
                outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")

                # Main option — best video + best audio merged
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": outtmpl,
                    "quiet": True
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title", "video")
                        filename = ydl.prepare_filename(info)
                        final_path = os.path.splitext(filename)[0] + ".mp4"

                    # ✅ CASE 1: Successfully merged video+audio
                    if os.path.exists(final_path):
                        with open(final_path, "rb") as f:
                            st.success("✅ Download complete (with sound)!")
                            st.download_button(
                                "📥 Download Merged Video",
                                f,
                                file_name=f"{title}.mp4",
                                mime="video/mp4"
                            )

                    else:
                        # ⚠️ CASE 2: Merge failed → fallback to video only + audio separately
                        st.warning("⚠️ Merge failed — downloading best video and audio separately...")

                        video_path = os.path.join(tmpdir, f"{title}_video.mp4")
                        audio_path = os.path.join(tmpdir, f"{title}_audio.m4a")

                        # Download best video only
                        video_opts = {"format": "bestvideo", "outtmpl": video_path, "quiet": True}
                        with yt_dlp.YoutubeDL(video_opts) as ydl:
                            ydl.download([url])

                        # Download best audio only
                        audio_opts = {"format": "bestaudio", "outtmpl": audio_path, "quiet": True}
                        with yt_dlp.YoutubeDL(audio_opts) as ydl:
                            ydl.download([url])

                        # ✅ Show download buttons
                        if os.path.exists(video_path):
                            with open(video_path, "rb") as v:
                                st.success("🎞 Best quality video downloaded.")
                                st.download_button(
                                    "🎥 Download Video Only",
                                    v,
                                    file_name=f"{title}_video.mp4",
                                    mime="video/mp4"
                                )

                        if os.path.exists(audio_path):
                            # rename to .mp3 for user clarity
                            renamed_audio = audio_path.replace(".m4a", ".mp3")
                            os.rename(audio_path, renamed_audio)
                            with open(renamed_audio, "rb") as a:
                                st.info("🎧 Separate audio available (converted to .mp3).")
                                st.download_button(
                                    "🎧 Download Audio Only",
                                    a,
                                    file_name=f"{title}_audio.mp3",
                                    mime="audio/mpeg"
                                )

                except Exception as e:
                    st.error(f"⚠️ Error during download: {e}")
