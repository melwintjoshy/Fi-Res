import csv
import requests
import streamlit as st
import pandas as pd
import datetime as dtt
import joblib
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime
from PIL import Image
# from model import predict_image
from pred_fire import predict_fire
from alertbot import send_telegram_notification

# Set page title and layout
st.set_page_config(page_title="Fi-Res", layout="wide")

# Custom CSS for improved visual appeal
st.markdown(
    """
    <style>
    /* Navbar styling */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #2c3e50;
        padding: 10px 20px;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .navbar a {
        color: white;
        text-decoration: none;
        margin: 0 15px;
        font-weight: bold;
    }
    .navbar a:hover {
        color: #1abc9c;
        text-decoration: none;
    }

    /* Metric card styling */
    .stMetric {
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric label {
        font-size: 14px;
        color: #7f8c8d;
    }
    .stMetric value {
        font-size: 24px;
        color: #2c3e50;
        font-weight: bold;
    }

    /* Section header styling */
    .stHeader {
        color: #C0C0C0 ;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Footer styling */
    .footer {
        text-align: center;
        padding: 20px;
        background-color: #2c3e50;
        color: white;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """
, unsafe_allow_html=True)

# Navigation bar
st.markdown(
    """
    <div class="navbar">
        <span>Fi-Res Disaster Monitoring Dashboard</span>
        <div>
            <a href="#home">Home</a>
            <a href="/Help_Bot">Help_Bot</a>
            <a href="/UAV_Stream">UAV Stream</a>
            <a href="/Historical_Data">Historical Data</a>
        </div>
    </div>
    """
, unsafe_allow_html=True)
with st.sidebar:
        custom_title = """
                        <h1 style="font-size: 50px; font-family: 'Helvetica', sans-serif;">Fi-Res</h1>
                       """
        st.markdown(custom_title, unsafe_allow_html=True)
        custom_title2 = """
                        <h3 style="font-size: 15px; font-family: 'Helvetica', sans-serif;">AI POWERED WILDFIRE DETECTION AND ALERT SYSTEM</h3>
                        """
        st.markdown(custom_title2, unsafe_allow_html=True)
        st.markdown("Detect Early, Respond Quickly")

# Load CSV data
@st.cache_data  # Cache the data to avoid reloading on every interaction
def load_data(csv):
    return pd.read_csv(csv)  # Replace with your CSV file path

# =================
# fetch real time data from 5 sources
def query(latlon: list):
    data = []

    for loc in latlon:
        API_URL = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": loc[0],
            "lon": loc[1],
            "appid": "b4ad38fe32d5825344e9884a205a94fc"
        }

        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            return {"error": f"Failed to fetch data: {response.status_code}", "details": response.text}
        
        res = response.json()

        datetime_object = dtt.datetime.fromtimestamp(int(res['dt']))
        formatted_datetime = datetime_object.strftime("%Y-%m-%dT%H:%M")

        data.append({
            'datetime': formatted_datetime,
            'temp': f"{float(res['main']['temp']) - 273.15:.2f}",
            'pressure': res['main']['pressure'],
            'humidity': res['main']['humidity'],
            'wind': res['wind']['speed'],
        })
    return data

