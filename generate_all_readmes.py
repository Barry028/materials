import os
import datetime
import re
from PIL import Image

IMAGE_DIR = 'images'
ROOT_README = 'README.md'
START_MARKER = '<!-- thumbnails-start -->'
END_MARKER = '<!-- thumbnails-end -->'

def get_size_format(b):
    for unit in ["", "K", "M", "G"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024

subdir_links = []

# 1. 遍歷所有子目錄生成各別 README
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    if valid_files:
        folder_path = os.path.relpath(root, '.')
        folder_name = os.path.basename(root)
        readme_path = os.path.join(root, 'README.md')
        
        # 紀錄給根目錄導覽使用
        subdir_links.append(f"- [📁 {folder_name}]({folder_path}/README.md) ({len(valid_files)} images)")
        
        # 建立子目錄圖庫內容
        content = [f"# 🖼️ {folder_name} Gallery\n", "| 預覽 | 詳細資訊 |", "| :--- | :--- |"]
        for f in sorted(valid_files):
            full_path = os.path.join(root, f)
            stat = os.stat(full_path)
            with Image.open(full_path) as img:
                w, h = img.size
            
            img_tag = f'<a href="{f}"><img src="{f}" width="250"></a>'
            info = f"**{f}**<br>{w}x{h} | {get_size_format(stat.st_size)}"
            content.append(f"| {img_tag} | {info} |")

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

# 2. 更新根目錄 README 的導覽選單
if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f:
        root_text = f.read()
    
    nav_menu = f"{START_MARKER}\n### 📂 分類導覽\n" + "\n".join(subdir_links) + f"\n{END_MARKER}"
    
    if START_MARKER in root_text:
        root_text = re.sub(f"{START_MARKER}.*?{END_MARKER}", nav_menu, root_text, flags=re.DOTALL)
    else:
        root_text += f"\n\n{nav_menu}"
        
    with open(ROOT_README, 'w', encoding='utf-8') as f:
        f.write(root_text)
