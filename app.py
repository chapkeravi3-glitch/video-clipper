import streamlit as st
import os
import yt_dlp

# Page configuration
st.set_page_config(page_title="AI Shorts Cutter", page_icon="✂️", layout="wide")

st.title("🎬 AI Shorts & Reels Auto-Cutter")
st.write("यह ऐप YouTube लिंक से वीडियो डाउनलोड करके शॉर्ट्स क्लिप्स बनाएगा।")

# Safe import check for moviepy
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except Exception as e:
    MOVIEPY_AVAILABLE = False

# Input Section
url = st.text_input("YouTube Video URL दर्ज करें:")

if st.button("वीडियो प्रोसेस करें"):
    if not url:
        st.warning("कृपया वैध YouTube लिंक दर्ज करें!")
    elif not MOVIEPY_AVAILABLE:
        st.error("MoviePy लाइब्रेरी लोड नहीं हो पाई है। कृपया सुनिश्चित करें कि requirements.txt में सही वर्ज़न्स हैं।")
    else:
        with st.spinner("YouTube से वीडियो डाउनलोड किया जा रहा है... कृपया प्रतीक्षा करें।"):
            try:
                ydl_opts = {
                    'format': 'best[height<=720]',
                    'outtmpl': 'source_video.mp4',
                    'noplaylist': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                video_path = 'source_video.mp4'
                
                if os.path.exists(video_path):
                    clip = VideoFileClip(video_path)
                    st.success(f"वीडियो सफलतापूर्वक लोड हो गया! कुल अवधि: {int(clip.duration)} सेकंड")
                    st.video(video_path)
                    
                    # आगे क्लिप काटने और वर्टिकल क्रॉप करने का लॉजिक यहाँ जुड़ेगा
                else:
                    st.error("वीडियो डाउनलोड नहीं हो पाया।")
                    
            except Exception as e:
                st.error(f"प्रोसेसिंग के दौरान एरर आया: {str(e)}")
