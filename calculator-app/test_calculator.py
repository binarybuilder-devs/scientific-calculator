"""Quick checks: run with  python -m pytest test_calculator.py  (or python test_calculator.py)"""
import math
from app import app
from calculator_logic import calculate, CalcError, public_operations

def test_math_matches_original():
    assert calculate("addition", {"n1": "2", "n2": "3"}) == "5"
    assert calculate("subtraction", {"n1": "2", "n2": "7", "choice": "1"}) == "-5"
    assert calculate("subtraction", {"n1": "2", "n2": "7", "choice": "2"}) == "5"
    assert calculate("multiplication", {"n1": "4", "n2": "5"}) == "20"
    assert calculate("division", {"n1": "9", "n2": "2", "choice": "1"}) == "4.5"
    assert calculate("combination", {"n": "5", "r": "2"}) == "10"
    assert calculate("permutation", {"n": "5", "r": "2"}) == "20"
    assert calculate("factorial", {"n": "5"}) == "120"
    assert calculate("hcf", {"nums": ["12", "18", "24"]}) == "6"
    assert calculate("lcm", {"nums": ["4", "6"]}) == "12"
    assert calculate("square_root_int", {"n": "17"}) == "4"
    assert calculate("square_root", {"n": "16"}) == "4.0"
    assert abs(float(calculate("cuberoot", {"n": "27"})) - 3) < 1e-9
    assert abs(float(calculate("simple_log", {"n": "8", "base": "2"})) - 3) < 1e-9
    assert abs(float(calculate("log_base10", {"n": "1000"})) - 3) < 1e-9
    assert calculate("power", {"n": "2", "p": "10"}) == "1024.0"
    assert calculate("exp_base2", {"n": "3"}) == "8.0"

def test_errors_are_friendly():
    for op, vals in [("division", {"n1": "1", "n2": "0", "choice": "1"}),
                     ("subtraction", {"n1": "1", "n2": "2", "choice": "9"}),
                     ("factorial", {"n": "-1"}),
                     ("addition", {"n1": "abc", "n2": "2"}),
                     ("hcf", {"nums": ["5"]})]:
        try:
            calculate(op, vals); raise AssertionError(f"{op} should fail")
        except CalcError:
            pass

def test_api():
    c = app.test_client()
    assert c.get("/api/operations").json[0]["key"]
    r = c.post("/api/calculate", json={"operation": "addition", "values": {"n1": "2", "n2": "3"}})
    assert r.json == {"ok": True, "result": "5"}
    r = c.post("/api/calculate", json={"operation": "division", "values": {"n1": "1", "n2": "0", "choice": "1"}})
    assert r.status_code == 400 and not r.json["ok"]

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("passed", name)
