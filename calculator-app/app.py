"""
app.py - Flask backend for the calculator.
Run:  python app.py   then open http://127.0.0.1:5000
"""
from flask import Flask, jsonify, request, send_from_directory
from calculator_logic import CalcError, calculate, public_operations

app = Flask(__name__, static_folder="static", static_url_path="")


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/operations")
def operations():
    """The frontend asks for the list of calculations and builds its buttons from it."""
    return jsonify(public_operations())


@app.post("/api/calculate")
def api_calculate():
    data = request.get_json(silent=True) or {}
    op_key = data.get("operation", "")
    values = data.get("values", {})
    try:
        result = calculate(op_key, values)
    except CalcError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "result": result})


if __name__ == "__main__":
    # Port 5000 is used by macOS AirPlay Receiver, so default to 5001.
    # To use another port: PORT=8000 python app.py
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="127.0.0.1", port=port, debug=True)
