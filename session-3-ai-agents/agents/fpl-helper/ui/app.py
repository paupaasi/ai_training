#!/usr/bin/env python3
"""Flask UI for FPL Helper Agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    category = data.get("category", "transfer")

    if category == "captain":
        return jsonify({
            "top_picks": [
                {"player": "Salah", "reason": "Top form, good fixtures"},
                {"player": "Haaland", "reason": "Premium pick"},
                {"player": "Saka", "reason": "Good ownership, great fixtures"}
            ]
        })
    elif category == "transfer":
        return jsonify({
            "buy": [
                {"player": "Palmer", "price": 6.5, "reason": "High value"},
                {"player": "Saka", "price": 9.5, "reason": "Premium option"}
            ],
            "sell": [
                {"player": "Underperformer", "reason": "Low form"}
            ]
        })
    elif category == "chips":
        return jsonify({
            "wildcard": "GW32-35",
            "bench_boost": "GW33 or GW36",
            "free_hit": "Blank GW",
            "triple_captain": "Double GW"
        })

    return jsonify({"message": "Unknown category"})


@app.route("/api/squad", methods=["GET", "POST"])
def squad():
    if request.method == "POST":
        data = request.get_json()
        return jsonify({"status": "saved"})
    else:
        return jsonify({"players": [], "message": "No squad saved"})


@app.route("/api/injuries")
def injuries():
    return jsonify({
        "injuries": [
            {"player": "Check Premier League website", "status": "Unknown"}
        ]
    })


def main():
    print("Starting FPL Helper UI...")
    app.run(host="0.0.0.0", port=5002, debug=True)


if __name__ == "__main__":
    main()