import streamlit as st
import yt_dlp
import os
import glob
from yt_dlp.networking.impersonate import ImpersonateTarget

# 設定環境變數與下載路徑
os.environ["NODE_PATH"] = "/usr/local/lib/node_modules"
DOWNLOAD_PATH = "./downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

st.set_page_config(page_title="YouTube 便利下載器", page_icon="🎥")
st.title("🎥 YouTube 影音便利下載器 (Streamlit 雲端版)")

url = st.text_input("請輸入 YouTube 網址", placeholder="https://www.youtube.com/...")

col1, col2 = st.columns(2)
with col1:
    quality_choice = st.selectbox("請選擇畫質", ["1080p", "720p", "480p", "360p", "最佳畫質"], index=4)
with col2:
    format_choice = st.selectbox("請選擇下載格式", ["MP4", "WEBM", "M4A(純音訊)", "MP3(需FFmpeg)"])

if st.button("開始下載", type="primary"):
    if not url:
        st.warning("請先輸入網址！")
    else:
        with st.spinner("影片下載與轉檔中，請稍候..."):
            # 下載前清空暫存，避免雲端空間爆滿
            for f in glob.glob(f"{DOWNLOAD_PATH}/*"):
                try:
                    os.remove(f)
                except:
                    pass

            quality_map = {
                "1080p": "1080", "720p": "720", "480p": "480", 
                "360p": "360", "最佳畫質": "best"
            }
            
            out_tmpl = f"{DOWNLOAD_PATH}/%(title)s.%(ext)s"
            
            ydl_opts = {
                "outtmpl": out_tmpl,
                "impersonate": ImpersonateTarget(client="chrome"),
                "extractor_args": {"youtube": {"player_client": ["ios", "android"]}}
            }
            
            if format_choice == "MP4":
                if quality_map[quality_choice] == "best":
                    format_code = "bestvideo+bestaudio/best"
                else:
                    format_code = f"bestvideo[height<={quality_map[quality_choice]}]+bestaudio/best[height<={quality_map[quality_choice]}]/best"
                ydl_opts["format"] = format_code
                ydl_opts["merge_output_format"] = "mp4"
                
            elif format_choice == "WEBM":
                if quality_map[quality_choice] == "best":
                    format_code = "best[ext=webm]"
                else:
                    format_code = f"best[ext=webm][height<={quality_map[quality_choice]}]"
                ydl_opts["format"] = format_code
                
            elif format_choice == "M4A(純音訊)":
                ydl_opts["format"] = "bestaudio[ext=m4a]"
                
            elif format_choice == "MP3(需FFmpeg)":
                ydl_opts["format"] = "bestaudio"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                downloaded_files = glob.glob(f"{DOWNLOAD_PATH}/*")
                if downloaded_files:
                    file_path = downloaded_files[0]
                    file_name = os.path.basename(file_path)
                    
                    st.success("✅ 下載成功！")
                    # 提供網頁下載按鈕，直接存入個人裝置
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"💾 點此儲存檔案：{file_name}",
                            data=file,
                            file_name=file_name,
                            mime="application/octet-stream"
                        )
                else:
                    st.error("檔案下載失敗，找不到輸出檔案")
                    
            except Exception as e:
                st.error(f"下載過程中發生錯誤：{str(e)}")
