def generate_report(count, label):
    return 'Total: ' + str(count) + ' ' + label

def test_generate_report():
    assert generate_report(5, 'items') == 'Total: 5 items'

if __name__ == '__main__':
    try:
        test_generate_report()
    except TypeError as e:
        print(f'BUG FOUND: {e}')
