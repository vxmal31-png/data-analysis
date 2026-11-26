import json
import math
import os
from io import BytesIO

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "website_visitors.csv")
MODEL_PATH = os.path.join(BASE_DIR, "visitor_model.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "metrics.json")

app = Flask(__name__)


def load_data():
    return pd.read_csv(DATASET_PATH)


def load_model():
    return joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None


def load_metrics():
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def get_target(df):
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    for candidate in ("Visitor_Count", "visitor_count", "Visitors", "visitors"):
        if candidate in df.columns:
            return candidate
    return numeric_columns[0] if numeric_columns else None


df = load_data()
model = load_model()
metrics = load_metrics()
target = get_target(df)
numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
model_features = (
    list(getattr(model, "feature_names_in_", []))
    if model is not None
    else []
)


def base_context(title, page):
    return {
        "title": title,
        "page": page,
        "model_loaded": model is not None,
        "record_count": len(df),
        "column_count": len(df.columns),
    }


@app.route("/")
def dashboard():
    total_visitors = float(df[target].sum()) if target else 0
    avg_visitors = float(df[target].mean()) if target else 0
    context = base_context("Overview", "dashboard")
    context.update({
        "total_visitors": total_visitors,
        "average_visitors": avg_visitors,
        "target": target,
        "missing_values": int(df.isna().sum().sum()),
    })
    return render_template("index.html", **context)


@app.route("/analytics")
def analytics():
    context = base_context("Visitor Analytics", "analytics")
    context["target"] = target
    return render_template("analytics.html", **context)


@app.route("/prediction")
def prediction():
    defaults = {}
    for feature in model_features:
        value = pd.to_numeric(df[feature], errors="coerce").median() if feature in df.columns else 0
        defaults[feature] = float(value) if pd.notna(value) else 0.0
    context = base_context("Visitor Prediction", "prediction")
    context.update({"features": model_features, "defaults": defaults})
    return render_template("prediction.html", **context)


@app.route("/dataset")
def dataset():
    context = base_context("Dataset", "dataset")
    context.update({
        "missing_values": df.isna().sum().to_dict(),
        "summary": df.describe(include="all").fillna("").to_dict(),
    })
    return render_template("dataset.html", **context)


@app.route("/performance")
def performance():
    context = base_context("Model Performance", "performance")
    context["metrics"] = metrics
    return render_template("performance.html", **context)


@app.route("/about")
def about():
    return render_template("about.html", **base_context("About", "about"))


@app.route("/api/predict", methods=["POST"])
def api_predict():
    if model is None:
        return jsonify({"error": "Prediction model is not available."}), 503
    if not model_features:
        return jsonify({"error": "The model has no readable feature contract."}), 422

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON request body is required."}), 400

    values = {}
    for feature in model_features:
        raw_value = payload.get(feature)
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return jsonify({"error": f"{feature} must be a valid number."}), 400
        if not math.isfinite(value):
            return jsonify({"error": f"{feature} must be a finite number."}), 400
        values[feature] = value

    try:
        input_df = pd.DataFrame([values], columns=model_features)
        prediction = float(model.predict(input_df)[0])
        if not math.isfinite(prediction):
            raise ValueError("The model returned a non-finite prediction.")
        return jsonify({
            "prediction": prediction,
            "prediction_display": f"{prediction:,.2f}",
            "features": values,
        })
    except Exception as exc:
        app.logger.exception("Prediction failed")
        return jsonify({"error": f"Prediction failed: {exc}"}), 422


@app.route("/api/chart-data")
def chart_data():
    records = df.copy()
    if target:
        records["__target"] = pd.to_numeric(records[target], errors="coerce")
    return jsonify({
        "dates": records["Date"].tolist() if "Date" in records else [],
        "visitors": records["__target"].fillna(0).tolist() if target else [],
        "target": records[target].dropna().tolist() if target else [],
        "target_name": target,
        "day_of_week": (
            records["Day_of_Week"].tolist()
            if "Day_of_Week" in records
            else []
        ),
        "correlation": (
            df[numeric_columns].corr().fillna(0).round(4).to_dict()
            if len(numeric_columns) >= 2
            else {}
        ),
    })


@app.route("/api/dataset")
def api_dataset():
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 25, type=int)))
    search = request.args.get("search", "").strip().lower()
    result = df.copy()
    if search:
        mask = result.astype(str).apply(
            lambda column: column.str.lower().str.contains(search, regex=False)
        ).any(axis=1)
        result = result[mask]

    total = len(result)
    start = (page - 1) * per_page
    end = start + per_page
    records = result.iloc[start:end].replace({np.nan: None}).to_dict(orient="records")
    return jsonify({
        "columns": list(result.columns),
        "records": records,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": max(1, math.ceil(total / per_page)),
    })


@app.route("/dataset/download")
def download_dataset():
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="website_visitors.csv",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)