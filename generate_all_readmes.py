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
SUB_WIDTH = 250 # 子目錄圖片預覽寬度鎖定
REPO_NAME = os.getenv('GITHUB_REPOSITORY', '你的帳號/你的倉庫名')
BRANCH = 'main' 
IMG_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')

def get_size_format(b):
    for unit in ["", "K", "M", "G"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

subdir_links = []

# 1. 遍歷目錄 (從 IMAGE_DIR 根部開始，不跳過)
for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
    folder_path = os.path.normpath(root) # 直接使用 root
    folder_name = os.path.basename(root)
    
    # 計算相對於專案根目錄的路徑
    rel_url = folder_path.replace('\\', '/')
    # 計算深度：'images' 為 0, 'images/3Ds' 為 1
    depth = rel_url.replace(IMAGE_DIR, '').strip('/').count('/')
    if rel_url == IMAGE_DIR:
        depth = 0
    else:
        depth = rel_url.replace(IMAGE_DIR, '').strip('/').count('/') + 1

    valid_files = [f for f in files if f.lower().endswith(IMG_EXTENSIONS)]
    
    indent = "　" * depth + ("┗ " if depth > 0 else "📂 ")
    display_name = f"{indent}**{folder_name}**" if depth == 0 else f"{indent}`{folder_name}`"
    safe_folder_url = urllib.parse.quote(rel_url)

    # --- 準備生成 README ---
    readme_path = os.path.join(root, '{ROOT_README}')
    # 計算回根目錄層級：images/ 需要 ../, images/sub/ 需要 ../../
    back_depth = rel_url.count('/') + 1
    back_to_root = "../" * back_depth

    # --- 生成層級麵包屑 ---
    path_parts = rel_url.split('/')
    breadcrumb_links = [f"[🏠 主目錄]({back_to_root}{ROOT_README})"]
    for i in range(len(path_parts)):
        part_name = path_parts[i]
        if i == len(path_parts) - 1:
            breadcrumb_links.append(f"**{part_name}**")
        else:
            steps_back = len(path_parts) - 1 - i
            link_path = "../" * steps_back + "{ROOT_README}"
            breadcrumb_links.append(f"[{part_name}]({link_path})")
    breadcrumb_str = " / ".join(breadcrumb_links)

    width_lock = '<img src="https://raw.githubusercontent.com" width="250" height="1">'

    if valid_files:
        # --- 主目錄預覽邏輯 ---
        max_previews = 4
        preview_files = sorted(valid_files)[:max_previews]
        preview_imgs_html = [f'<img src="{urllib.parse.quote(os.path.join(rel_url, pf).replace("\\", "/"))}" width="{MAIN_WIDTH}" height="{MAIN_WIDTH}" align="top">' for pf in preview_files]
        img_row = "&nbsp;".join(preview_imgs_html)
        more_tag = f'<sub>(+{len(valid_files)-max_previews})</sub>' if len(valid_files) > max_previews else ""
        img_html = f'{img_row} <a href="{safe_folder_url}/{ROOT_README}">{more_tag}</a>'
        
        subdir_links.append(f"| [{display_name}]({safe_folder_url}/README.md) | {img_html} | `{len(valid_files)} Items` |")

        sub_content = [
            f"# 🖼️ 素材分類：{folder_name}\n",
            f"> {breadcrumb_str}\n",
            f"本目錄共有 `{len(valid_files)}` 個檔案\n",
            f"| 🎨 預覽 (點擊放大)<br>{width_lock} | 📋 檔案詳細資訊與連結 |",
            "| :--- | :--- |"
        ]
        
        for f in sorted(valid_files):
            f_path = os.path.join(root, f)
            safe_f = urllib.parse.quote(f)
            safe_repo = REPO_NAME.lower()
            try:
                stat = os.stat(f_path)
                size = get_size_format(stat.st_size)
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                
                if f.lower().endswith('.svg'):
                    spec = "✨ **格式:** `Vector (SVG)`"
                else:
                    with Image.open(f_path) as img:
                        w, h = img.size
                    spec = f"🖼️ **尺寸:** `{w}x{h} px`"

                cdn_url = f"https://cdn.jsdelivr.net/gh/{safe_repo}@{BRANCH}/{urllib.parse.quote(rel_url)}/{safe_f}"
                copy_md = f"![{f}]({cdn_url})"

                details = (
                    f"**📂 檔名:** `{f}`<br>"
                    f"{spec}<br>"
                    f"⚖️ **大小:** `{size}`<br>"
                    f"📅 **更新:** `{mtime}`<br><br>"
                    f"🚀 **jsDelivr Markdown:**<br>`{copy_md}`<br>"
                    f"🔗 **直接連結 (Url):**<br><code>{cdn_url}</code><br>"
                    f"📥 [檢視原始檔]({safe_f})"
                )
                
                img_tag = f'<a href="{safe_f}"><img src="{safe_f}" width="{SUB_WIDTH}" alt="{f}"></a>'
                sub_content.append(f"| {img_tag} | {details} |")
            except Exception as e:
                sub_content.append(f"| `{f}` | ⚠️ 無法讀取詳細資訊 |")
        
        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))
    else:
        # --- 處理無圖片的導覽層 (包含 images/ 根目錄) ---
        if folder_path != IMAGE_DIR:
            subdir_links.append(f"| [{display_name}]({safe_folder_url}/README.md) | 📁 (導覽層) | - |")
            
        sub_content = [
            f"# 📂 目錄：{folder_name}\n",
            f"> {breadcrumb_str}\n",
            "此目錄目前沒有直接存放圖片，請選擇下方子分類：\n",
            "### 🗂️ 子分類列表\n",
            "| 分類名稱 | 封面預覽 | 統計 |",
            "| :--- | :--- | :--- |"
        ]
        
        has_sub = False
        for d in sorted(dirs):
            if not d.startswith('.'):
                has_sub = True
                sub_dir_path = os.path.join(root, d)
                
                # 遍歷子資料夾找圖片當封面
                sub_valid_files = []
                for sub_root, _, sub_files in os.walk(sub_dir_path):
                    sub_valid_files.extend([os.path.join(sub_root, sf) for sf in sub_files if sf.lower().endswith(IMG_EXTENSIONS)])
                
                # 製作子分類的封面 HTML
                if sub_valid_files:
                    sub_preview_count = 20
                    # 取得前幾張圖的路徑並轉為 URL
                    previews = sorted(sub_valid_files)[:sub_preview_count]
                    previews_html = []
                    for p in previews:
                        # 這裡要計算相對於當前 README 的路徑
                        rel_p = os.path.relpath(p, root).replace('\\', '/')
                        previews_html.append(f'<img src="{urllib.parse.quote(rel_p)}" width="{MAIN_WIDTH}" height="{MAIN_WIDTH}" align="top">')
                    
                    sub_img_row = "&nbsp;".join(previews_html)
                    sub_count_tag = f"共 `{len(sub_valid_files)}` 張"
                else:
                    sub_img_row = "📁 *(無圖片)*"
                    sub_count_tag = "-"

                sub_content.append(f"| [📁 **{d}**]({urllib.parse.quote(d)}/README.md) | {sub_img_row} | {sub_count_tag} |")
        
        if not has_sub:
            sub_content = sub_content[:4] # 移除表格頭部
            sub_content.append("*(此目錄目前為空)*")

        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))


# 2. 更新根目錄 README
tree_table = ["## 📂 素材目錄樹狀導覽\n", "| 目錄路徑 | 封面預覽 | 統計 |", "| :--- | :---: | :---: |"] + subdir_links
nav_table_text = "\n".join(tree_table)
new_nav_section = f"{START_MARKER}\n{nav_table_text}\n{END_MARKER}"

if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f_in:
        content = f_in.read()
    content = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_nav_section, content, flags=re.DOTALL) if START_MARKER in content else content + f"\n\n{new_nav_section}"
else:
    content = f"# 🎨 素材庫\n\n{new_nav_section}"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
print("Done! All READMEs (including images/{ROOT_README}) generated.")


















