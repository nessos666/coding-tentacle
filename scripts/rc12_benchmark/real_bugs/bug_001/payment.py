"""
Echte Bug-Reproduktion: NullPointer in payment.py
Erwartet: CT erkennt NullPointer, schlägt guard_clause vor.
"""

def process_payment(user):
    """
    BUG: user kann None sein wenn nicht eingeloggt.
    Kein Null-Check → AttributeError: 'NoneType' has no attribute 'get'
    """
    # BUG: Kein guard clause
    amount = user.get('amount', 0)  # Line 12: CRASH wenn user=None
    return f"Processed {amount}"


# Test
def test_process_payment_with_user():
    assert process_payment({'amount': 100}) == "Processed 100"

def test_process_payment_none_user():
    """Dieser Test SCHLÄGT FEHL — das ist der Bug."""
    try:
        result = process_payment(None)
        assert result is not None  # Sollte nicht crashen
    except AttributeError:
        assert False, "BUG: process_payment crashed on None user"


if __name__ == '__main__':
    test_process_payment_with_user()
    print("Test 1 passed (mit User)")
    
    try:
        test_process_payment_none_user()
    except AssertionError as e:
        print(f"BUG GEFUNDEN: {e}")
