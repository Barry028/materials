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
        
        # 動態計算「回到主目錄」的層級
        # root 相對於根目錄的深度
        rel_depth = folder_path.replace('\\', '/').count('/') + 1
        back_to_root = "../" * rel_depth
        
        # 紀錄樹狀導覽資訊（用於根目錄）
        tree_depth = folder_path.replace('\\', '/').count('/')
        indent = "　" * tree_depth + ("┗ " if tree_depth > 0 else "📂 ")
        cover_file = sorted(valid_files)[0]
        cover_url = os.path.join(folder_path, cover_file).replace('\\', '/')
        
        img_style = 'width="45" height="45" style="border-radius:50%; border:2px solid #eee; object-fit:cover;"'
        img_html = f'<a href="{folder_path}/README.md"><img src="{cover_url}" {img_style}></a>'
        subdir_links.append(f"| [{indent}{folder_name}]({folder_path}/README.md) | {img_html} | `{len(valid_files)} Items` |")
        
        # 生成子目錄 README
        sub_content = [
            f"# 🖼️ {folder_name} 素材庫\n",
            f"[⬅️ 返回主目錄]({back_to_root}{ROOT_README})\n", # 修正處
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
# 建立分類導覽表格 (如果 subdir_links 是空的，給予提示)
if not subdir_links:
    nav_table_text = "\n目前 `images/` 資料夾中還沒有圖片，請上傳圖片至子目錄後再執行。\n"
else:
    tree_table = [
        "## 📂 素材目錄樹狀導覽\n",
        "| 目錄路徑 | 封面 | 統計 |",
        "| :--- | :---: | :---: |"
    ] + subdir_links
    nav_table_text = "\n".join(tree_table)

new_nav_section = f"{START_MARKER}\n{nav_table_text}\n{END_MARKER}"

# 檢查根目錄 README 是否存在
if os.path.exists(ROOT_README):
    with open(ROOT_README, 'r', encoding='utf-8') as f_in:
        content = f_in.read()
    
    if START_MARKER in content:
        content = re.sub(f"{START_MARKER}.*?{END_MARKER}", new_nav_section, content, flags=re.DOTALL)
    else:
        # 如果檔案存在但沒有標記，就補在最後面
        content += f"\n\n{new_nav_section}"
else:
    # 關鍵：如果完全沒檔案，直接建立一個
    header = "# 🎨 我的設計素材庫\n這是一個全自動更新的素材導覽。"
    content = f"{header}\n\n{new_nav_section}\n\n---\n*Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"

with open(ROOT_README, 'w', encoding='utf-8') as f_out:
    f_out.write(content)
print(f"Successfully processed {ROOT_README}") # 讓 Log 顯示進度