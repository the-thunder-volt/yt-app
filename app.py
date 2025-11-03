import streamlit as st
import yt_dlp
import os
import tempfile
import base64

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 Smart YouTube Downloader (Auto with/without Sound)")

url = st.text_input("Enter YouTube video URL:")

def trigger_download(file_path, label):
    """Automatically trigger a browser download (respects browser settings)."""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}" id="autodl" style="display:none;"></a>'
    js = """
    <script>
    const a = document.getElementById('autodl');
    a.click();
    </script>
    """
    st.markdown(href + js, unsafe_allow_html=True)
    st.success(f"✅ {label} downloaded successfully!")

if st.button("Download Video"):
    if not url.strip():
        st.error("❌ Please enter a YouTube URL.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ydl_opts = {
                "format": "bv*+ba/b",
                "merge_output_format": "mp4",
                "outtmpl": output_template,
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }]
            }

            try:
                st.info("⬇️ Attempting to download best quality (merged)...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "video")
                    filename = ydl.prepare_filename(info)
                    merged_file = os.path.splitext(filename)[0] + ".mp4"

                if os.path.exists(merged_file):
                    st.success("✅ Download complete with sound!")
                    trigger_download(merged_file, "Merged video")

                else:
                    st.warning("⚠️ Merging failed (no FFmpeg). Downloading separately...")

                    video_path = os.path.join(tmpdir, f"{title}_video.mp4")
                    audio_path = os.path.join(tmpdir, f"{title}_audio.m4a")

                    st.info("🎥 Downloading video...")
                    with yt_dlp.YoutubeDL({"format": "bestvideo", "outtmpl": video_path}) as ydl:
                        ydl.download([url])

                    st.info("🎵 Downloading audio...")
                    with yt_dlp.YoutubeDL({"format": "bestaudio", "outtmpl": audio_path}) as ydl:
                        ydl.download([url])

                    st.success("✅ Video + Audio downloaded separately.")
                    trigger_download(video_path, "Video")
                    trigger_download(audio_path, "Audio")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
