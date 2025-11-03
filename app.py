import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="🎬 Smart YouTube Downloader", layout="centered")
st.title("🎬 Smart YouTube Downloader (Best Quality + Audio Option)")

url = st.text_input("Enter YouTube video URL:")

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"

if st.button("Confirm"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("⏳ Fetching video info, please wait..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                title = "video"
                merged_path = os.path.join(tmpdir, "merged.mp4")
                audio_path = os.path.join(tmpdir, "audio_only.m4a")
                video_only_path = os.path.join(tmpdir, "video_only.mp4")

                base_opts = {
                    "quiet": True,
                    "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s")
                }

                # === Get info first (no download yet) ===
                try:
                    with yt_dlp.YoutubeDL({"quiet": True, "format": "bv*+ba/b"}) as ydl:
                        info = ydl.extract_info(url, download=False)
                    title = info.get("title", "video")
                    filesize = info.get("filesize_approx", 0)
                    if filesize:
                        st.info(f"💾 Estimated video+audio size: **{sizeof_fmt(filesize)}**")
                except Exception as e:
                    st.warning(f"⚠️ Could not fetch info: {e}")
                    info = None

                st.write("")

                # === 1️⃣ Download best merged video+audio ===
                if st.button("🎬 Download Best Quality (Video+Audio)"):
                    with st.spinner("⬇️ Downloading video and audio..."):
                        try:
                            merge_opts = {
                                **base_opts,
                                "format": "bv*+ba/b",
                                "merge_output_format": "mp4",
                                "outtmpl": merged_path
                            }
                            with yt_dlp.YoutubeDL(merge_opts) as ydl:
                                ydl.download([url])
                            st.success("✅ Merged video with sound downloaded successfully!")

                            if os.path.exists(merged_path):
                                size = os.path.getsize(merged_path)
                                st.caption(f"File size: {sizeof_fmt(size)}")
                                with open(merged_path, "rb") as f:
                                    st.download_button(
                                        "🎥 Download Merged Video",
                                        f,
                                        file_name=f"{title}.mp4",
                                        mime="video/mp4"
                                    )
                        except Exception as e:
                            st.warning(f"⚠️ Merge failed: {e}")

                # === 2️⃣ Separate Audio Download (Always Available) ===
                if st.button("🎧 Download Audio Only"):
                    with st.spinner("🎵 Downloading best audio..."):
                        try:
                            audio_opts = {**base_opts, "format": "bestaudio", "outtmpl": audio_path}
                            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                                ydl.download([url])
                            if os.path.exists(audio_path):
                                size = os.path.getsize(audio_path)
                                st.caption(f"File size: {sizeof_fmt(size)}")
                                renamed_audio = audio_path.replace(".m4a", ".mp3")
                                os.rename(audio_path, renamed_audio)
                                with open(renamed_audio, "rb") as a:
                                    st.download_button(
                                        "⬇️ Download Audio (.mp3)",
                                        a,
                                        file_name=f"{title}_audio.mp3",
                                        mime="audio/mpeg"
                                    )
                                st.success("🎧 Audio file ready!")
                        except Exception as e:
                            st.error(f"❌ Audio-only download failed: {e}")

                # === 3️⃣ Ask for Video-Only Download ===
                st.divider()
                st.info("Would you like to download **video-only** (highest visual quality)?")

                if st.button("🎞️ Yes, get video-only"):
                    with st.spinner("🎞️ Downloading high-quality video only..."):
                        try:
                            video_opts = {**base_opts, "format": "bv*", "outtmpl": video_only_path}
                            with yt_dlp.YoutubeDL(video_opts) as ydl:
                                ydl.download([url])
                            if os.path.exists(video_only_path):
                                size = os.path.getsize(video_only_path)
                                st.caption(f"File size: {sizeof_fmt(size)}")
                                with open(video_only_path, "rb") as f:
                                    st.download_button(
                                        "⬇️ Download Video Only",
                                        f,
                                        file_name=f"{title}_video_only.mp4",
                                        mime="video/mp4"
                                    )
                                st.success("✅ Video-only version ready!")
                        except Exception as e:
                            st.error(f"❌ Failed to download video only: {e}")
