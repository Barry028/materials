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
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
    
    if valid_files:
        folder_path = os.path.relpath(root, '.')
        folder_name = os.path.basename(root)
        readme_path = os.path.join(root, 'README.md')
        
        # 紀錄根目錄導覽資訊
        subdir_links.append(f"- [📁 {folder_name}]({folder_path}/README.md) ({len(valid_files)} images)")
        
        # 子目錄 README 內容：增加「回到首頁」連結
        content = [
            f"# 🖼️ {folder_name} Gallery\n",
            f"[⬅️ 回到首頁](../../{ROOT_README})\n",
            "| 預覽 | 詳細資訊 |",
            "| :--- | :--- |"
        ]
        
        for f in sorted(valid_files):
            full_path = os.path.join(root, f)
            stat = os.stat(full_path)
            size = get_size_format(stat.st_size)
            
            # 2. 針對 SVG 處理尺寸 (SVG 是文字檔，Pillow 無法直接 open)
            if f.lower().endswith('.svg'):
                w, h = "Vector", "Vector"
            else:
                try:
                    with Image.open(full_path) as img:
                        w, h = img.size
                except:
                    w, h = "Unknown", "Unknown"
            
            # 3. 預覽標籤 (SVG 在瀏覽器會自動渲染)
            img_tag = f'<a href="{f}"><img src="{f}" width="250" alt="{f}"></a>'
            info = f"**{f}**<br>{w}x{h} | {size}"
            content.append(f"| {img_tag} | {info} |")
            except Exception as e:
                print(f"Error processing {f}: {e}")

        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(content))

# 2. 更新根目錄 README
if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f_in:
        root_text = f_in.read()
    
    # 建立分類導覽選單
    nav_menu = f"{START_MARKER}\n## 📂 圖片分類導覽\n" + "\n".join(subdir_links) + f"\n{END_MARKER}"
    
    if START_MARKER in root_text:
        root_text = re.sub(f"{START_MARKER}.*?{END_MARKER}", nav_menu, root_text, flags=re.DOTALL)
    else:
        root_text += f"\n\n{nav_menu}"
        
    with open(ROOT_README, 'w', encoding='utf-8') as f_out:
        f_out.write(root_text)
