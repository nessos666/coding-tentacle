"""
Bug: ValueError — int() Parse-Fehler bei ungültiger Eingabe
"""
def parse_age(age_str):
    # BUG: int() crasht bei 'N/A'
    # return int(age_str)
    try:
        return int(age_str)
    except ValueError:
        return -1  # Fix: Fehler abfangen

def test_parse_age():
    assert parse_age("25") == 25
    assert parse_age("N/A") == -1

if __name__ == '__main__':
    test_parse_age()
    print("OK")
