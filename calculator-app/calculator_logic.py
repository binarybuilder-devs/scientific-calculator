"""
calculator_logic.py
-------------------
Your original calculator functions, turned into pure functions that take values
and RETURN the answer (instead of using input()/print()). All the same math,
same options, same rules. The web API in app.py uses these.

To add a new feature: write a function, then add one entry to OPERATIONS below.
"""
import math


class CalcError(ValueError):
    """Raised for bad input. The message is shown to the user."""


# ---------- input parsing helpers (replace your int(input(...)) calls) ----------

def to_int(value, label="number"):
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        raise CalcError(f"Bro, '{label}' must be a whole number 😩")


def to_num(value, label="number"):
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        raise CalcError(f"Bro, '{label}' must be a number 😩")


def to_int_list(values, label="numbers"):
    if not isinstance(values, list) or len(values) < 2:
        raise CalcError("Enter at least 2 numbers.")
    return [to_int(v, label) for v in values]


# ---------- Simple arithmetic ----------

def addition(v):
    return to_int(v["n1"], "first number") + to_int(v["n2"], "second number")


def subtraction(v):
    n1, n2 = to_int(v["n1"], "first number"), to_int(v["n2"], "second number")
    choice = str(v.get("choice", "1"))
    if choice == "1":      # subtract the second number from the first
        return n1 - n2
    if choice == "2":      # subtract the first number from the second
        return n2 - n1
    raise CalcError("Bro you typed the wrong choice 😩")


def multiplication(v):
    return to_int(v["n1"], "first number") * to_int(v["n2"], "second number")


def division(v):
    n1, n2 = to_int(v["n1"], "first number"), to_int(v["n2"], "second number")
    choice = str(v.get("choice", "1"))
    if choice == "1":      # first number divided by second
        if n2 == 0:
            raise CalcError("Can't divide by zero bro 😎")
        return n1 / n2
    if choice == "2":      # second number divided by first
        if n1 == 0:
            raise CalcError("Can't divide by zero bro 😎")
        return n2 / n1
    raise CalcError("invalid choice bro😎")


# ---------- Number-theoretic ----------

def combination(v):
    n, r = to_int(v["n"], "total items"), to_int(v["r"], "items selected")
    if n < 0 or r < 0:
        raise CalcError("Both values must be 0 or more.")
    return math.comb(n, r)


def factorial(v):
    n = to_int(v["n"])
    if n < 0:
        raise CalcError("Factorial needs a number that is 0 or more.")
    if n > 5000:
        raise CalcError("That's too big for me, keep it 5000 or below.")
    return math.factorial(n)


def hcf(v):
    return math.gcd(*to_int_list(v["nums"]))


def lcm(v):
    return math.lcm(*to_int_list(v["nums"]))


def square_root_int(v):
    n = to_int(v["n"])
    if n < 0:
        raise CalcError("No square root for negative numbers.")
    return math.isqrt(n)          # whole-number square root, like your SquareRoot()


def permutation(v):
    n, r = to_int(v["n"], "items available"), to_int(v["r"], "items arranged")
    if n < 0 or r < 0:
        raise CalcError("Both values must be 0 or more.")
    return math.perm(n, r)


# ---------- Power, exponential and logarithmic ----------

def cuberoot(v):
    x = to_num(v["n"])
    if hasattr(math, "cbrt"):      # Python 3.11+
        return math.cbrt(x)
    return math.copysign(abs(x) ** (1 / 3), x)


def exponential(v):                # e ** x
    try:
        return math.exp(to_num(v["n"], "power"))
    except OverflowError:
        raise CalcError("That power is too large.")


def exp_base2(v):                  # 2 ** x
    x = to_num(v["n"], "power")
    try:
        return math.exp2(x) if hasattr(math, "exp2") else 2.0 ** x
    except OverflowError:
        raise CalcError("That power is too large.")


