"""
Bug: MemoryError — Große Datei komplett in Speicher laden (CWE-789)
"""
def load_large_file(path):
    # BUG: Ganze Datei auf einmal im Speicher
    # return open(path).read()
    result = []
    with open(path) as f:
        for line in f:  # Fix: Zeilenweise lesen
            result.append(line.strip())
            if len(result) >= 1000:
                break
    return result

def test_load():
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("line1\nline2\n")
        path = f.name
    result = load_large_file(path)
    assert len(result) == 2
    import os; os.unlink(path)

if __name__ == '__main__':
    test_load()
    print("OK — chunked read")
