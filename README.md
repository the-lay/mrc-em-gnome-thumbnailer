# mrc-em-gnome-thumbnailer

GNOME desktop thumbnailer for MRC2014 (*.mrc, *.mrcs, *.map, ...) and EM (*.em), common cryo-electron microscopy and tomography file formats. The thumbnail shows the central slice and automatically applies contrast stretching.

Update 20.10.2026: Works again on current distributions: no more pip, only numpy and Pillow from your distribution's packages. Added .mrcs and .map support.

Update 22.12.2021: Added support for .em files, renamed the project.

Tested on Ubuntu 22.04, 24.04, 26.04, Debian 13, Fedora 44 and Arch Linux (Nautilus 42 to 51). Earlier versions were tested on Ubuntu/PopOS 20.04 to 21.10.

![Before and after](demo.png)

# Installation
1. Install numpy and Pillow from your distribution's packages:
   - Ubuntu/Debian: `sudo apt install python3-numpy python3-pil`
   - Fedora: `sudo dnf install python3-numpy python3-pillow`
   - Arch: `sudo pacman -S python-numpy python-pillow`
2. Clone the repository: `git clone https://github.com/the-lay/mrc-em-gnome-thumbnailer.git tomo-thumbnailer`
3. Change directory: `cd tomo-thumbnailer`
4. Run make install: `sudo make install`
5. Restart Nautilus: `nautilus -q`

From now on, the thumbnails should be visible.

To uninstall, run `sudo make uninstall` in the same directory.

Why not pip? GNOME runs thumbnailers in a sandbox that can only see `/usr`, and current distributions refuse system-wide pip installs ([PEP 668](https://peps.python.org/pep-0668/)), so the dependencies have to come from your distribution.

# Supported files
- MRC2014: `.mrc`, `.mrcs`, and any other MRC file with the standard `MAP ` stamp in its header (`.map`, IMOD's `.rec`/`.st`/`.ali`, ...). Modes 0, 1, 2, 6 and 12. 2D images, 3D volumes and volume stacks.
- EM: `.em` with 8/16/32-bit integer or 32/64-bit float data.

# Troubleshooting
#### Thumbnails do not show up for files you have opened before
GNOME remembers files it failed to thumbnail (for example, with an older version of this thumbnailer) and does not retry them. Clear the list of failures and restart Nautilus:
```
rm -r ~/.cache/thumbnails/fail
nautilus -q
```

#### Checking a single file
Run the thumbnailer by hand to see the error message: `mrc-em-thumbnailer path/to/file.mrc /tmp/thumbnail.png 256`

# Development
Run the tests with [uv](https://docs.astral.sh/uv/): `uv run test_thumbnailer.py`
