# /// script
# dependencies = ["numpy", "pillow", "mrcfile", "emfile"]
# ///
"""Tests for src/mrc-em-thumbnailer.py. Run with: uv run test_thumbnailer.py

mrcfile and emfile are used only as reference readers to check the thumbnailer against.
"""
import importlib.util
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import emfile
import mrcfile
import numpy as np
from PIL import Image

SCRIPT = Path(__file__).parent / 'src' / 'mrc-em-thumbnailer.py'
spec = importlib.util.spec_from_file_location('thumbnailer', SCRIPT)
thumbnailer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thumbnailer)

rng = np.random.default_rng(0)
tmp = Path(tempfile.mkdtemp())
SHAPES = [(40, 30), (5, 40, 30), (6, 40, 30)]  # non-square to catch x/y mix-ups


def central(data):
    data = data.reshape(-1, *data.shape[-2:])
    return data[data.shape[0] // 2]


def random_data(shape, dtype):
    return (rng.normal(0, 50, shape) + 100).astype(dtype)


def thumbnail(path, out, size=16):
    return subprocess.run([sys.executable, SCRIPT, path, out, str(size)], capture_output=True)


def test_mrc_reader_matches_mrcfile():
    cases = [(f'{np.dtype(t).name}_{len(s)}d_{s[0]}', random_data(s, t))
             for t in (np.int8, np.int16, np.float32, np.uint16, np.float16) for s in SHAPES]
    cases.append(('big_endian', random_data((5, 40, 30), '>f4')))
    cases.append(('volume_stack', random_data((3, 4, 40, 30), np.float32)))
    for name, data in cases:
        path = tmp / f'{name}.mrc'
        mrcfile.write(path, data, overwrite=True)
        with mrcfile.open(path) as mrc:
            expected = central(mrc.data)
        assert np.array_equal(thumbnailer.mrc_central_slice(path), expected), name
    assert (tmp / 'big_endian.mrc').read_bytes()[212] == 0x11  # really wrote big-endian

    path = tmp / 'extended_header.mrc'
    with mrcfile.new(path, overwrite=True) as mrc:
        mrc.set_data(random_data((5, 40, 30), np.float32))
        mrc.set_extended_header(np.arange(77, dtype=np.int32))
        expected = central(mrc.data)
    assert np.array_equal(thumbnailer.mrc_central_slice(path), expected)


def test_em_reader_matches_emfile():
    for t in (np.int8, np.int16, np.int32, np.float32, np.float64):
        for shape in [(1, 40, 30), *SHAPES[1:]]:
            path = tmp / f'{np.dtype(t).name}_{shape[0]}.em'
            emfile.write(path, random_data(shape, t), overwrite=True)
            expected = central(emfile.read(path)[1])
            assert np.array_equal(thumbnailer.em_central_slice(path), expected), path.name


def test_cli_writes_png_for_every_extension():
    data = random_data((5, 64, 48), np.float32)
    for name in ('a.mrc', 'b.MRC', 'c.mrcs', 'd.map', 'e.rec'):
        mrcfile.write(tmp / name, data, overwrite=True)
    mrcfile.write(tmp / 'h_2d.mrc', data[0], overwrite=True)
    for name in ('f.em', 'g.EM'):
        emfile.write(tmp / name, data, overwrite=True)
    for name in ('a.mrc', 'b.MRC', 'c.mrcs', 'd.map', 'e.rec', 'h_2d.mrc', 'f.em', 'g.EM'):
        out = tmp / f'{name}.png'
        result = thumbnail(tmp / name, out)
        assert result.returncode == 0, (name, result.stderr)
        img = Image.open(out)
        assert (img.mode, img.size) == ('L', (12, 16)), (name, img.mode, img.size)


def test_cli_output_path_without_extension():
    mrcfile.write(tmp / 'noext.mrc', random_data((5, 40, 30), np.float32), overwrite=True)
    out = tmp / 'thumbnail-output'
    result = thumbnail(tmp / 'noext.mrc', out)
    assert result.returncode == 0, result.stderr
    assert Image.open(out).format == 'PNG'


def test_nan_pixels_do_not_blank_thumbnail():
    data = np.tile(np.linspace(0, 1, 64, dtype=np.float32), (3, 64, 1))
    data[:, :8, :8] = np.nan
    mrcfile.write(tmp / 'nan.mrc', data, overwrite=True)
    out = tmp / 'nan.png'
    assert thumbnail(tmp / 'nan.mrc', out, 64).returncode == 0
    pixels = np.asarray(Image.open(out))
    assert pixels[32].min() == 0 and pixels[32].max() == 255, pixels[32]


def test_constant_slice_rescales_without_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        out = thumbnailer.rescale(np.zeros((4, 4), np.float32), in_range=(0.0, 0.0))
    assert out.dtype == np.uint8 and np.all(out == out[0, 0])


def test_garbage_input_fails_without_output():
    (tmp / 'garbage.mrc').write_bytes(b'not an mrc file' * 10)
    out = tmp / 'garbage.png'
    assert thumbnail(tmp / 'garbage.mrc', out).returncode != 0
    assert not out.exists()


if __name__ == '__main__':
    tests = [f for name, f in sorted(globals().items()) if name.startswith('test_')]
    failed = 0
    for test in tests:
        try:
            test()
            print(f'PASS {test.__name__}')
        except (Exception, SystemExit) as e:  # noqa: BLE001
            failed += 1
            print(f'FAIL {test.__name__}: {type(e).__name__}: {e}'[:400])
    print(f'{len(tests) - failed}/{len(tests)} passed')
    sys.exit(1 if failed else 0)
