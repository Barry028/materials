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

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

subdir_links = []

# 1. 遍歷目錄
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    folder_path = os.path.normpath(os.path.relpath(root, '.'))
    folder_name = os.path.basename(root)
    
    # 略過根目錄自身
    if folder_path == ".":
        continue

    # 檢查是否有圖片
    valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
    
    # 計算樹狀縮排與字體大小
    rel_url = folder_path.replace('\\', '/')
    depth = rel_url.count('/')
    
    # 字體大小邏輯：第一層 size=4，之後每深一層減 1，最小為 1
    f_size = max(1, 4 - depth)
    indent = "　" * depth + ("┗ " if depth > 0 else "📂 ")
    
    # 第一層加粗，其餘正常
    bold_s, bold_e = ("**", "**") if depth == 0 else ("", "")
    
    # 組合美化後的顯示名稱
    display_name = f'<font size="{f_size}">{indent}{bold_s}{folder_name}{bold_e}</font>'
    safe_folder_url = urllib.parse.quote(rel_url)

    if valid_files:
        # --- 有圖片：生成 README 並顯示多圖封面 ---
        readme_path = os.path.join(root, 'README.md')
        rel_depth = depth + 1
        back_to_root = "../" * rel_depth
        
        # 多圖封面 (Avatar Stack 效果)
        max_previews = 5
        preview_files = sorted(valid_files)[:max_previews]
        preview_imgs_html = []
        for i, pf in enumerate(preview_files):
            pf_path_raw = os.path.join(folder_path, pf).replace('\\', '/')
            safe_pf_url = urllib.parse.quote(pf_path_raw)
            overlap = 'margin-left: -15px;' if i > 0 else ''
            style = f'width="40" height="40" style="border-radius:50%; border:2px solid #fff; object-fit:cover; {overlap} box-shadow: 1px 1px 3px rgba(0,0,0,0.1);"'
            preview_imgs_html.append(f'<img src="{safe_pf_url}" {style}>')
        
        more_tag = f'<span style="font-size:12px; color:#666; margin-left:8px;">+{len(valid_files)-max_previews}</span>' if len(valid_files) > max_previews else ""
        img_html = f'<a href="{safe_folder_url}/README.md" style="white-space:nowrap;">' + "".join(preview_imgs_html) + f'{more_tag}</a>'
        
        # 加入連結
        subdir_links.append(f"| [{display_name}]({safe_folder_url}/README.md) | {img_html} | `{len(valid_files)} Items` |")

        # 生成子 README
        sub_content = [f"# 🖼️ {folder_name}\n", f"[⬅️ 返回主目錄]({back_to_root}{ROOT_README})\n", "| 預覽 | 資訊 |", "| :--- | :--- |"]
        for f in sorted(valid_files):
            safe_f = urllib.parse.quote(f)
            sub_content.append(f'| <a href="{safe_f}"><img src="{safe_f}" width="250"></a> | **{f}** |')
        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))
    else:
        # --- 沒圖片 (父資料夾)：保留樹狀結構，僅顯示文字 ---
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
    content = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_nav_section, content, flags=re.DOTALL) if START_MARKER in content else content + f"\n\n{new_nav_section}"
else:
    header = "# 🎨 我的設計素材庫"
    content = f"{header}\n\n{new_nav_section}\n\n---\n*Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
print(f"Successfully processed {ROOT_README}")
