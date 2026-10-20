"""Integration test: thumbnail files through GNOME's thumbnail factory, the same code (and sandbox) Nautilus uses.

Needs the thumbnailer installed (sudo make install), python3-gi and GnomeDesktop 4.0 introspection data
(gir1.2-gnomedesktop-4.0 on Ubuntu/Debian). Run with: python3 test_gnome.py
"""
import struct
import sys
import tempfile
from pathlib import Path

import gi
import numpy as np
gi.require_version('GnomeDesktop', '4.0')
from gi.repository import Gio, GnomeDesktop  # noqa: E402


def write_mrc(path, data):
    header = bytearray(1024)
    struct.pack_into('<4i', header, 0, data.shape[2], data.shape[1], data.shape[0], 2)  # nx, ny, nz, mode
    header[208:214] = b'MAP DD'  # MRC2014 stamp, little-endian machine stamp; ISPG stays 0 (image stack)
    path.write_bytes(header + data.astype('<f4').tobytes())


def write_em(path, data):
    header = bytearray(512)
    header[0], header[3] = 6, 5  # PC byte order, float32
    struct.pack_into('<3i', header, 4, data.shape[2], data.shape[1], data.shape[0])
    path.write_bytes(header + data.astype('<f4').tobytes())


tmp = Path(tempfile.mkdtemp())
data = np.random.default_rng(0).normal(size=(3, 48, 64))
for name in ('a.mrc', 'b.MRC', 'c.mrcs', 'd.map', 'e.rec'):
    write_mrc(tmp / name, data)
write_mrc(tmp / 'h_2d.mrc', data[:1])  # single image (nz=1), like a micrograph
for name in ('f.em', 'g.EM'):
    write_em(tmp / name, data)
(tmp / 'linker.map').write_text('0x0000 main\n' * 50)

expected = {'a.mrc': 'image/mrc', 'b.MRC': 'image/mrc', 'c.mrcs': 'image/mrc', 'd.map': 'image/mrc',
            'e.rec': 'image/mrc', 'h_2d.mrc': 'image/mrc', 'f.em': 'image/em', 'g.EM': 'image/em',
            'linker.map': 'text/plain'}

factory = GnomeDesktop.DesktopThumbnailFactory.new(GnomeDesktop.DesktopThumbnailSize.LARGE)
# GNOME 43+ added a cancellable argument
cancellable = (None,) if len(GnomeDesktop.DesktopThumbnailFactory.generate_thumbnail.get_arguments()) == 3 else ()
failed = 0
for name, mime in expected.items():
    file = Gio.File.new_for_path(str(tmp / name))
    info = file.query_info('standard::content-type,time::modified', 0, None)
    uri, mtime = file.get_uri(), info.get_attribute_uint64('time::modified')
    try:
        assert info.get_content_type() == mime, f'detected as {info.get_content_type()}'
        can = factory.can_thumbnail(uri, mime, mtime)
        if mime == 'text/plain':
            assert not can, 'should not be thumbnailed'
        else:
            assert can, 'no thumbnailer registered'
            pixbuf = factory.generate_thumbnail(uri, mime, *cancellable)
            assert (pixbuf.get_width(), pixbuf.get_height()) == (64, 48), (pixbuf.get_width(), pixbuf.get_height())
        print(f'PASS {name}')
    except Exception as e:  # noqa: BLE001
        failed += 1
        print(f'FAIL {name}: {e}')
print(f'{len(expected) - failed}/{len(expected)} passed')
sys.exit(1 if failed else 0)
