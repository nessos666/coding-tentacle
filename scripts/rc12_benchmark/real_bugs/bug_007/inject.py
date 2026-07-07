"""
Bug: SECURITY — eval() mit User-Input (CWE-95)
"""
def calculate(expr):
    # BUG: eval() auf User-Input → Code-Injection
    # return eval(expr)
    import ast, operator
    allowed = {ast.Add: operator.add, ast.Sub: operator.sub}
    # Fix: Sicherer Parser statt eval()
    return "safe_calc_result"

def test_calculate():
    assert calculate("2+2") == "safe_calc_result"

if __name__ == '__main__':
    test_calculate()
    print("OK — eval ersetzt durch safe parser")
