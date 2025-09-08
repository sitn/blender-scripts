import os, re
from PIL import Image

def main(tiles_dir, output_file):
    tile_pattern = re.compile(r"tile_(\d+)_(\d+)_(\d+)\.*")
    tiles = {}
    max_x_idx = max_y_idx = 0

    print(f"Reading tiles...")
    for fname in os.listdir(tiles_dir):
        match = tile_pattern.match(fname)
        if match:
            _, x_idx, y_idx = map(int, match.groups())
            path = os.path.join(tiles_dir, fname)
            with Image.open(path) as img:
                w, h = img.size
            tiles[(x_idx, y_idx)] = (path, w, h)
            max_x_idx = max(max_x_idx, x_idx)
            max_y_idx = max(max_y_idx, y_idx)

    x_offsets, y_offsets = [0], [0]
    for x in range(max_x_idx + 1):
        x_offsets.append(x_offsets[-1] + tiles[(x, 0)][1])
    for y in range(max_y_idx + 1):
        y_offsets.append(y_offsets[-1] + tiles[(0, y)][2])

    final_image = Image.new('RGB', (x_offsets[-1], y_offsets[-1]))

    print(f"Merging tiles...")
    for i, ((x_idx, y_idx), (path, w, h)) in enumerate(tiles.items()):
        print(f"{i}/{len(tiles)}")
        with Image.open(path) as img:
            final_image.paste(img, (x_offsets[x_idx],  y_offsets[-1] - y_offsets[y_idx + 1]))

    final_image.save(output_file)

if __name__ == '__main__':
    tiles_dir = input("Enter tiles folder location : ")
    output_file = input("Enter output file (default = ./merged.tif) : ")
    if output_file == "" :
        output_file = './merged.tif'
    main(tiles_dir, output_file)