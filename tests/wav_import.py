"""Check RIFF boundaries and preserve the inherited sounds' decoded PCM."""
from pathlib import Path
import struct
import wave


root = Path(__file__).resolve().parents[1]
for path in sorted((root / "assets/sounds").glob("*.wav")):
    data = path.read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WAVE", path
    assert struct.unpack_from("<I", data, 4)[0] + 8 == len(data), path
    offset = 12
    while offset < len(data):
        assert offset + 8 <= len(data), (path, "incomplete chunk header")
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        assert end <= len(data), (path, "truncated chunk")
        if size % 2:
            assert end < len(data), (path, "missing RIFF padding")
        offset = end + size % 2
    assert offset == len(data), path
    source = root / "assets/source/sounds" / path.name
    if path.stem in {"coin", "jump", "tap"}:
        assert source.is_file(), (path, "missing preserved source")
        with wave.open(str(source), "rb") as original, wave.open(str(path), "rb") as ready:
            assert original.getparams() == ready.getparams(), path
            assert original.readframes(original.getnframes()) == ready.readframes(ready.getnframes()), path
    print(f"PASS {path.name}: RIFF aligned; original PCM preserved when normalized")
