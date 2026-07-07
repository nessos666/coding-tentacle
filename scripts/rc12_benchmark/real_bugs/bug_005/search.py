"""
Bug: IndexError — Zugriff auf leere Liste
"""
def get_first_result(results):
    # BUG: Kein Check ob Liste leer ist
    # return results[0]
    if not results:
        return None
    return results[0]  # Fix: bounds check

def test_get_first():
    assert get_first_result([1,2,3]) == 1
    assert get_first_result([]) is None

if __name__ == '__main__':
    test_get_first()
    print("OK")
