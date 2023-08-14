const fs = require('fs');
const path = require('path');

const imageFolderPath = 'images/'; // 指定圖片資料夾路徑
const outputFile = 'image_list.json'; // 輸出的 JSON 檔案名稱

const supportedExtensions = ['.svg', '.png', '.jpg', 'webp'];

function getFilesRecursively(folderPath) {
  const files = [];

  function traverse(currentPath) {
    const dirContents = fs.readdirSync(currentPath);

    dirContents.forEach(item => {
      const itemPath = path.join(currentPath, item);
      const isDirectory = fs.statSync(itemPath).isDirectory();

      if (isDirectory) {
        traverse(itemPath);
      } else {
        const ext = path.extname(item).toLowerCase();
        if (supportedExtensions.includes(ext)) {
          files.push(itemPath);
        }
      }
    });
  }

  traverse(folderPath);
  return files;
}

const imageFiles = getFilesRecursively(imageFolderPath);

fs.writeFileSync(outputFile, JSON.stringify(imageFiles, null, 2));

console.log(`Image list generated and saved to ${outputFile}`);