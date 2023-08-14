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
          // 提取資料夾名稱並組成路徑
          const imagePath = path.relative(imageFolderPath, itemPath);
          const folderNames = imagePath.split(path.sep).slice(0, -1);
          const folderPathNames = folderNames.map(name => name.toLowerCase());

          files.push({
            imagePath: imageFolderPath+imagePath,
            folderNames: folderPathNames
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





//   let listfiles = [
//     "images/3Ds/3D_Ecommercia/3d-Icon-ecommercia-09-60.png",
//     "images/3Ds/3D_Education/BackPack-b3.png"]


// console.log( listfiles )