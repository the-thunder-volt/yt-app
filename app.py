import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Downloader (With or Without FFmpeg)")

url = st.text_input("Enter YouTube video URL:")

if st.button("Download Video"):
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            # Try merged MP4 first (no FFmpeg needed)
            ydl_opts_merged = {
                "format": "best[ext=mp4][acodec!=none][vcodec!=none]/best[ext=mp4]",
                "outtmpl": output_template,
                "quiet": False
            }

            try:
                st.info("⬇️ Attempting to download merged video (no FFmpeg)...")
                with yt_dlp.YoutubeDL(ydl_opts_merged) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    final_path = ydl.prepare_filename(info)

                # ✅ If merged MP4 exists
                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success("✅ Download complete with sound (no FFmpeg needed)!")
                        st.download_button(
                            label="📥 Download MP4",
                            data=f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4"
                        )
                else:
                    raise FileNotFoundError("Merged file not found, will try separate downloads.")

            except Exception as e:
                st.warning("⚠️ Couldn't get merged video, trying separate audio/video...")

                try:
                    # Fallback to separate streams
                    video_path = os.path.join(tmpdir, f"{int(os.times()[4])}_video.mp4")
                    audio_path = os.path.join(tmpdir, f"{int(os.times()[4])}_audio.m4a")

                    ydl_video_opts = {
                        "format": "bestvideo[ext=mp4]",
                        "outtmpl": video_path,
                        "quiet": False
                    }
                    ydl_audio_opts = {
                        "format": "bestaudio[ext=m4a]",
                        "outtmpl": audio_path,
                        "quiet": False
                    }

                    with yt_dlp.YoutubeDL(ydl_video_opts) as ydl:
                        info_video = ydl.extract_info(url, download=True)

                    with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
                        info_audio = ydl.extract_info(url, download=True)

                    title = info_video.get("title", "video")

                    st.success("✅ Video and audio downloaded separately (merge manually if needed).")

                    with open(video_path, "rb") as vf:
                        st.download_button(
                            label="🎞️ Download Video Only",
                            data=vf,
                            file_name=f"{title}_video.mp4",
                            mime="video/mp4"
                        )

                    with open(audio_path, "rb") as af:
                        st.download_button(
                            label="🎵 Download Audio Only",
                            data=af,
                            file_name=f"{title}_audio.m4a",
                            mime="audio/mp4"
                        )

                except Exception as e2:
                    st.error(f"❌ Both methods failed: {e2}")
