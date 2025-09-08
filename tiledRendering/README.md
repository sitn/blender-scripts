# Tiled Rendering

This blender plugin adds an option to split large renders into multiple tiles. Partial renders can be resumed from the last rendered tile.

## Installation and Configuration

In a recent blender version, go to `Edit -> Preferences -> Add-ons` and select `Install from Disk` in a the dropdown option menu.

In the file selector, select the file `blender_tiled_render.py`

Ensure that the plugin `Tiling Renderer` is enabled

Once the plugin is enabled, in the render properties, a new menu "Tiling" is added with the following options :
- `Tile Size X` : Width of output tiles in pixels
- `Tile Size Y` : Height of output tiles in pixels
- `Start Tile ID` : First tile ID to be rendered
- `End Tile ID` : Last tile ID to be rendered, -1 to render until the last tile
- `Overlap` : Overlap between tiles in pixels
- `Output Directory` : Folder where all tiles are stored

The `Render` button starts to render the specified tiles. All other render parameters (full image resolution, format, compression, etc) can be defined as usual.

Tile are stored with the following name : `tile_<id>_<X_position>_<Y_position>.png` where `<id>` is a unique identifier

## Merging tiles

The script `merge_tiles.py` merges all tiles in a folder into one final image.
The script asks for the directory where the tiles are located and for the output file.

The script requires the Pillow library. The dependencies can be installed with `pip install -r requirements.txt` 
