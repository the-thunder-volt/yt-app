import streamlit as st
import yt_dlp
import os
import time

st.title("🎥 YouTube Video Downloader (with Sound)")

url = st.text_input("🔗 Enter YouTube URL:")

if st.button("Download"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
    else:
        # Create a permanent downloads folder
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)

        # Generate unique filename
        filename = f"video_{int(time.time())}.mp4"
        output_path = os.path.join(download_dir, filename)

        ydl_opts = {
            "format": "bv*+ba/b",              # best video + audio
            "outtmpl": output_path,            # output path
            "merge_output_format": "mp4",      # merge format
            "quiet": True
        }

        try:
            st.info("📥 Downloading... please wait.")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(output_path):
                st.success("✅ Download complete!")
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download to your device",
                        data=f,
                        file_name=filename,
                        mime="video/mp4"
                    )
            else:
                st.error("❌ Download failed.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
