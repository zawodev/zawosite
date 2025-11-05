import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const distDir = path.join(__dirname, '..', 'dist');
const publicDir = path.join(__dirname, '..', '..', '..', 'frontend', 'public', 'games', 'zawomons-gt');

function deleteDirectoryRecursive(dirPath) {
    if (fs.existsSync(dirPath)) {
        fs.readdirSync(dirPath).forEach((file) => {
            const curPath = path.join(dirPath, file);
            if (fs.lstatSync(curPath).isDirectory()) {
                deleteDirectoryRecursive(curPath);
            } else {
                fs.unlinkSync(curPath);
            }
        });
        fs.rmdirSync(dirPath);
    }
}

function copyRecursive(src, dest) {
    if (!fs.existsSync(src)) {
        console.error(`Source directory ${src} does not exist`);
        return;
    }

    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    }

    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (let entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);

        if (entry.isDirectory()) {
            copyRecursive(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

console.log('Cleaning old build files...');
// Usuń stare pliki, ale zachowaj thumbnail.svg
const thumbnailPath = path.join(publicDir, 'thumbnail.svg');
const thumbnailExists = fs.existsSync(thumbnailPath);
let thumbnailBackup = null;

if (thumbnailExists) {
    thumbnailBackup = fs.readFileSync(thumbnailPath);
}

// Usuń tylko foldery assets i index.html (nie cały folder)
const assetsDir = path.join(publicDir, 'assets');
const indexPath = path.join(publicDir, 'index.html');

if (fs.existsSync(assetsDir)) {
    deleteDirectoryRecursive(assetsDir);
    console.log('✓ Removed old assets');
}

if (fs.existsSync(indexPath)) {
    fs.unlinkSync(indexPath);
    console.log('✓ Removed old index.html');
}

console.log('Copying new build to frontend/public/games/zawomons-gt...');
copyRecursive(distDir, publicDir);

// Przywróć thumbnail jeśli był
if (thumbnailBackup) {
    fs.writeFileSync(thumbnailPath, thumbnailBackup);
}

console.log('✓ Build copied successfully!');