def exp_minus_one(v):              # e ** x - 1
    try:
        return math.expm1(to_num(v["n"], "power"))
    except OverflowError:
        raise CalcError("That power is too large.")


def simple_log(v):                 # log of n with a chosen base
    n, base = to_num(v["n"]), to_num(v["base"], "base")
    if n <= 0:
        raise CalcError("Logarithm needs a number greater than 0.")
    if base <= 0 or base == 1:
        raise CalcError("Base must be greater than 0 and not equal to 1.")
    return math.log(n, base)


def log_one_plus(v):               # log(1 + x)
    x = to_num(v["n"])
    if x <= -1:
        raise CalcError("Number must be greater than -1.")
    return math.log1p(x)


def log_base2(v):
    n = to_num(v["n"])
    if n <= 0:
        raise CalcError("Logarithm needs a number greater than 0.")
    return math.log2(n)


def log_base10(v):
    n = to_num(v["n"])
    if n <= 0:
        raise CalcError("Logarithm needs a number greater than 0.")
    return math.log10(n)


def power(v):
    base, p = to_num(v["n"], "number"), to_num(v["p"], "power")
    try:
        return math.pow(base, p)
    except (OverflowError, ValueError):
        raise CalcError("Can't calculate that power.")


def square_root(v):                # decimal square root, like your squareroot()
    n = to_num(v["n"])
    if n < 0:
        raise CalcError("No square root for negative numbers.")
    return math.sqrt(n)


# ---------- Registry: the UI is built from this ----------
# field types: "int" (whole number), "num" (decimal ok), "list" (2+ whole numbers),
#              "choice" (pick one option, shown as a sliding toggle)

_two = [{"name": "n1", "label": "First number", "type": "int"},
        {"name": "n2", "label": "Second number", "type": "int"}]
_one = [{"name": "n", "label": "Number", "type": "num"}]
_one_int = [{"name": "n", "label": "Number", "type": "int"}]

