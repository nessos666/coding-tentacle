"""
Bug: KeyError — dict access ohne .get()
"""
def get_user_id(request_data):
    return request_data.get('user_id', 'unknown')

def test_get_user_id():
    assert get_user_id({'user_id': 42}) == 42
    assert get_user_id({}) == 'unknown'

if __name__ == '__main__':
    test_get_user_id()
    print("OK")
