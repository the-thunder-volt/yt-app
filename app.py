import streamlit as st
import yt_dlp
import os
import tempfile

st.title("🎬 YouTube Video Downloader (Best Quality + Audio)")

url = st.text_input("🔗 Enter YouTube URL:")

if st.button("Confirm & Prepare Download"):
    if not url.strip():
        st.error("❌ Please enter a valid URL.")
    else:
        with st.spinner("Preparing download..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

                ydl_opts = {
                    "format": "bv*+ba/b",
                    "merge_output_format": "mp4",
                    "outtmpl": output_template,
                    "noplaylist": True
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        filesize = info.get("filesize_approx") or info.get("filesize") or 0
                        title = info.get("title", "video")

                        size_mb = round(filesize / (1024 * 1024), 2)
                        st.info(f"🎥 Title: **{title}**  |  💾 Size: ~{size_mb} MB")

                    # === Download file now ===
                    if st.button("⬇️ Start Download"):
                        st.info("Downloading best video with audio...")
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            final_file = ydl.prepare_filename(info)
                            merged_file = os.path.splitext(final_file)[0] + ".mp4"

                        if os.path.exists(merged_file):
                            with open(merged_file, "rb") as f:
                                st.success("✅ Download complete!")
                                st.download_button(
                                    label="📥 Click to save to device",
                                    data=f,
                                    file_name=os.path.basename(merged_file),
                                    mime="video/mp4"
                                )
                        else:
                            st.warning("⚠️ Merged video not found. Trying separate audio...")
                            audio_path = os.path.splitext(final_file)[0] + ".m4a"
