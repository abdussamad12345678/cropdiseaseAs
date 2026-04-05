import requests
import streamlit as st

API_KEY = "9f244592efe26bbd55cf0f9ddaeb63d6"

@st.cache_data(ttl=600)
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5)
        data = res.json()

        if "main" not in data:
            raise Exception("API Error")

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        rainfall = data.get("rain", {}).get("1h", 0)

        return temp, humidity, rainfall, "LIVE"

    except:
        return 28, 80, 12, "DEMO"

def get_coordinates(city):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        res = requests.get(url).json()
        return res[0]["lat"], res[0]["lon"]
    except:
        return 28.61, 77.23
