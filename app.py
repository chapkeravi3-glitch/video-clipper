import streamlit as st
import os
import yt_dlp
from moviepy.editor import VideoFileClip

# Page Config
st.set_page_config(page_title="AI Shorts Auto-Cutter & Editor", page_icon="✂️", layout="wide")

st.title("🎬 AI Shorts & Reels Auto-Cutter & Editor")
st.write("यह ऐप लंबी वीडियो या YouTube लिंक को स्वचालित रूप से **9:16 वर्टिकल शॉर्ट्स** में काटता और एडिट करता है।")

# 1. Video Source Selection
source_type = st.radio("वीडियो का स्रोत चुनें:", ["YouTube Link", "Upload Video File"])
video_path = None

if source_type == "YouTube Link":
    url = st.text_input("YouTube Video URL दर्ज करें:")
    if st.button("वीडियो डाउनलोड करें") and url:
        with st.spinner("YouTube से वीडियो डाउनलोड हो रहा है... कृपया प्रतीक्षा करें।"):
            try:
                ydl_opts = {
                    'format': 'best[height<=720]',
                    'outtmpl': 'source_video.mp4',
                    'noplaylist': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                video_path = 'source_video.mp4'
                st.success("वीडियो सफलतापूर्वक डाउनलोड हो गया!")
            except Exception as e:
                st.error(f"डाउनलोड एरर: {str(e)}")

else:
    uploaded_file = st.file_uploader("अपनी वीडियो फ़ाइल अपलोड करें (MP4)", type=["mp4", "mov", "mkv"])
    if uploaded_file is not None:
        video_path = "source_uploaded.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("फ़ाइल सफलतापूर्वक अपलोड हो गई!")

# 2. Video Editing & Auto-Clipping Section
if video_path and os.path.exists(video_path):
    st.divider()
    st.subheader("⚙️ ऑटोमैटिक शॉर्ट्स सेटिंग्स")
    
    st.video(video_path)
    
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        st.info(f"कुल वीडियो अवधि: {int(duration)} सेकंड ({int(duration/60)} मिनट)")
        
        # Clip duration selection (e.g., 30 seconds per short)
        clip_duration = st.slider("प्रत्येक शॉर्ट क्लिप की लंबाई (सेकंड में):", min_value=15, max_value=60, value=30)
        
        if st.button("🚀 शॉर्ट्स काटें और एडिट करें"):
            os.makedirs("output_shorts", exist_ok=True)
            
            with st.spinner("वीडियो को वर्टिकल (9:16) फॉर्मेट में क्रॉप और एडिट किया जा रहा है..."):
                w, h = clip.size
                
                # 9:16 आस्पेक्ट रेश्यो के लिए सेंटर क्रॉप कैलकुलेशन
                target_w = int(h * (9 / 16))
                if target_w > w:
                    target_w = w
                    target_h = int(w * (16 / 9))
                else:
                    target_h = h
                    
                x1 = (w - target_w) // 2
                y1 = (h - target_h) // 2
                
                start = 0
                clip_count = 1
                
                # लूप चलाकर वीडियो को टुकड़ों में बांटना और वर्टिकल क्रॉप करना
                while start < duration:
                    end = min(start + clip_duration, duration)
                    
                    if (end - start) < 5 and clip_count > 1:
                        break
                        
                    subclip = clip.subclip(start, end)
                    # 9:16 वर्टिकल क्रॉप अप्लाई करना
                    cropped_clip = subclip.crop(x1=x1, y1=y1, x2=x1+target_w, y2=y1+target_h)
                    
                    output_file = f"output_shorts/short_{clip_count}.mp4"
                    cropped_clip.write_videofile(
                        output_file, 
                        codec="libx264", 
                        audio_codec="aac", 
                        preset="ultrafast", 
                        fps=24,
                        logger=None
                    )
                    
                    clip_count += 1
                    start += clip_duration
                    
            st.success(f"शानदार! कुल {clip_count - 1} शॉर्ट्स क्लिप्स बनकर तैयार हैं!")
            
            # 3. Display and Download Generated Shorts
            st.subheader("📥 आपके तैयार किए गए शॉर्ट्स:")
            for f_name in os.listdir("output_shorts"):
                if f_name.endswith(".mp4"):
                    f_path = os.path.join("output_shorts", f_name)
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.video(f_path)
                    with col2:
                        st.write(f"**{f_name}**")
                        with open(f_path, "rb") as file_data:
                            st.download_button(
                                label=f"डाउनलोड करें",
                                data=file_data,
                                file_name=f_name,
                                mime="video/mp4",
                                key=f_path
                            )
                            
    except Exception as e:
        st.error(f"वीडियो प्रोसेसिंग में त्रुटि: {str(e)}")
