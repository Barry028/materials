import os
import datetime
from PIL import Image

IMAGE_DIR = 'images'
README_FILE = 'README.md'
START_MARKER = '<!-- thumbnails-start -->'
END_MARKER = '<!-- thumbnails-end -->'

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G"]:
        if b < factor: return f"{b:.2f}{unit}{suffix}"
        b /= factor

content = []
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    folder_name = os.path.basename(root)
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if folder_name and valid_files:
        content.append(f"\n### 📁 {folder_name.capitalize()}\n")
        # 使用表格格式讓資訊整齊排列在圖片右側
        content.append("| 預覽 | 檔案詳細資訊 |")
        content.append("| :--- | :--- |")
        
        for f in sorted(valid_files):
            path = os.path.join(root, f)
            stat = os.stat(path)
            
            # 獲取資訊
            size = get_size_format(stat.st_size)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
            with Image.open(path) as img:
                width, height = img.size
            
            # 組裝 Markdown 行 (圖片 | 資訊)
            img_tag = f'<img src="{path}" width="200" alt="{f}">'
            info = f"**檔名:** `{f}`<br>**尺寸:** {width}x{height}<br>**大小:** {size}<br>**更新:** {mtime}"
            content.append(f"| {img_tag} | {info} |")

# 讀取並替換 README 內容
with open(README_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

import re
new_content = f"{START_MARKER}\n" + "\n".join(content) + f"\n{END_MARKER}"
text = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_content, text, flags=re.DOTALL)

with open(README_FILE, 'w', encoding='utf-8') as f:
    f.write(text)
