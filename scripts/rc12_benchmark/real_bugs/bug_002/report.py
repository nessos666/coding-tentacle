"""
Bug: TypeError — int + str concatenation in report.py
"""

def generate_report(count, label):
    return "Total: " + count + " " + label  # BUG: count ist int

def test_generate_report():
    assert generate_report(5, "items") == "Total: 5 items"

if __name__ == '__main__':
    try:
        test_generate_report()
    except TypeError as e:
        print(f"BUG GEFUNDEN: {e}")
