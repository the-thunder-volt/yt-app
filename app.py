import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="🎬 Smart YouTube Downloader", layout="centered")

st.title("🎬 Smart YouTube Downloader with Auto Merge")

# === Input field ===
url = st.text_input("Enter YouTube video URL:")

def get_formats(url):
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
        return formats, info.get("title", "video")
    except Exception as e:
        st.error(f"Error fetching formats: {e}")
        return None, None

if url:
    formats, title = get_formats(url)
    if formats:
        st.subheader(f"🎥 Available Formats for: {title}")
        video_formats = []
        audio_formats = []
        for f in formats:
            if f.get("vcodec") != "none" and f.get("acodec") == "none":
                video_formats.append(f)
            elif f.get("acodec") != "none" and f.get("vcodec") == "none":
                audio_formats.append(f)
            elif f.get("vcodec") != "none" and f.get("acodec") != "none":
                video_formats.append(f)

        with st.expander("🎞 Video + Audio Formats"):
            for f in video_formats:
                st.write(f"**{f.get('format_note', 'N/A')}** — {f.get('ext', 'N/A')} | {f.get('height', '')}p | {round(f.get('filesize', 0)/1e6,2) if f.get('filesize') else '?'} MB")

        with st.expander("🎧 Audio Only Formats"):
            for f in audio_formats:
                st.write(f"**{f.get('abr', 'N/A')}kbps** — {f.get('ext', 'N/A')} | {round(f.get('filesize', 0)/1e6,2) if f.get('filesize') else '?'} MB")

        st.info("🎯 Click below to download the best possible version (auto merge if possible).")

        if st.button("⬇️ Download Best Quality"):
            with st.spinner("Downloading best quality video with audio... please wait ⏳"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    video_path = os.path.join(tmpdir, "video.mp4")
                    audio_path = os.path.join(tmpdir, "audio.m4a")

                    # Options for best possible download
                    ydl_opts = {
                        "format": "bestvideo+bestaudio/best",
                        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                        "merge_output_format": "mp4",
                        "quiet": True,
                    }

                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            filename = ydl.prepare_filename(info)
                            final_file = os.path.splitext(filename)[0] + ".mp4"

                        if os.path.exists(final_file):
                            with open(final_file, "rb") as f:
                                st.success("✅ Merged video+audio downloaded successfully!")
                                st.download_button(
                                    label="📥 Download Final Video",
                                    data=f,
                                    file_name=f"{title}.mp4",
                                    mime="video/mp4"
                                )
                        else:
                            # fallback: separate downloads
                            st.warning("⚠️ Merging failed. Downloading separately...")

                            # Video only
                            ydl_opts_video = {"format": "bestvideo", "outtmpl": video_path, "quiet": True}
                            ydl_opts_audio = {"format": "bestaudio", "outtmpl": audio_path, "quiet": True}

                            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                                ydl.download([url])
                            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                                ydl.download([url])

                            if os.path.exists(video_path):
                                with open(video_path, "rb") as v:
                                    st.download_button(
                                        label="🎥 Download Video Only",
                                        data=v,
                                        file_name=f"{title}_video.mp4",
                                        mime="video/mp4"
                                    )

                            if os.path.exists(audio_path):
                                with open(audio_path, "rb") as a:
                                    st.download_button(
                                        label="🎧 Download Audio Only",
                                        data=a,
                                        file_name=f"{title}_audio.m4a",
                                        mime="audio/mp4"
                                    )

                    except Exception as e:
                        st.error(f"Error during download: {e}")
