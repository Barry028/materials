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
MAIN_WIDTH = 30 # 主導覽縮圖大小
SUB_WIDTH = 250 # 子目錄圖片寬度

def get_size_format(b):
    for unit in ["", "K", "M", "G"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

subdir_links = []

# 1. 遍歷目錄
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    folder_path = os.path.normpath(os.path.relpath(root, '.'))
    folder_name = os.path.basename(root)
    
    if folder_path == ".":
        continue

    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
    rel_url = folder_path.replace('\\', '/')
    depth = rel_url.count('/')
    
    # 樹狀縮排符號
    indent = "　" * depth + ("┗ " if depth > 0 else "📂 ")
    
    # 視覺層級：第一層粗體，其餘代碼樣式
    if depth == 0:
        display_name = f"{indent}**{folder_name}**"
    else:
        display_name = f"{indent}`{folder_name}`"

    safe_folder_url = urllib.parse.quote(rel_url)

    if valid_files:
        readme_path = os.path.join(root, 'README.md')
        rel_depth = depth + 1
        back_to_root = "../" * rel_depth
        
        # --- 修正：GitHub 相容版多圖封面 ---
        max_previews = 4 # 表格內並排 4 張較整齊
        preview_files = sorted(valid_files)[:max_previews]
        preview_imgs_html = []
        
        for pf in preview_files:
            pf_path_raw = os.path.join(folder_path, pf).replace('\\', '/')
            safe_pf_url = urllib.parse.quote(pf_path_raw)
            # 移除所有 style，僅保留 GitHub 支援的屬性
            preview_imgs_html.append(f'<img src="{safe_pf_url}" width="{MAIN_WIDTH}" height="{MAIN_WIDTH}" align="top">')
        
        # 使用 &nbsp; 代替 CSS margin 進行間隔
        img_row = "&nbsp;".join(preview_imgs_html)
        
        # 使用 <sub> 縮小字體顯示剩餘數量
        more_tag = f'<sub>(+{len(valid_files)-max_previews})</sub>' if len(valid_files) > max_previews else ""
        img_html = f'<a href="{safe_folder_url}/README.md">{img_row}</a> {more_tag}'
        
        subdir_links.append(f"| [{display_name}]({safe_folder_url}/README.md) | {img_html} | `{len(valid_files)} Items` |")

        # 生成子 README
        sub_content = [f"# 🖼️ {folder_name}\n", f"[⬅️ 返回主目錄]({back_to_root}{ROOT_README})\n", "| 預覽 | 資訊 |", "| :--- | :--- |"]
        for f in sorted(valid_files):
            safe_f = urllib.parse.quote(f)
            sub_content.append(f'| <a href="{safe_f}"><img src="{safe_f}" width="{SUB_WIDTH}"></a> | **{f}** |')
        
        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))
    else:
        if folder_name != IMAGE_DIR:
            subdir_links.append(f"| {display_name} | 📁 (資料夾) | - |")

# 2. 更新根目錄 README
if not subdir_links:
    nav_table_text = "\n目前 `images/` 中還沒有內容。\n"
else:
    tree_table = ["## 📂 素材目錄樹狀導覽\n", "| 目錄路徑 | 封面預覽 | 統計 |", "| :--- | :---: | :---: |"] + subdir_links
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
    header = "# 🎨 我的設計素材庫"
    content = f"{header}\n\n{new_nav_section}\n\n---\n*Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