def to_csv(json_data):
    # with open('furie.csv', 'w') as file:
    #     writer = csv.writer(file)
    #     writer.writerow([json_data[-1]['datetime'], json_data[-1]['temp'], json_data[-1]['pressure'], json_data[-1]['humidity'], json_data[-1]['wind']])
        
    # with open('proximity5.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["time", "temperature_2m", "surface_pressure", "relative_humidity_2m", "wind_speed_10m"])
    #     for row in json_data:
    #         writer.writerow([row['datetime'], row['temp'], row['pressure'], row['humidity'], row['wind']])

    with open('furie.csv', 'a', newline='') as file:  # 'a' mode appends to the file
        writer = csv.writer(file)
        
        # Append the latest entry from json_data
        writer.writerow([json_data[-1]['datetime'], json_data[-1]['temp'], json_data[-1]['humidity'], json_data[-1]['pressure'], json_data[-1]['wind']])


    with open('proximity5.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["time", "temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m"])
        
        for row in json_data:
            writer.writerow([row['datetime'], row['temp'], row['pressure'], row['humidity'], row['wind']])


latlon = [ 
    (34.069525, -118.575536),
    (34.067993, -118.560856),
    (34.079533, -118.571529),
    (34.079056, -118.554556),
    (34.0725, -118.5425)
]
res_q = query(latlon)
to_csv(res_q)

model = joblib.load("rfmodel1.pkl")
proximity_data = res_q[:-1]
# proximity_df = pd.DataFrame(proximity_data)
proximity_df = pd.DataFrame(proximity_data, columns=["time","temperature_2m","relative_humidity_2m","surface_pressure","wind_speed_10m"])

xtest = proximity_df.drop(columns=['time'])
ypred = model.predict(xtest)
ypred_labels = np.where(ypred == 1, "Low", "High")
# =================

csv = "furie.csv"
data = load_data(csv)
# data["time"] = data["time"].astype(str)

# Load satellite images (replace with actual file paths or URLs)
proximity_area_images = [ f"D:/hack/{i}.jpeg" for i in range(1,5)]
affected_area_image = r"D:\hack\1.jpeg"  # Replace with your image path

# Main content

# Section 1: Live Satellite Image and Real-Time Data
st.markdown("<h1 style='text-align: center;'>AFFECTED AREA MONITORING</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# Left column: Real-Time Data
with col1:
    st.subheader("Real-Time Data")

    # Fetch the latest row from the CSV file
    latest_data = data.iloc[-1]
    # print(latest_data)
    date_string = latest_data["time"]

    # Convert to datetime object
    dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M")
    formatted_datetime = dt.strftime("%Y-%m-%d %H:%M")

    st.metric(label="Time", value=f"{ formatted_datetime }")
    st.metric(label="Temperature", value=f"{latest_data['temperature_2m']:.2f}°C")
    st.metric(label="Surface Pressure", value=f"{latest_data['surface_pressure']:.2f} hPa") 
    st.metric(label="Humidity", value=f"{latest_data['relative_humidity_2m']:.2f}%")
    st.metric(label="Wind Speed", value=f"{latest_data['wind_speed_10m']:.2f} km/h")

# Right column: Live Satellite Image
with col2:
    st.subheader("Live Satellite Image")
    # st.image(affected_area_image, use_container_width=True, caption="Affected Area Satellite Image")
    image = r"D:\hack\valid\wildfire\-57.3633,51.4978.jpg"
    st.image(image, width = 550)
    prediction = predict_fire(image)
    if prediction == "Fire":
        st.error(f"**Prediction:** WILDFIRE DETECTED")
        bot_token = '7722089045:AAE8jSa8wDVSD4CX6Lf-CulEk8aFpxLUgLg'
        chat_id = ['617451765', '6288108679', '610643071', '1457915351']
        message = 'ALERT!!!. THERE HAS BEEN A FIRE OUTBREAK IN YOUR REGION.'
        for id in chat_id:
            send_telegram_notification(bot_token, id, message)

    else:
        st.success(f"**Prediction:** NO WILDFIRE DETECTED")

# Section 2: Charts for Temperature, Wind Speed, and Humidity
st.markdown('<div class="stHeader">Environmental Data Trends</div>', unsafe_allow_html=True)

# Generate charts from CSV data
data_last_20 = data.tail(70)

fig1, ax1 = plt.subplots()
ax1.plot(data_last_20["time"], data_last_20["temperature_2m"], color="#e74c3c")
ax1.set_title("Temperature Over Time", fontsize=14, color="#2c3e50")
ax1.set_xlabel("Time", fontsize=12, color="#7f8c8d")
ax1.set_ylabel("Temperature (°C)", fontsize=12, color="#7f8c8d")
# ax1.tick_params(axis="x", rotation=45)  # Rotate x-axis labels for better readability

fig2, ax2 = plt.subplots()
ax2.plot(data_last_20["time"], data_last_20["wind_speed_10m"], color="#3498db")
ax2.set_title("Wind Speed Over Time", fontsize=14, color="#2c3e50")
ax2.set_xlabel("Time", fontsize=12, color="#7f8c8d")
ax2.set_ylabel("Wind Speed (km/h)", fontsize=12, color="#7f8c8d")
# ax2.tick_params(axis="x", rotation=45)

fig3, ax3 = plt.subplots()
ax3.plot(data_last_20["time"], data_last_20["relative_humidity_2m"], color="#2ecc71")
ax3.set_title("Humidity Over Time", fontsize=14, color="#2c3e50")
ax3.set_xlabel("Time", fontsize=12, color="#7f8c8d")
ax3.set_ylabel("Humidity (%)", fontsize=12, color="#7f8c8d")
# ax3.tick_params(axis="x", rotation=45)

fig4, ax4 = plt.subplots()
ax4.plot(data_last_20["time"], data_last_20["surface_pressure"], color="#f1c40f")
ax4.set_title("Surface Pressure Over Time", fontsize=14, color="#2c3e50")
ax4.set_xlabel("Time", fontsize=12, color="#7f8c8d")
ax4.set_ylabel("Surface Pressure", fontsize=12, color="#7f8c8d")
# ax4.tick_params(axis="x", rotation=45)

# Display charts in columns
col3, col4, col5, col6 = st.columns(4)
with col3:
    st.pyplot(fig1)
with col4:
    st.pyplot(fig2)
with col5:
    st.pyplot(fig3)
with col6:
    st.pyplot(fig4)

# Section 3: Proximity Region Satellite Image and Details
st.markdown('<div class="stHeader">Proximity Region Monitoring</div>', unsafe_allow_html=True)

col7_10 = st.columns([1, 1, 1, 1])

# Proximity Real-Time Data
for i in range(len(proximity_data)):
    with col7_10[i]:
        st.markdown("""<div class="card_card_card">""", unsafe_allow_html=True)
        img_str = proximity_area_images[i]

        date_string = proximity_data[i]["datetime"]
        dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M")
        formatted_datetime = dt.strftime("%Y-%m-%d %H:%M")

        st.image(img_str, use_container_width=True, caption="Affected Area Satellite Image")
        st.metric(label="Time", value=f"{formatted_datetime}")
        st.metric(label="Temperature", value=f"{proximity_data[i]['temp']}°C")
        st.metric(label="Surface Pressure", value=f"{proximity_data[i]['pressure']} hPa")
        st.metric(label="Humidity", value=f"{proximity_data[i]['humidity']}%")
        st.metric(label="Wind Speed", value=f"{proximity_data[i]['wind']} km/h")
        st.metric(label="Probability of Fire", value=f"{ypred_labels[i]}")
        

        
        st.markdown("""</div>""", unsafe_allow_html=True)

# with col7:

#     # st.subheader("Location Name")
#     st.image(proximity_area_image1, use_container_width=True, caption="Affected Area Satellite Image")
#     st.metric(label="Temperature", value=f"{proximity_data[0]['temp']}°C")
#     st.metric(label="Surface Pressure", value=f"{proximity_data[0]['pressure']} hPa")
#     st.metric(label="Humidity", value=f"{proximity_data[0]['humidity']}%")
#     st.metric(label="Wind Speed", value=f"{proximity_data[0]['wind']} km/h")
#     st.metric(label="Probability of Fire", value=f"{ypred_labels[0]}")

# with col8:
#     # st.subheader("Location Name")
#     st.image(proximity_area_image2, use_container_width=True, caption="Affected Area Satellite Image")
#     st.metric(label="Temperature", value=f"{proximity_data[1]['temp']}°C")
#     st.metric(label="Surface Pressure", value=f"{proximity_data[1]['pressure']} hPa")
#     st.metric(label="Humidity", value=f"{proximity_data[1]['humidity']}%")
#     st.metric(label="Wind Speed", value=f"{proximity_data[1]['wind']} km/h")
#     st.metric(label="Probability of Fire", value=f"{ypred_labels[1]}")

# with col9:
#     # st.subheader("Location Name")
#     st.image(proximity_area_image3, use_container_width=True, caption="Affected Area Satellite Image")
#     st.metric(label="Temperature", value=f"{proximity_data[2]['temp']}°C")
#     st.metric(label="Surface Pressure", value=f"{proximity_data[2]['pressure']} hPa")
#     st.metric(label="Humidity", value=f"{proximity_data[2]['humidity']}%")
#     st.metric(label="Wind Speed", value=f"{proximity_data[2]['wind']} km/h")
#     st.metric(label="Probability of Fire", value=f"{ypred_labels[2]}")

# with col10:
#     # st.subheader("Location Name")
#     st.image(proximity_area_image4, use_container_width=True, caption="Affected Area Satellite Image")
#     st.metric(label="Temperature", value=f"{proximity_data[3]['temp']}°C")
#     st.metric(label="Surface Pressure", value=f"{proximity_data[3]['pressure']} hPa")
#     st.metric(label="Humidity", value=f"{proximity_data[3]['humidity']}%")
#     st.metric(label="Wind Speed", value=f"{proximity_data[3]['wind']} km/h")
#     st.metric(label="Probability of Fire", value=f"{ypred_labels[3]}")


# Footer
st.markdown(
    """
    <div class="footer">
        © 2025 Fi-Res. All rights reserved.
    </div>
    """
, unsafe_allow_html=True)