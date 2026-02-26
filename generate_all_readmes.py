import os
import datetime
import re
from PIL import Image

# 設定
IMAGE_DIR = 'images'
ROOT_README = 'README.md'
START_MARKER = '<!-- thumbnails-start -->'
END_MARKER = '<!-- thumbnails-end -->'

def get_size_format(b):
    for unit in ["", "K", "M", "G"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024

subdir_links = []

# 1. 遍歷子目錄生成個別 README
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    # 支援格式清單（包含 SVG）
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
    
    if valid_files:
        folder_path = os.path.relpath(root, '.')
        folder_name = os.path.basename(root)
        readme_path = os.path.join(root, 'README.md')
        
        # 紀錄根目錄導覽資訊
        subdir_links.append(f"- [📁 {folder_name}]({folder_path}/README.md) ({len(valid_files)} images)")
        
        # 子目錄 README 內容
        content = [
            f"# 🖼️ {folder_name} Gallery\n",
            f"[⬅️ 回到首頁](../../{ROOT_README})\n",
            "| 預覽 | 詳細資訊 |",
            "| :--- | :--- |"
        ]
        
        for f in sorted(valid_files):
            full_path = os.path.join(root, f)
            try:
                stat = os.stat(full_path)
                size = get_size_format(stat.st_size)
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                
                # 區分 SVG (Vector) 與 一般位圖 (Pixel)
                if f.lower().endswith('.svg'):
                    w_h_info = "Vector (SVG)"
                else:
                    with Image.open(full_path) as img:
                        w, h = img.size
                        w_h_info = f"{w}x{h}"
                
                # 建立預覽與資訊
                img_tag = f'<a href="{f}"><img src="{f}" width="250" alt="{f}"></a>'
                info = f"**{f}**<br>{w_h_info} \| {size}<br>更新: {mtime}"
                content.append(f"| {img_tag} | {info} |")
            except Exception as e:
                print(f"Skipping {f} due to error: {e}")

        # 寫入子目錄 README
        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(content))

# 2. 更新根目錄 README 的導覽索引
if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f_in:
        root_text = f_in.read()
    
    nav_menu = f"{START_MARKER}\n## 📂 圖片分類導覽\n" + "\n".join(subdir_links) + f"\n{END_MARKER}"
    
    if START_MARKER in root_text:
        root_text = re.sub(f"{START_MARKER}.*?{END_MARKER}", nav_menu, root_text, flags=re.DOTALL)
    else:
        root_text += f"\n\n{nav_menu}"
        
    with open(ROOT_README, 'w', encoding='utf-8') as f_out:
        f_out.write(root_text)
