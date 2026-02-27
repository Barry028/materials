import os
import datetime
import re
import urllib.parse
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
        
        # 動態計算「回到主目錄」的層級
        rel_depth = folder_path.replace('\\', '/').count('/') + 1
        back_to_root = "../" * rel_depth
        
        # 核心修正：對路徑進行編碼以處理空格
        folder_url_raw = folder_path.replace('\\', '/')
        safe_folder_url = urllib.parse.quote(folder_url_raw)
        
        # 紀錄樹狀導覽資訊（用於根目錄）
        tree_depth = folder_path.replace('\\', '/').count('/')
        indent = "　" * tree_depth + ("┗ " if tree_depth > 0 else "📂 ")
        
        # --- 新增：生成多張縮圖封面 (最多 5 張) ---
        max_previews = 5
        preview_files = sorted(valid_files)[:max_previews]
        preview_imgs_html = []
        
        for i, pf in enumerate(preview_files):
            pf_path_raw = os.path.join(folder_path, pf).replace('\\', '/')
            safe_pf_url = urllib.parse.quote(pf_path_raw)
            # 疊加樣式：負 margin 產生重疊感，白色邊框區隔
            overlap = 'margin-left: -15px;' if i > 0 else ''
            style = f'width="40" height="40" style="border-radius:50%; border:2px solid #fff; object-fit:cover; {overlap} box-shadow: 1px 1px 3px rgba(0,0,0,0.1);"'
            preview_imgs_html.append(f'<img src="{safe_pf_url}" {style}>')
        
        more_tag = f'<span style="font-size:12px; color:#666; margin-left:8px; vertical-align:middle;">+{len(valid_files)-max_previews}</span>' if len(valid_files) > max_previews else ""
        img_html = f'<a href="{safe_folder_url}/README.md" style="text-decoration:none; white-space:nowrap;">' + "".join(preview_imgs_html) + f'{more_tag}</a>'
        
        subdir_links.append(f"| [{indent}{folder_name}]({safe_folder_url}/README.md) | {img_html} | `{len(valid_files)} Items` |")
        
        # 生成子目錄 README
        sub_content = [
            f"# 🖼️ {folder_name} 素材庫\n",
            f"[⬅️ 返回主目錄]({back_to_root}{ROOT_README})\n",
            "| 預覽 (點擊放大) | 檔案資訊 |",
            "| :--- | :--- |"
        ]
        
        for f in sorted(valid_files):
            f_path = os.path.join(root, f)
            try:
                stat = os.stat(f_path)
                size = get_size_format(stat.st_size)
                safe_file_url = urllib.parse.quote(f)
                
                if f.lower().endswith('.svg'):
                    info_text = f"Vector (SVG) | {size}"
                else:
                    with Image.open(f_path) as img:
                        w, h = img.size
                        info_text = f"{w}x{h} | {size}"
                
                sub_content.append(f'| <a href="{safe_file_url}"><img src="{safe_file_url}" width="250"></a> | **{f}**<br>{info_text} |')
            except:
                continue

        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))

# 2. 生成或更新根目錄 README
if not subdir_links:
    nav_table_text = "\n目前 `images/` 資料夾中還沒有圖片，請上傳圖片至子目錄後再執行。\n"
else:
    tree_table = [
        "## 📂 素材目錄樹狀導覽\n",
        "| 目錄路徑 | 封面預覽 | 統計 |",
        "| :--- | :---: | :---: |"
    ] + subdir_links
    nav_table_text = "\n".join(tree_table)

new_nav_section = f"{START_MARKER}\n{nav_table_text}\n{END_MARKER}"

if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f_in:
        content = f_in.read()
    if START_MARKER in content:
        content = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_nav_section, content, flags=re.DOTALL)
    else:
        content += f"\n\n{new_nav_section}"
else:
    header = "# 🎨 我的設計素材庫\n這是一個全自動更新的素材導覽系統。"
    content = f"{header}\n\n{new_nav_section}\n\n---\n*Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
print(f"Successfully processed {ROOT_README}")
