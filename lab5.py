import streamlit as st
import openai
import requests
from openai import OpenAI

def get_current_weather(location):
    if "," in location:
        location = location.split(",")[0].strip()
    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={st.secrets['weather_key']}"
    url = urlbase + urlweather
    response = requests.get(url)
    data = response.json()
    # Extract temperatures & Convert Kelvin to Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']
    return {"location": location,
            "temperature": round(temp, 2),
            "feels_like": round(feels_like, 2),
            "temp_min": round(temp_min, 2),
            "temp_max": round(temp_max, 2),
            "humidity": round(humidity, 2)
            }

if 'client' not in st.session_state:
    api_key = st.secrets["openai_key"]
    st.session_state.client = OpenAI(api_key=api_key)

def get_clothing_suggestion(weather_data):
    prompt = (f"The weather in {weather_data['location']} is currently the"
              f"temperature of {weather_data['temperature']}°C, feels like {weather_data['feels_like']}°C. "
              "What should I wear today? Also, is it a good day for a picnic?")
    
    # OpenAI API call for clothing suggestions
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit app interface
st.title("What to Wear Bot")

# User input for city
city = st.text_input("Enter a city:", value="Syracuse, NY")

# Get weather data
weather_data = get_current_weather(city)

if 'error' not in weather_data:
    # Display weather data
    st.write(f"Weather in {weather_data['location']}")
    st.write(f"Temperature: {weather_data['temperature']}°C, Feels like: {weather_data['feels_like']}°C")
    st.write(f"Humidity: {weather_data['humidity']}%")

    # Get clothing suggestion from OpenAI
    clothing_suggestion = get_clothing_suggestion(weather_data)
    st.write(clothing_suggestion)
else:
    st.write(weather_data['error'])