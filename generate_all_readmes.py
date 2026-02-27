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
SUB_WIDTH = 250 # 子目錄圖片預覽寬度
# 自動抓取 GitHub 倉庫名稱，若在本機執行請修改預設值
REPO_NAME = os.getenv('GITHUB_REPOSITORY', '你的帳號/你的倉庫名')
BRANCH = 'main' # 確保這是您的主分支名稱

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
        
        # --- 主目錄封面預覽 (並排縮圖) ---
        max_previews = 4
        preview_files = sorted(valid_files)[:max_previews]
        preview_imgs_html = [f'<img src="{urllib.parse.quote(os.path.join(folder_path, pf).replace("\\", "/"))}" width="{MAIN_WIDTH}" height="{MAIN_WIDTH}" align="top">' for pf in preview_files]
        img_row = "&nbsp;".join(preview_imgs_html)
        more_tag = f'<sub>(+{len(valid_files)-max_previews})</sub>' if len(valid_files) > max_previews else ""
        img_html = f'{img_row} <a href="{safe_folder_url}/README.md">{more_tag}</a>'
        
        subdir_links.append(f"| [{display_name}]({safe_folder_url}/README.md) | {img_html} | `{len(valid_files)} Items` |")

        # --- 💡 強化版：動態生成完整層級麵包屑 ---
        path_parts = folder_path.split(os.sep)
        breadcrumb_links = [f"[🏠 主目錄]({back_to_root}{ROOT_README})"]
        for i in range(len(path_parts)):
            part_name = path_parts[i]
            if i == len(path_parts) - 1:
                breadcrumb_links.append(f"**{part_name}**")
            else:
                steps_back = len(path_parts) - 1 - i
                link_path = "../" * steps_back + "README.md"
                breadcrumb_links.append(f"[{part_name}]({link_path})")
        breadcrumb_str = " / ".join(breadcrumb_links)

        # --- 子目錄 README 美化 (卡片樣式 + CDN 複製區塊) ---
        sub_content = [
            f"# 🖼️ 素材分類：{folder_name}\n",
            f"> {breadcrumb_str}\n",
            f"本目錄共有 `{len(valid_files)}` 個檔案\n",
            "| 🎨 預覽 (點擊放大) | 📋 檔案詳細資訊與連結 |",
            "| :--- | :--- |"
        ]
        
        for f in sorted(valid_files):
            f_path = os.path.join(root, f)
            rel_img_path = os.path.relpath(f_path, '.').replace('\\', '/')
            safe_rel_path = urllib.parse.quote(rel_img_path)
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

                cdn_url = f"https://cdn.jsdelivr.net/gh{safe_repo}@{BRANCH}/{safe_rel_path}"
                copy_md = f"![{f}]({cdn_url})"

                details = (
                    f"**📂 檔名:** `{f}`<br>"
                    f"{spec}<br>"
                    f"⚖️ **大小:** `{size}` | 📅 **更新:** `{mtime}`<br>"
                    f"<br>🚀 **jsDelivr Markdown:**<br>`{copy_md}`<br>"
                    f"🔗 **直接連結 (Url):**<br>`{cdn_url}`<br>"
                    f"📥 [檢視原始檔]({safe_f})"
                )
                
                img_tag = f'<a href="{safe_f}"><img src="{safe_f}" width="{SUB_WIDTH}" alt="{f}"></a>'
                sub_content.append(f"| {img_tag} | {details} |")
            except Exception as e:
                print(f"Error processing {f}: {e}")
                sub_content.append(f"| `{f}` | ⚠️ 無法讀取詳細資訊 |")
        
        with open(readme_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(sub_content))
    else:
        # 保留父資料夾名稱（如 3Ds）
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
    header = "# 🎨 我的設計素材庫\n這是一個全自動更新的素材導覽系統。"
    content = f"{header}\n\n{new_nav_section}\n\n---\n*Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
print(f"Successfully processed {ROOT_README}")
