

// node generate-image-list.js
const fs = require('fs');
const path = require('path');

const imageFolderPath = 'images/'; // 指定圖片資料夾路徑
const outputFile = 'image_list.json'; // 輸出的 JSON 檔案名稱

const supportedExtensions = ['.svg', '.png', '.jpg', 'webp'];
const fileExtensionRegExp = new RegExp(/([^/.])([^/.]+)/g);

// fs.utimes( path , atime,mtime, callback)
const getFileUpdatedDate = (path) => {
  const stats = fs.statSync(path)
  return stats.mtime
}
console.log( getFileUpdatedDate('image_list.json') )



// fs.utimes('images/image_list.json', new Date(), new Date(), function(err) {
//   if (err) {
//     console.log(“修改時間失敗”);
//     throw err;
//   }
// })

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
          // 提取資料夾名稱並組成路徑
          const imagePath = path.relative(imageFolderPath, itemPath);
          const folderNames = imagePath.split(path.sep).slice(0, -1);
          const folderPathNames = folderNames.map(name => name.toLowerCase());
          const imgtrees = imagePath.match(fileExtensionRegExp).length
          const imageName = imagePath.match(fileExtensionRegExp)[imgtrees - 2]
          const imageType = imagePath.match(fileExtensionRegExp)[imgtrees - 1]

          // console.log( imageName , imageType)
          files.push({
            "imageName": imageName,
            "imageType": imageType,
            "imagePath": imageFolderPath + imagePath,
            "categoryes": [
              folderPathNames,
            ]
          });
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