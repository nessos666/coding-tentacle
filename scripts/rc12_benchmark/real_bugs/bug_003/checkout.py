"""
Bug: ImportError — PaymentProcessor wurde in PaymentHandler umbenannt.
"""
class PaymentHandler:
    def __init__(self, user): self.user = user
    def process(self): return f"Processed for {self.user}"

def checkout(user):
    return PaymentHandler(user).process()

def test_checkout():
    assert checkout("user42") == "Processed for user42"

if __name__ == '__main__':
    test_checkout()
    print("OK — PaymentHandler import works")
