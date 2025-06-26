import streamlit as st
import pandas as pd
import numpy as np
from st_audiorec import st_audiorec
import librosa
import io
import matplotlib.pyplot as plt
import altair as alt
import requests
import logging


logging.basicConfig(
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

URL_BASE = "https://your.hf.space"

logger.debug(URL_BASE)

def generate_mel_spectrogram(audio_data, sr=16000):
    if audio_data is None:
        return None
    
    try:
        y = np.frombuffer(audio_data, np.int16).astype(np.float32) / 32768.0
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)

        fig, ax = plt.subplots(figsize=(6, 3))
        img = librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', ax=ax, cmap='magma')
        ax.set(title="Mel Spectrogram")
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        buf.seek(0)
        plt.close(fig)
        return buf
    
    except Exception as e:
        st.error(f"Error generating spectrogram : {str(e)}")
        return None

def generate_donuts(name, value, color):
    source = pd.DataFrame({
        'category': [name, 'Other'],
        'value': [value, 100 - value],
        'color': [color, '#E0E0E0']
    })

    chart = alt.Chart(source).mark_arc(innerRadius=70).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="color", type="nominal", scale=None),
        tooltip=["category", "value"]
    ).properties(width=200, height=200)

    central_text = alt.Chart(pd.DataFrame({
        "text": [f"{name}\n{value:.0f}%"]
    })).mark_text(
        align='center',
        baseline='middle',
        fontSize=16,
        fontWeight='bold'
    ).encode(
        text='text:N'
    )

    return chart + central_text

def display_waveform(audio_data):
    try:
        if audio_data is None:
            return None
        
        y = np.frombuffer(audio_data, np.int16).astype(np.float32)
        fig, ax = plt.subplots(figsize=(12, 6))
        librosa.display.waveshow(y, sr=16000, alpha=0.8, ax=ax)
        ax.set_title("Audio Waveform")
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude")
        ax.grid(True)

        return fig
    except Exception as e:
        st.error(f"Erreur : {e}")
        return None

def get_predict(wav_audio_data):
    """
    Send audio file to get prediction
    """
    if wav_audio_data is None:
        st.error("No audio file.")
        return None
        
    try:
        audio_size = len(wav_audio_data)
        if audio_size == 0:
            st.error("Audio file is empty.")
            return None
            
        files = {
            'file': ('audio.wav', wav_audio_data, 'audio/wav')
        }
        
        with st.spinner('Loading...'):
            response = requests.post(
                f"{URL_BASE}/predict_basemodel",
                files=files,
            )
        logger.debug(f"API Response status: {response.status_code}")
        if response.status_code == 200:
            try:
                prediction = response.json()
                logger.info(f"Successful prediction: {prediction}")
                return prediction
                
            except ValueError as e:
                st.error(f"JSON format error: {str(e)}")
                return None
        else:
            st.error(f"Something goes wrong: (code {response.status_code})")
            return None
            
    except Exception as e:
        st.error(f"Something goes wrong: {str(e)}")
        return None

# Page Config
st.set_page_config(page_title="Echocare", page_icon="🗣️", layout="wide")

# Init session variables 
if 'input_mode' not in st.session_state:
    st.session_state.input_mode = 'record'
if 'is_validate' not in st.session_state:
    st.session_state.is_validate = False

# Layout
row1 = st.columns(1)
row2_left, row2_center, row2_right = st.columns(3)
row3 = st.columns(1)

# Sidebar
with st.sidebar:
    st.header('🗣️Echocare')

# Main content
with row1[0]:
    card = st.container(height=200)
    card.write("""
    ### Please start recording and read this text or load audio file(.wav)

    Whispers of the Wind
    Beneath the sky, so vast, so blue,
    The wind hums songs, both old and new.
    It tells of trees that swayed with grace,
    And dreams once held in time's embrace.

    The rivers laugh, the mountains sigh,
    The stars blink softly in the sky.
    Each note, a memory to share,
    A gentle kiss of nature’s care.

    So pause and listen, let it be,
    The whispers of eternity.    
    """)    

with row2_left:
    card = st.container()
    card.subheader("Audio Controls")
   
    # Toggle button record or upload
    mode = card.radio("Choose input mode:", ["Record", "Upload"], key="input_mode_radio", horizontal=True)
    st.session_state.input_mode = mode.lower()

    wav_audio_data = None
    
    if st.session_state.input_mode == 'record':
        
        wav_audio_data = card.container()
        wav_audio_data = st_audiorec()
        
        if card.button("Validate"):
            st.session_state.is_validate = not st.session_state.is_validate
    
    else:  # Mode upload
        uploaded_file = card.file_uploader("Upload audio file", type=['wav'], key="audio_uploader")
        if uploaded_file is not None:
            wav_audio_data = uploaded_file.read()
            st.session_state.is_validate = True
            card.audio(wav_audio_data, format='audio/wav')

with row2_center:
    card = st.container()
    card.subheader("Waveform")
    if wav_audio_data and st.session_state.is_validate:
        fig = display_waveform(wav_audio_data)
        if fig:
            card.pyplot(fig)
            plt.close(fig) 
    else:
        st.info("No audio wave available. Record or upload an audio to view.")

with row2_right:
    card = st.container()
    card.subheader("Spectrogram")
    if wav_audio_data and st.session_state.is_validate:
        spectrogram_buf = generate_mel_spectrogram(wav_audio_data)
        if spectrogram_buf:
            st.image(spectrogram_buf, use_container_width=True)
    else:
        st.info("No audio wave available. Record or upload an audio to view.")

with row3[0]:
    card = st.container()
    card.subheader("Prediction")

    if wav_audio_data and st.session_state.is_validate:
        data = get_predict(wav_audio_data)
        
        if data is not None:
            try:
                control = round(data["prediction"][0] * 100, 2)
                mci = round(data["prediction"][1] * 100, 2)
                adrd = round(data["prediction"][2] * 100, 2)

                chart_data = [
                    {"name": "Control", "value": control, "color": "#8884d8"},
                    {"name": "MCI", "value": mci, "color": "#82ca9d"},
                    {"name": "ADRD", "value": adrd, "color": "#ffc658"}
                ]

                prediction_cols = card.columns(3)
                for col, data in zip(prediction_cols, chart_data):
                    with col:
                        chart = generate_donuts(data["name"], data["value"], data["color"])
                        st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                card.error(f"Error while processing predictions : {str(e)}")
        else:
            card.error("Unable to get prediction. Please check API connection or audio quality.")
    else:
        card.info("No audio wave available. Record or upload an audio to view.")