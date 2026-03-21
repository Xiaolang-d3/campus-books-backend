"""
Generate placeholder cover images for demo books.
Creates simple PNG images and saves them to campus-books-backend/static/upload/
"""
import os
import zlib
import struct

# Placeholder images: (filename, bg_color_rgb, title, subtitle)
PLACEHOLDERS = [
    ('datastructure.jpg', (37, 99, 235), '数据结构', 'Data Structure'),
    ('finance.jpg', (5, 150, 105), '金融学', 'Finance'),
    ('literature.jpg', (220, 38, 38), '中国现代文学史', 'Literature'),
    ('os.jpg', (124, 58, 237), '操作系统原理', 'OS'),
    ('database.jpg', (217, 119, 6), '数据库系统概论', 'Database'),
    ('python.jpg', (22, 163, 74), 'Python程序设计', 'Python'),
    ('accounting.jpg', (8, 145, 178), '基础会计学', 'Accounting'),
    ('microeconomics.jpg', (190, 24, 93), '微观经济学', 'Microeconomics'),
    ('news_picture1.jpg', (79, 70, 229), '校园二手书平台', 'Campus Books'),
    ('picture1.jpg', (99, 102, 241), '欢迎使用', 'Welcome'),
    ('picture2.jpg', (139, 92, 246), '校园二手专业书', 'Textbooks'),
    ('picture3.jpg', (168, 85, 247), '交易平台', 'Trading Platform'),
]


def create_png(width, height, pixels):
    """Create a PNG file from raw RGB pixel data."""
    def png_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    png += png_chunk(b'IHDR', ihdr_data)

    # IDAT chunk (raw image data with filter bytes)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter type: none
        for x in range(width):
            raw_data += bytes(pixels[y * width + x])
    compressed = zlib.compress(raw_data, 9)
    png += png_chunk(b'IDAT', compressed)

    # IEND chunk
    png += png_chunk(b'IEND', b'')

    return png


def hex_to_dark(r, g, b, factor=0.65):
    return (max(0, int(r * factor)), max(0, int(g * factor)), max(0, int(b * factor)))


def blend(c1, c2, t):
    return (int(c1[0] * (1 - t) + c2[0] * t), int(c1[1] * (1 - t) + c2[1] * t), int(c1[2] * (1 - t) + c2[2] * t))


def generate_book_cover(width, height, bg_rgb, title, subtitle):
    """Generate a book cover placeholder image."""
    pixels = []
    dark_bg = hex_to_dark(*bg_rgb)

    for y in range(height):
        row = []
        for x in range(width):
            # Linear gradient from top-left to bottom-right
            t = ((x / width) + (y / height)) / 2
            r, g, b = blend(bg_rgb, dark_bg, t)

            # Add book spine effect on left edge
            if x < 30:
                shadow_factor = 0.3 + (x / 30) * 0.3
                r = max(0, int(r * shadow_factor))
                g = max(0, int(g * shadow_factor))
                b = max(0, int(b * shadow_factor))

            # Add subtle border
            if x < 3 or x >= width - 3 or y < 3 or y >= height - 3:
                r = max(0, r - 30)
                g = max(0, g - 30)
                b = max(0, b - 30)

            row.append((r, g, b))
        pixels.extend(row)

    return pixels


def darken(r, g, b, factor=0.75):
    return (max(0, int(r * factor)), max(0, int(g * factor)), max(0, int(b * factor)))


def generate_banner(width, height, bg_rgb, title, subtitle):
    """Generate a banner placeholder image."""
    pixels = []
    dark_bg = darken(*bg_rgb)

    for y in range(height):
        row = []
        for x in range(width):
            t = (x / width + y / height) / 2
            r, g, b = blend(bg_rgb, dark_bg, t)
            # Border
            if x < 4 or x >= width - 4 or y < 4 or y >= height - 4:
                r = max(0, r - 25)
                g = max(0, g - 25)
                b = max(0, b - 25)
            row.append((r, g, b))
        pixels.extend(row)

    return pixels


def generate_images():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(backend_dir, 'static', 'upload')
    os.makedirs(upload_dir, exist_ok=True)

    W, H = 400, 560  # Book cover size
    BW, BH = 800, 400  # Banner size

    created = 0
    for filename, color, title, subtitle in PLACEHOLDERS:
        if 'news' in filename or 'picture' in filename:
            w, h = BW, BH
            pixels = generate_banner(w, h, color, title, subtitle)
        else:
            w, h = W, H
            pixels = generate_book_cover(w, h, color, title, subtitle)

        png_data = create_png(w, h, pixels)
        out_path = os.path.join(upload_dir, filename)
        with open(out_path, 'wb') as f:
            f.write(png_data)
        print(f'[OK] Created: {filename} ({w}x{h})')
        created += 1

    print(f'\nTotal: {created} placeholder images created in:\n  {upload_dir}')


if __name__ == '__main__':
    generate_images()
