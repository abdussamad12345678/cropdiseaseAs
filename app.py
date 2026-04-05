import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from PIL import Image
import folium
from streamlit_folium import st_folium
import time

from utils import get_weather, get_coordinates

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="PragyanAI Pro", layout="wide")

st.title("🌾 PragyanAI Crop Intelligence System")

# -------------------------------
# MODEL
# -------------------------------
MODEL_FILE = "model.pkl"

def train_model():
    data = pd.read_csv("data.csv")
    X = data[["temperature", "humidity", "rainfall"]]
    y = data["disease"]

    model = RandomForestClassifier()
    model.fit(X, y)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)

    return model

def load_model():
    if not os.path.exists(MODEL_FILE):
        return train_model()
    return pickle.load(open(MODEL_FILE, "rb"))

model = load_model()

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("⚙️ Control Panel")

city = st.sidebar.text_input("📍 Location", "Delhi")
crop = st.sidebar.selectbox("🌾 Crop", ["Rice", "Wheat", "Corn"])
stage = st.sidebar.selectbox("🌱 Growth Stage", ["Seedling", "Vegetative", "Flowering", "Harvest"])

if st.sidebar.button("🚀 Analyze"):

    with st.spinner("Fetching data..."):

        temp, humidity, rainfall, source = get_weather(city)

        # -------------------------------
        # METRICS
        # -------------------------------
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡 Temp", f"{temp}°C")
        col2.metric("💧 Humidity", f"{humidity}%")
        col3.metric("🌧 Rainfall", f"{rainfall} mm")

        st.caption(f"Source: {source}")

        # -------------------------------
        # PREDICTION
        # -------------------------------
        prob = model.predict_proba([[temp, humidity, rainfall]])[0][1]

        st.subheader("⚠️ Risk Score")
        st.progress(int(prob * 100))

        if prob < 0.3:
            st.success("🟢 Low Risk")
        elif prob < 0.7:
            st.warning("🟡 Medium Risk")
        else:
            st.error("🔴 High Risk")
            st.write("💊 Spray recommended within 2–3 days")

        # -------------------------------
        # ALERT SYSTEM
        # -------------------------------
        st.subheader("🚨 Smart Alert")

        if prob > 0.7:
            st.error("High risk detected!")
        elif prob > 0.4:
            st.warning("Monitor crop daily")
        else:
            st.success("Crop safe")

        # -------------------------------
        # MAP
        # -------------------------------
        st.subheader("🌍 Risk Map")

        lat, lon = get_coordinates(city)

        m = folium.Map(location=[lat, lon], zoom_start=6)

        color = "green" if prob < 0.3 else "orange" if prob < 0.7 else "red"

        folium.Marker(
            [lat, lon],
            popup=f"Risk: {round(prob,2)}",
            icon=folium.Icon(color=color)
        ).add_to(m)

        st_folium(m, width=700)

# -------------------------------
# IMAGE ANALYSIS
# -------------------------------
st.subheader("📸 Leaf Image Detection")

file = st.file_uploader("Upload Image")

if file:
    img = Image.open(file)
    st.image(img, width=300)

    avg = np.array(img).mean()

    if avg < 100:
        st.error("Disease Detected")
    else:
        st.success("Healthy")

# -------------------------------
# DASHBOARD
# -------------------------------
st.subheader("📊 Analytics")

data = pd.read_csv("data.csv")

st.line_chart(data[["temperature", "humidity", "rainfall"]])
st.bar_chart(data["disease"].value_counts())

# -------------------------------
# REFRESH BUTTON
# -------------------------------
if st.button("🔄 Refresh"):
    time.sleep(1)
    st.rerun()

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.write("🚀 AI-powered crop advisory system")
