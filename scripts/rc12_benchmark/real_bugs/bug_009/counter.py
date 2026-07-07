"""
Bug: RACE CONDITION — Counter ohne Lock (CWE-362)
"""
import threading

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()  # Fix: Lock hinzugefügt
    
    def increment(self):
        # BUG: self.value += 1 ist nicht atomar
        # self.value += 1
        with self.lock:
            self.value += 1  # Fix: thread-safe
        return self.value

def test_counter():
    c = Counter()
    assert c.increment() == 1

if __name__ == '__main__':
    test_counter()
    print("OK — thread-safe counter")
