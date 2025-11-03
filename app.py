import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="🎬 Smart YouTube Downloader", layout="centered")
st.title("🎬 Smart YouTube Downloader (Best Quality Video + Audio)")

url = st.text_input("Enter YouTube video URL:")

if st.button("Confirm"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("🎥 Downloading best quality video and audio... please wait."):
            with tempfile.TemporaryDirectory() as tmpdir:
                title = "video"
                merged_path = os.path.join(tmpdir, "merged.mp4")
                audio_path = os.path.join(tmpdir, "audio_only.m4a")

                # Base options
                base_opts = {"quiet": True, "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s")}

                # ======== 1️⃣ Try best merged (video + audio) ========
                try:
                    merge_opts = {
                        **base_opts,
                        "format": "bv*+ba/b",
                        "merge_output_format": "mp4",
                        "outtmpl": merged_path
                    }
                    with yt_dlp.YoutubeDL(merge_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get("title", "video")
                        merged_path = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp4"
                except Exception as e:
                    st.warning(f"⚠️ Merge failed: {e}")
                    merged_path = None

                # ======== 2️⃣ Always get audio separately ========
                try:
                    audio_opts = {**base_opts, "format": "bestaudio", "outtmpl": audio_path}
                    with yt_dlp.YoutubeDL(audio_opts) as ydl:
                        ydl.download([url])
                except Exception as e:
                    st.warning(f"⚠️ Audio-only download failed: {e}")

                # ======== 3️⃣ If merge failed, download best video only ========
                if not os.path.exists(merged_path):
                    st.warning("⚠️ FFmpeg merge failed — downloading best video only.")
                    video_path = os.path.join(tmpdir, "video_only.mp4")
                    try:
                        video_opts = {**base_opts, "format": "bv*", "outtmpl": video_path}
                        with yt_dlp.YoutubeDL(video_opts) as ydl:
                            ydl.download([url])
                        merged_path = video_path
                    except Exception as e:
                        st.error(f"❌ Could not download video: {e}")
                        merged_path = None

                # ======== 4️⃣ Provide download buttons ========
                if merged_path and os.path.exists(merged_path):
                    with open(merged_path, "rb") as f:
                        st.success("✅ Video ready for download!")
                        st.download_button(
                            "🎥 Download Video (Best Quality)",
                            f,
                            file_name=f"{title}.mp4",
                            mime="video/mp4"
                        )

                if os.path.exists(audio_path):
                    renamed_audio = audio_path.replace(".m4a", ".mp3")
                    os.rename(audio_path, renamed_audio)
                    with open(renamed_audio, "rb") as a:
                        st.info("🎧 Separate high-quality audio available.")
                        st.download_button(
                            "🎧 Download Audio Only",
                            a,
                            file_name=f"{title}_audio.mp3",
                            mime="audio/mpeg"
                        )

                if not merged_path and not os.path.exists(audio_path):
                    st.error("❌ Download failed completely.")
