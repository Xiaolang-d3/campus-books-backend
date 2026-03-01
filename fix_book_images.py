"""
修复书籍图片 - 将现有图片复制为缺失的图片文件
"""
import shutil
import os

# 源图片（现有的书籍封面）
source_images = [
    'ershoushuji_shujifengmian1.jpg',
    'ershoushuji_shujifengmian2.jpg',
    'ershoushuji_shujifengmian3.jpg',
    'ershoushuji_shujifengmian4.jpg',
    'ershoushuji_shujifengmian5.jpg',
    'ershoushuji_shujifengmian6.jpg',
    'ershoushuji_shujifengmian7.jpg',
    'ershoushuji_shujifengmian8.jpg',
]

# 需要创建的图片文件
target_images = [
    'python.jpg', 'java.jpg', 'algorithm.jpg', 'csapp.jpg',
    'datastructure.jpg', 'js.jpg', 'mysql.jpg', 'linux.jpg',
    'alive.jpg', 'ordinary.jpg', 'threebody.jpg', 'dream.jpg', 'fortress.jpg',
    'economics.jpg', 'wealth.jpg', 'capital.jpg', 'thinking.jpg',
    'wanli.jpg', 'sapiens.jpg', 'guns.jpg', 'history.jpg',
    'philosophy.jpg', 'sophie.jpg', 'republic.jpg',
    'pedagogy.jpg', 'psychology.jpg', 'education.jpg',
    'art.jpg', 'design.jpg', 'color.jpg',
    'time.jpg', 'origin.jpg', 'cosmos.jpg', 'gene.jpg',
]

upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'upload')

print("=" * 60)
print("修复书籍图片文件")
print("=" * 60)

copied = 0
skipped = 0

for i, target in enumerate(target_images):
    target_path = os.path.join(upload_dir, target)

    # 如果文件已存在，跳过
    if os.path.exists(target_path):
        print(f"✓ 跳过 {target} (已存在)")
        skipped += 1
        continue

    # 循环使用源图片
    source = source_images[i % len(source_images)]
    source_path = os.path.join(upload_dir, source)

    try:
        shutil.copy2(source_path, target_path)
        print(f"✓ 创建 {target} (从 {source})")
        copied += 1
    except Exception as e:
        print(f"✗ 失败 {target}: {e}")

print("\n" + "=" * 60)
print(f"完成！复制了 {copied} 个文件，跳过 {skipped} 个")
print("=" * 60)
