import streamlit as st
import yt_dlp
import os

# Streamlit Page Config
st.set_page_config(page_title="Video Downloader App", page_icon="🎬")

st.title("🎬 Video Downloader App")
st.write("नीचे वीडियो लिंक दर्ज करें और डाउनलोड करें:")

# URL Input
url = st.text_input("Enter Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# Download Button
if st.button("Download Video"):
    if not url:
        st.warning("कृपया पहले एक वैध URL दर्ज करें!")
    else:
        try:
            st.info("वीडियो की जानकारी और डाउनलोड तैयार किया जा रहा है... कृपया प्रतीक्षा करें।")
            
            # yt-dlp Configuration to prevent Streamlit Cloud blocking/errors
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                # Streamlit cloud blocking से बचने के लिए Headers:
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                }
            }

            os.makedirs("downloads", exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            st.success(f"सफलतापूर्वक डाउनलोड हो गया: **{info.get('title', 'Video')}**")

            # Streamlit Download Button for user
            with open(filename, "rb") as file:
                st.download_button(
                    label="⬇️ अपने डिवाइस में सेव करें",
                    data=file,
                    file_name=os.path.basename(filename),
                    mime="video/mp4"
                )

        except yt_dlp.utils.DownloadError as e:
            st.error("❌ YouTube/सर्वर द्वारा यह अनुरोध ब्लॉक कर दिया गया है या URL गलत है।")
            st.warning("सुझाव: Streamlit Cloud IP प्रतिबंधों के कारण कभी-कभी डाउनलोड फ़ेल हो जाते हैं। स्थानीय (Local machine) पर इसे चलाकर देखें।")
        except Exception as e:
            st.error(f"❌ एक अनपेक्षित एरर आई: {str(e)}")
