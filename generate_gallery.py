import os
import datetime
import re
from PIL import Image

# 設定
IMAGE_DIR = 'images'
README_FILE = 'README.md'
START_MARKER = '<!-- thumbnails-start -->'
END_MARKER = '<!-- thumbnails-end -->'

def get_size_format(b):
    for unit in ["", "K", "M", "G"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024

content = []
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    folder_name = os.path.basename(root)
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    if folder_name and valid_files:
        content.append(f"\n### 📁 {folder_name.capitalize()}\n")
        content.append("| 預覽 (點擊放大) | 檔案詳細資訊 |")
        content.append("| :--- | :--- |")
        
        for f in sorted(valid_files):
            path = os.path.join(root, f)
            stat = os.stat(path)
            size = get_size_format(stat.st_size)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
            
            with Image.open(path) as img:
                w, h = img.size
            
            # 建立帶連結的圖片標籤與資訊
            img_tag = f'<a href="{path}"><img src="{path}" width="200" alt="{f}"></a>'
            info = f"**檔名:** `{f}`<br>**尺寸:** {w}x{h}<br>**大小:** {size}<br>**更新:** {mtime}"
            content.append(f"| {img_tag} | {info} |")

# 讀取並替換 README
with open(README_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

new_section = f"{START_MARKER}\n" + "\n".join(content) + f"\n{END_MARKER}"
text = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_section, text, flags=re.DOTALL)

with open(README_FILE, 'w', encoding='utf-8') as f:
    f.write(text)
