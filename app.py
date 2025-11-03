import streamlit as st
import yt_dlp
import os
import tempfile
import glob
import shutil
import math

st.set_page_config(page_title="YouTube Downloader (Best-first)", page_icon="🎬")
st.title("🎬 YouTube Downloader — Best-quality prioritized")

# ---------- Helpers & state ----------
if "formats" not in st.session_state:
    st.session_state.formats = []
if "info" not in st.session_state:
    st.session_state.info = None
if "status" not in st.session_state:
    st.session_state.status = ""
if "progress" not in st.session_state:
    st.session_state.progress = 0

progress_bar = st.progress(0)
status_box = st.empty()

def progress_hook(d):
    status = d.get("status")
    if status == "downloading":
        # percent string like "23.4%"
        pct = d.get("_percent_str") or d.get("percent")
        if isinstance(pct, str):
            try:
                val = float(pct.replace("%", ""))
                st.session_state.progress = int(min(max(val, 0), 100))
                progress_bar.progress(st.session_state.progress)
                st.session_state.status = f"⬇️ Downloading... {pct}"
            except Exception:
                st.session_state.status = f"⬇️ Downloading... {pct}"
        else:
            st.session_state.status = "⬇️ Downloading..."
    elif status == "finished":
        st.session_state.status = "🔁 Download finished; processing..."
        progress_bar.progress(100)
    status_box.info(st.session_state.status)

def human_size(bytesize):
    if not bytesize:
        return "—"
    for unit in ['B','KB','MB','GB','TB']:
        if bytesize < 1024:
            return f"{bytesize:.1f}{unit}"
        bytesize /= 1024
    return f"{bytesize:.1f}PB"

# ---------- UI: input + confirm ----------
url = st.text_input("Enter YouTube video URL:")

col1, col2 = st.columns([1,1])
with col1:
    confirm = st.button("✅ Confirm")
with col2:
    refresh = st.button("🔄 Refresh formats (if already fetched)")

# ---------- Fetch formats on Confirm ----------
if confirm or refresh:
    if not url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        st.session_state.status = "🔍 Fetching available formats..."
        status_box.info(st.session_state.status)
        progress_bar.progress(0)
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            st.session_state.info = info

            formats = []
            for f in info.get("formats", []):
                # only include formats that actually exist (filter nothing out here)
                filesize = f.get("filesize") or f.get("filesize_approx")
                height = f.get("height")
                resolution = f.get("resolution") or (f"{height}p" if height else "audio")
                vcodec = f.get("vcodec")
                acodec = f.get("acodec")
                ftype = ("Muxed" if vcodec != "none" and acodec != "none"
                         else "Video-only" if vcodec != "none"
                         else "Audio-only")
                formats.append({
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": resolution,
                    "height": height or 0,
                    "fps": f.get("fps") or "",
                    "filesize": filesize,
                    "vcodec": vcodec,
                    "acodec": acodec,
                    "type": ftype,
                    "note": f.get("format_note") or "",
                })

            # Sort by type and height descending, so best muxed first, then best video-only, etc.
            st.session_state.formats = sorted(
                formats,
                key=lambda x: (0 if x["type"] == "Muxed" else 1 if x["type"]=="Video-only" else 2, - (x["height"] or 0))
            )
            st.success("✅ Formats fetched. See categories below.")
        except Exception as e:
            st.error(f"Failed to fetch formats: {e}")
            st.session_state.formats = []

