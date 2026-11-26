import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json
import os

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Website Visitor Prediction",
    page_icon="📊",
    layout="wide"
)

# ---------------- DARK THEME ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080d1b, #111a30);
    color: white;
}

[data-testid="stSidebar"] {
    background: #101a30;
}

h1, h2, h3 {
    color: #ffffff !important;
}

p, label {
    color: #b8c5dc !important;
}

div[data-testid="stMetric"] {
    background: #1b2944;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #304467;
}

div[data-testid="stMetricValue"] {
    color: #48c6ef;
}

.stButton button {
    background: #2878f0;
    color: white;
    border-radius: 8px;
    border: none;
    width: 100%;
}

.stButton button:hover {
    background: #1558c0;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    return pd.read_csv("website_visitors.csv")


@st.cache_resource
def load_model():
    if os.path.exists("visitor_model.pkl"):
        return joblib.load("visitor_model.pkl")
    return None


@st.cache_data
def load_metrics():
    if os.path.exists("metrics.json"):
        with open("metrics.json", "r") as file:
            return json.load(file)
    return {}


try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()

model = load_model()
metrics = load_metrics()


# ---------------- HEADER ----------------

st.markdown("""
# 📊 Website Visitor Prediction

### AI Powered Website Traffic Analytics Dashboard

Monitor website traffic, explore visitor trends
and predict future website visitors.
""")

st.divider()


# ---------------- SIDEBAR ----------------

st.sidebar.markdown("# 🚀 VISITOR AI")
st.sidebar.markdown("### Analytics Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "📈 Analytics",
        "🤖 Visitor Prediction",
        "📋 Dataset",
        "ℹ️ About"
    ]
)

st.sidebar.divider()
st.sidebar.success("System Online")
st.sidebar.caption("Website Visitor Prediction v1.0")


# ---------------- COMMON DATA ----------------

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

target_candidates = [
    "Visitor_Count",
    "visitor_count",
    "Visitors",
    "visitors"
]

target = next(
    (c for c in target_candidates if c in df.columns),
    None
)

if target is None and numeric_columns:
    target = numeric_columns[0]

total_records = len(df)

total_visitors = (
    df[target].sum()
    if target else 0
)

total_features = len(df.columns)

numeric_features = len(numeric_columns)


# ---------------- OVERVIEW ----------------

if page == "🏠 Overview":

    st.subheader("📌 Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Visitors",
        f"{total_visitors:,.0f}"
    )

    c2.metric(
        "Total Records",
        f"{total_records:,}"
    )

    c3.metric(
        "Total Features",
        total_features
    )

    c4.metric(
        "Numeric Features",
        numeric_features
    )

    st.divider()

    st.subheader("📊 Website Visitor Analytics")

    if target:
        fig = px.histogram(
            df,
            x=target,
            title="Visitor Distribution",
            template="plotly_dark",
            color_discrete_sequence=["#48c6ef"]
        )

        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dataset Information")
        st.write("Total Rows:", total_records)
        st.write("Total Columns:", total_features)
        st.write("Missing Values:", int(df.isnull().sum().sum()))

    with col2:
        st.subheader("ML Model Status")

        if model is not None:
            st.success("Prediction Model Loaded")
        else:
            st.warning("Prediction model not found")

        st.write("Dataset Status: Loaded")


# ---------------- ANALYTICS ----------------

elif page == "📈 Analytics":

    st.title("📈 Website Traffic Analytics")

    if target:

        fig = px.box(
            df,
            y=target,
            title="Visitor Count Distribution",
            template="plotly_dark",
            color_discrete_sequence=["#00c6ff"]
        )

        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(
            df,
            x=df.index,
            y=target,
            title="Visitor Trends",
            template="plotly_dark",
            color_discrete_sequence=["#8a5cf6"]
        )

        st.plotly_chart(fig2, use_container_width=True)

    if len(numeric_columns) >= 2:

        st.subheader("Feature Correlation")

        corr = df[numeric_columns].corr()

        fig3 = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Correlation Heatmap",
            template="plotly_dark"
        )

        st.plotly_chart(fig3, use_container_width=True)


# ---------------- PREDICTION ----------------

elif page == "🤖 Visitor Prediction":

    st.title("🤖 AI Visitor Prediction")

    st.write(
        "Enter the website information to predict visitor count."
    )

    if model is None:

        st.error(
            "visitor_model.pkl not found. "
            "Please check your model file."
        )

    else:

        model_features = getattr(
            model,
            "feature_names_in_",
            None
        )

        if model_features is not None:
            features = list(model_features)
        else:
            features = [
                c for c in numeric_columns
                if c != target
            ]

        if not features:

            st.warning("No suitable input features found.")

        else:

            with st.form("prediction_form"):

                st.subheader("Enter Prediction Details")

                input_values = {}

                cols = st.columns(2)

                for i, feature in enumerate(features):

                    default = float(
                        pd.to_numeric(
                            df[feature],
                            errors="coerce"
                        ).median()
                    )

                    if not np.isfinite(default):
                        default = 0.0

                    with cols[i % 2]:

                        input_values[feature] = st.number_input(
                            feature.replace("_", " "),
                            value=default
                        )

                submitted = st.form_submit_button(
                    "🚀 Predict Visitors"
                )

            if submitted:

                try:

                    input_df = pd.DataFrame(
                        [input_values],
                        columns=features
                    )

                    prediction = model.predict(input_df)

                    st.divider()

                    st.success("Prediction Completed!")

                    st.metric(
                        "Predicted Website Visitors",
                        f"{float(prediction[0]):,.2f}"
                    )

                except Exception as e:

                    st.error(
                        f"Prediction Error: {e}"
                    )


# ---------------- DATASET ----------------

elif page == "📋 Dataset":

    st.title("📋 Website Visitor Dataset")

    st.write("Dataset Preview")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("Missing Values")

    missing = df.isnull().sum()

    st.dataframe(
        missing.rename("Missing Values"),
        use_container_width=True
    )

    st.subheader("Statistical Summary")

    st.dataframe(
        df.describe(),
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Dataset",
        data=csv,
        file_name="website_visitors.csv",
        mime="text/csv"
    )


# ---------------- ABOUT ----------------

elif page == "ℹ️ About":

    st.title("ℹ️ About This Project")

    st.markdown("""
    ### Website Visitor Prediction System

    This project uses Machine Learning to analyze
    website traffic and predict visitor counts.

    **Technologies Used**

    - Python
    - Streamlit
    - Pandas
    - NumPy
    - Scikit-learn
    - Plotly
    - Joblib

    **Main Features**

    - Professional Dark Dashboard
    - Website Traffic Analytics
    - Visitor Prediction
    - Dataset Visualization
    - Data Statistics
    - CSV Download
    """)

    st.info(
        "Developed using Python and Machine Learning."
    )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "© 2026 Website Visitor Prediction | AI Analytics Dashboard"
)