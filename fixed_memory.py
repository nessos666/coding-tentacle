"""
Bug: MemoryError — Große Datei komplett in Speicher laden (CWE-789)
"""
def load_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

def test_load():
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("line1\nline2\n")
        path = f.name
    result = list(load_large_file(path))
    assert len(result) == 2
    import os; os.unlink(path)

if __name__ == '__main__':
    test_load()
    print("OK — chunked read")
