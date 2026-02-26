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
    
    # 建立樹狀表格導覽（圓形縮圖版）
    tree_content = [
        "## 📂 素材庫樹狀導覽\n",
        "| 目錄名稱 | 封面預覽 | 統計 |",
        "| :--- | :---: | :---: |"
    ]
    
    # 重新遍歷以建立層級感
    for root, dirs, files in sorted(os.walk(IMAGE_DIR)):
        valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))]
        
        if valid_files:
            folder_path = os.path.normpath(os.path.relpath(root, '.'))
            folder_name = os.path.basename(root)
            
            # 計算層級深度，建立縮排
            # 注意：在 GitHub README 中，全形空白 "　" 縮進效果最好
            depth = folder_path.count(os.sep)
            indent = "　" * depth + ("┗ " if depth > 0 else "📂 ")
            
            # 取得第一張圖片作為封面，並使用 HTML 樣式美化
            cover_file = sorted(valid_files)[0]
            # 修正路徑在 Windows/Linux 上的相容性
            cover_path = os.path.join(folder_path, cover_file).replace('\\', '/')
            
            # 圓形縮圖樣式：固定寬高 + 圓角 + 灰色細邊框
            img_style = 'width="40" height="40" style="border-radius:50%; border:1px solid #ddd; object-fit:cover; display:block; margin:auto;"'
            img_preview = f'<a href="{folder_path}/README.md"><img src="{cover_path}" {img_style}></a>'
            
            # 連結與資訊
            folder_link = f"[{indent}{folder_name}]({folder_path}/README.md)"
            count_info = f"`{len(valid_files)} Items`"
            
            tree_content.append(f"| {folder_link} | {img_preview} | {count_info} |")

    # 組合內容並替換標記
    nav_menu = f"{START_MARKER}\n" + "\n".join(tree_content) + f"\n{END_MARKER}"
    
    if START_MARKER in root_text:
        root_text = re.sub(f"{START_MARKER}.*?{END_MARKER}", nav_menu, root_text, flags=re.DOTALL)
    else:
        root_text += f"\n\n{nav_menu}"
        
    with open(ROOT_README, 'w', encoding='utf-8') as f_out:
        f_out.write(root_text)