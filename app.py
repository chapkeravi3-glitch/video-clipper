import os
import json
import re
import subprocess
import streamlit as st
import yt_dlp
import whisper
import google.generativeai as genai

st.set_page_config(page_title="Kixy AI Free Alternative", page_icon="🎬", layout="centered")

st.title("🎬 Free AI Video Clipper (Shorts Generator)")

# Input for Gemini API Key & YouTube URL
api_key = st.text_input("Gemini API Key डेलें:", type="password")
youtube_url = st.text_input("YouTube वीडियो का लिंक डेलें:")

if st.button("🚀 क्लिप बनाना शुरू करें"):
    if not api_key or not youtube_url:
        st.warning("कृपया API Key और YouTube लिंक दोनों भरें!")
    else:
        genai.configure(api_key=api_key)
        
        # 1. Download Video
        st.info("📥 वीडियो डाउनलोड हो रहा है...")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'input_video.mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        st.success("✅ वीडियो डाउनलोड हो गया!")
        
        # 2. Transcribe with Whisper
        st.info("🎙️ AI वॉइस को टेक्स्ट और टाइमस्टैम्प में बदल रहा है...")
        model = whisper.load_model("base")
        result = model.transcribe("input_video.mp4", word_timestamps=True)
        
        srt_content = ""
        for i, segment in enumerate(result['segments'], start=1):
            start_s, end_s = segment['start'], segment['end']
            # Format time for SRT
            def fmt(sec):
                h, m, s = int(sec//3600), int((sec%3600)//60), int(sec%60)
                ms = int((sec%1)*1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"
            srt_content += f"{i}\n{fmt(start_s)} --> {fmt(end_s)}\n{segment['text'].strip()}\n\n"
            
        with open("subtitles.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
            
        # 3. Find Highlights with Gemini
        st.info("🧠 Gemini AI वायरल हाइलाइट्स ढूंढ रहा है...")
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Analyze this transcript and find the top 5 most interesting/viral moments.
        Each clip should be 30 to 50 seconds long.
        Return ONLY a valid JSON array of objects with keys "start" (seconds as float), "end" (seconds as float), and "title".
        No markdown formatting, just raw JSON.
        Transcript: {result['text'][:15000]}
        """
        response = gemini_model.generate_content(prompt)
        clean_json = re.sub(r'```json|```', '', response.text).strip()
        clips_data = json.loads(clean_json)
        
        # 4. Cut Clips using FFmpeg
        os.makedirs("output_clips", exist_ok=True)
        st.info("✂️ वर्टिकल (9:16) क्लिप्स और सबटाइटल काटे जा रहे हैं...")
        
        for idx, clip in enumerate(clips_data, start=1):
            start, duration = clip["start"], clip["end"] - clip["start"]
            out_file = f"output_clips/clip_{idx}.mp4"
            
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-ss', str(start), '-i', 'input_video.mp4', '-t', str(duration),
                '-vf', "crop=ih*(9/16):ih,subtitles=subtitles.srt:force_style='FontSize=16,PrimaryColour=&H00FFFF&,Alignment=2'",
                '-c:v', 'libx264', '-c:a', 'aac', out_file
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Show on Streamlit UI
            st.write(f"✨ **{clip.get('title', f'Clip {idx}')}**")
            st.video(out_file)
            
        st.success("🎉 सभी क्लिप्स तैयार हैं!")