# ---------- Show categories and recommended best ----------
if st.session_state.formats:
    info = st.session_state.info or {}
    title = info.get("title", "video")
    st.markdown(f"### 📌 Video: **{title}**")

    # Identify best muxed first (highest resolution)
    muxed = [f for f in st.session_state.formats if f["type"] == "Muxed"]
    video_only = [f for f in st.session_state.formats if f["type"] == "Video-only"]
    audio_only = [f for f in st.session_state.formats if f["type"] == "Audio-only"]

    # Recommended best: highest resolution muxed if exist,
    # otherwise highest video-only + best audio will be used automatically on download
    recommended = None
    if muxed:
        recommended = sorted(muxed, key=lambda x: x["height"] or 0, reverse=True)[0]
    else:
        # pick highest video-only if any
        if video_only:
            recommended = sorted(video_only, key=lambda x: x["height"] or 0, reverse=True)[0]

    st.markdown("#### 🔝 Recommended (priority: best merged).")
    if recommended:
        rec_label = f"{recommended['resolution']} • {recommended['type']} • {recommended['ext']} • {human_size(recommended['filesize'])}"
        st.info(f"**Recommended:** {rec_label}")
    else:
        st.info("No recommended format found.")

    # Show categories
    def show_category(name, items):
        if not items:
            return
        st.markdown(f"#### {name} ({len(items)})")
        for i, it in enumerate(items):
            note = f" — {it['note']}" if it['note'] else ""
            st.write(f"{i+1}. {it['resolution']} • {it['ext']} • {it['type']} • {human_size(it['filesize'])}{note}")

    show_category("Muxed (video + audio)", muxed)
    show_category("Video-only", video_only)
    show_category("Audio-only", audio_only)

    # Format selection (all formats)
    options = [
        f"{f['format_id']} — {f['resolution']} • {f['type']} • {f['ext']} • {human_size(f['filesize'])}"
        for f in st.session_state.formats
    ]
    selected_idx = st.selectbox("Choose a specific format (optional) — otherwise recommended will be used", range(len(options)), format_func=lambda i: options[i])
    chosen = st.session_state.formats[selected_idx]

    # Download logic
    if st.button("⬇️ Download Now (use recommended if none selected)"):
        # Determine target format: chosen if user explicitly picked else recommended
        target = chosen or recommended
        if not target:
            st.error("No format selected and no recommended format found.")
        else:
            st.session_state.status = "Starting download..."
            status_box.info(st.session_state.status)
            progress_bar.progress(0)

            with tempfile.TemporaryDirectory() as tmpdir:
                ffmpeg_path = shutil.which("ffmpeg")
                prefer_merge = (ffmpeg_path is not None)

                # Build format expression
                fmt_id = target["format_id"]
                # If target is Video-only and ffmpeg available, request merging with best audio:
                if target["type"] == "Video-only" and prefer_merge:
                    format_expr = f"{fmt_id}+bestaudio/best"
                else:
                    # for muxed or audio-only or video-only without ffmpeg, just request the format id
                    format_expr = fmt_id

                outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")

                ydl_opts = {
                    "format": format_expr,
                    "outtmpl": outtmpl,
                    "progress_hooks": [progress_hook],
                    "quiet": True,
                }
                # If ffmpeg available and merging desired, instruct yt-dlp to merge
                if prefer_merge:
                    ydl_opts.update({
                        "merge_output_format": "mp4",
                        "ffmpeg_location": ffmpeg_path,
                        "postprocessors": [{"key": "FFmpegMerger"}]
                    })

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        # gather created files
                        files = glob.glob(os.path.join(tmpdir, "*"))
                        # Prefer mp4 merged if exists
                        mp4s = [f for f in files if f.lower().endswith(".mp4")]
                        audios = [f for f in files if f.lower().endswith((".m4a", ".mp3", ".webm", ".opus"))]
                        videos = [f for f in files if f.lower().endswith((".mp4", ".webm")) and f not in mp4s]

                        # If merged mp4 exists -> offer single download
                        if mp4s:
                            final = mp4s[0]
                            with open(final, "rb") as fh:
                                st.success("✅ Merged (video+audio) ready.")
                                st.download_button("📥 Download MP4 (with audio)", fh, os.path.basename(final), mime="video/mp4")
                        else:
                            # No merged file: if we have both video and audio -> offer both together
                            if videos and audios:
                                st.warning("⚠️ Could not merge server-side (FFmpeg not available). Providing video and audio files.")
                                # Present both download buttons together (single step)
                                with open(videos[0], "rb") as vf, open(audios[0], "rb") as af:
                                    colv, cola = st.columns(2)
                                    with colv:
                                        st.download_button("📥 Download Video Only", vf, os.path.basename(videos[0]), mime="video/mp4")
                                    with cola:
                                        st.download_button("📥 Download Audio", af, os.path.basename(audios[0]), mime="audio/mp4")
                            elif videos:
                                # only video file found
                                with open(videos[0], "rb") as vf:
                                    st.download_button("📥 Download Video", vf, os.path.basename(videos[0]), mime="video/mp4")
                            elif audios:
                                with open(audios[0], "rb") as af:
                                    st.download_button("📥 Download Audio", af, os.path.basename(audios[0]), mime="audio/mp4")
                            else:
                                st.error("❌ No downloadable files found after yt-dlp run.")
                except Exception as e:
                    st.error(f"Download failed: {e}")

# show live status
if st.session_state.status:
    status_box.info(st.session_state.status)