OPERATIONS = {
    # ---- Arithmetic ----
    "addition": {"label": "Addition", "icon": "+", "category": "Arithmetic",
                 "desc": "Add two numbers.", "fields": _two, "fn": addition},
    "subtraction": {"label": "Subtraction", "icon": "−", "category": "Arithmetic",
                    "desc": "Subtract in whichever direction you want.",
                    "fields": _two + [{"name": "choice", "label": "Direction", "type": "choice",
                                       "options": [{"value": "1", "label": "1st − 2nd"},
                                                   {"value": "2", "label": "2nd − 1st"}]}],
                    "fn": subtraction},
    "multiplication": {"label": "Multiplication", "icon": "×", "category": "Arithmetic",
                       "desc": "Multiply two numbers.", "fields": _two, "fn": multiplication},
    "division": {"label": "Division", "icon": "÷", "category": "Arithmetic",
                 "desc": "Divide in whichever direction you want.",
                 "fields": _two + [{"name": "choice", "label": "Direction", "type": "choice",
                                    "options": [{"value": "1", "label": "1st ÷ 2nd"},
                                                {"value": "2", "label": "2nd ÷ 1st"}]}],
                 "fn": division},

    # ---- Number theory ----
    "combination": {"label": "Combination", "icon": "nCr", "category": "Number Theory",
                    "desc": "Ways to choose items from a set, order ignored.",
                    "fields": [{"name": "n", "label": "Total items in the set", "type": "int"},
                               {"name": "r", "label": "Items you select", "type": "int"}],
                    "fn": combination},
    "permutation": {"label": "Permutation", "icon": "nPr", "category": "Number Theory",
                    "desc": "Ways to choose and arrange items, order matters.",
                    "fields": [{"name": "n", "label": "Items available", "type": "int"},
                               {"name": "r", "label": "Items you select and arrange", "type": "int"}],
                    "fn": permutation},
    "factorial": {"label": "Factorial", "icon": "n!", "category": "Number Theory",
                  "desc": "Factorial of a number.", "fields": _one_int, "fn": factorial},
    "hcf": {"label": "HCF", "icon": "HCF", "category": "Number Theory",
            "desc": "Highest common factor of any amount of numbers.",
            "fields": [{"name": "nums", "label": "Numbers", "type": "list"}], "fn": hcf},
    "lcm": {"label": "LCM", "icon": "LCM", "category": "Number Theory",
            "desc": "Least common multiple of any amount of numbers.",
            "fields": [{"name": "nums", "label": "Numbers", "type": "list"}], "fn": lcm},
    "square_root_int": {"label": "Integer Sqrt (rounded down)", "icon": "⌊√⌋", "category": "Number Theory",
                        "desc": "Only the whole part of the root: √3 gives 1. For 1.732 use Square Root (√x).",
                        "fields": _one_int, "fn": square_root_int},

    # ---- Power, exponential, logarithm ----
    "square_root": {"label": "Square Root", "icon": "√x", "category": "Power & Log",
                    "desc": "Exact square root with decimals.", "fields": _one, "fn": square_root},
    "cuberoot": {"label": "Cube Root", "icon": "∛", "category": "Power & Log",
                 "desc": "Cube root of a number.", "fields": _one, "fn": cuberoot},
    "power": {"label": "Power", "icon": "xʸ", "category": "Power & Log",
              "desc": "Raise a number to a power.",
              "fields": [{"name": "n", "label": "Number", "type": "num"},
                         {"name": "p", "label": "Power", "type": "num"}], "fn": power},
    "exponential": {"label": "e to the power x", "icon": "eˣ", "category": "Power & Log",
                    "desc": "e raised to the power you enter.",
                    "fields": [{"name": "n", "label": "Power for e", "type": "num"}],
                    "fn": exponential},
    "exp_base2": {"label": "2 to the power x", "icon": "2ˣ", "category": "Power & Log",
                  "desc": "2 raised to the power you enter.",
                  "fields": [{"name": "n", "label": "Power for 2", "type": "num"}],
                  "fn": exp_base2},
    "exp_minus_one": {"label": "eˣ − 1", "icon": "eˣ−1", "category": "Power & Log",
                      "desc": "e**x − 1, accurate for small x.",
                      "fields": [{"name": "n", "label": "Power for e", "type": "num"}],
                      "fn": exp_minus_one},
    "simple_log": {"label": "Logarithm", "icon": "log", "category": "Power & Log",
                   "desc": "Logarithm of a number with any base.",
                   "fields": [{"name": "n", "label": "Number", "type": "num"},
                              {"name": "base", "label": "Base", "type": "num"}],
                   "fn": simple_log},
    "log_one_plus": {"label": "log(1 + x)", "icon": "ln(1+x)", "category": "Power & Log",
                     "desc": "Natural log of 1 plus your number.", "fields": _one,
                     "fn": log_one_plus},
    "log_base2": {"label": "Log base 2", "icon": "log₂", "category": "Power & Log",
                  "desc": "Logarithm with base 2.", "fields": _one, "fn": log_base2},
    "log_base10": {"label": "Log base 10", "icon": "log₁₀", "category": "Power & Log",
                   "desc": "Logarithm with base 10.", "fields": _one, "fn": log_base10},
}


def calculate(op_key, values):
    """Run an operation. Returns the answer as a string (keeps huge numbers exact)."""
    op = OPERATIONS.get(op_key)
    if op is None:
        raise CalcError("Unknown calculation.")
    try:
        result = op["fn"](values or {})
    except KeyError:
        raise CalcError("Please fill in every field.")
    except ZeroDivisionError:
        raise CalcError("Can't divide by zero bro 😎")
    except (ValueError, OverflowError) as e:
        if isinstance(e, CalcError):
            raise
        raise CalcError("That input can't be calculated.")
    return str(result)


def public_operations():
    """Operations without the Python functions, safe to send to the browser."""
    return [{"key": k, **{f: v for f, v in op.items() if f != "fn"}}
            for k, op in OPERATIONS.items()]
