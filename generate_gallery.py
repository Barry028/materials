import os

IMAGE_DIR = 'images'
README_FILE = 'README.md'
START_MARKER = '<!-- thumbnails-start -->'
END_MARKER = '<!-- thumbnails-end -->'

content = []
# 遍歷子目錄
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    level = root.replace(IMAGE_DIR, '').count(os.sep)
    indent = ' ' * 4 * (level)
    folder_name = os.path.basename(root)
    
    if folder_name and any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) for f in files):
        content.append(f"\n### {folder_name.capitalize()}\n")
        
        for f in sorted(files):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                img_path = os.path.join(root, f)
                # 垂直條列格式：縮圖 + 檔名
                content.append(f"- ![{f}]({img_path})  \n  `{f}`\n")

# 更新 README
with open(README_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

new_content = f"{START_MARKER}\n{''.join(content)}\n{END_MARKER}"
import re
text = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_content, text, flags=re.DOTALL)

with open(README_FILE, 'w', encoding='utf-8') as f:
    f.write(text)
