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

# 確保圖片目錄存在
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

subdir_links = []

# 1. 遍歷子目錄生成個別 README
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
    
    if valid_files:
        folder_path = os.path.normpath(os.path.relpath(root, '.'))
        folder_name = os.path.basename(root)
        readme_path = os.path.join(root, 'README.md')
        
        # 紀錄樹狀導覽資訊
        depth = folder_path.count(os.sep) + 1 
        back_prefix = "../" * depth
        indent = "　" * depth + ("┗ " if depth > 0 else "📂 ")
        cover_file = sorted(valid_files)[0]
        cover_url = os.path.join(folder_path, cover_file).replace('\\', '/')
        
        # 製作圓形封面 HTML
        img_style = 'width="45" height="45" style="border-radius:50%; border:2px solid #eee; object-fit:cover;"'
        img_html = f'<a href="{folder_path}/README.md"><img src="{cover_url}" {img_style}></a>'
        
        subdir_links.append(f"| [{indent}{folder_name}]({folder_path}/README.md) | {img_html} | `{len(valid_files)} Items` |")
        
        # 子目錄 README：含「回到首頁」
        sub_content = [
            f"# 🖼️ {folder_name} 素材庫\n",
            f"[⬅️ 返回主目錄]({back_prefix}{ROOT_README})\n", # 動態路徑修正
            "| 預覽 (點擊放大) | 檔案資訊 |",
            "| :--- | :--- |"
        ]
        
        for f in sorted(valid_files):
            f_path = os.path.join(root, f)
            try:
                stat = os.stat(f_path)
                size = get_size_format(stat.st_size)
                if f.lower().endswith('.svg'):
                    info_text = f"Vector (SVG) | {size}"
                else:
                    with Image.open(f_path) as img:
                        w, h = img.size
                        info_text = f"{w}x{h} | {size}"
                
                sub_content.append(f'| <a href="{f}"><img src="{f}" width="250"></a> | **{f}**<br>{info_text} |')
            except:
                continue

        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))

# 2. 生成或更新根目錄 README
default_header = "# 🎨 我的自動化設計素材庫\n這是一個透過 **GitHub Actions** 自動生成的圖庫系統。只需上傳圖片至 `images/` 資料夾即可自動更新。\n"
tree_table = [
    "## 📂 素材目錄樹狀導覽\n",
    "| 目錄路徑 | 封面 | 統計 |",
    "| :--- | :---: | :---: |"
] + subdir_links

new_nav_section = f"{START_MARKER}\n" + "\n".join(tree_table) + f"\n{END_MARKER}"

if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f_in:
        content = f_in.read()
    if START_MARKER in content:
        content = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_nav_section, content, flags=re.DOTALL)
    else:
        content += f"\n\n{new_nav_section}"
else:
    content = f"{default_header}\n\n{new_nav_section}\n\n---\n*最後更新於: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
