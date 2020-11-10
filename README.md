# mrc-gnome-thumbnailer
MRC2014 (*.mrc) 2D and 3D file thumbnail generator for GNOME desktops.

The thumbnail shows central slice (if 3D) and automatically applies contrast stretching.

Tested on Pop OS 20.10, Nautilus file browser.

![Before and after](demo.png)

# Installation
Clone the repository: `git clone git@github.com:the-lay/mrc-gnome-thumbnailer.git`

Change directory: `cd mrc-gnome-thumbnailer`

Run make install: `sudo make install`

Delete thumbnails folder: `rm -r ~/.cache/thumbnails`

Quit all Nautilus processes: `nautilus -q`

__Even if you currently do not have any Nautilus windows open, you should run the command above!__

From now on, the thumbnails should be visible.

# Troubleshooting
#### Thumbnails do no show up on some Ubuntu-based distributions 18.04 and later
Most likely it is a problem with bubblewrap 
([1](https://askubuntu.com/questions/1279091/nautilus-thumbnailer-for-ms-office-documents-in-ubuntu-20),
[2](https://askubuntu.com/questions/1088539/custom-thumbnailers-don-t-work-on-ubuntu-18-10-and-18-04),
and many more threads online). The short workaround fix would be to install a bwrap wrapper in `/usr/local/bin`:
```
sudo wget -O /usr/local/bin/bwrap https://raw.githubusercontent.com/NicolasBernaerts/ubuntu-scripts/master/nautilus/bwrap
sudo chmod +rx /usr/local/bin/bwrap
```