# import streamlit as st
# import pandas as pd

# @st.cache_data
# def load_history_data():
#     # Replace with your historical wildfire data file
#     return pd.read_csv("historical_wildfire_data.csv")

# historical_data = load_history_data()
# st.markdown('<div id="history" class="stHeader">History</div>', unsafe_allow_html=True)
# st.header("Historical Data")
# # st.write(historical_data)

# # Display historical data in a table
# st.subheader("Wildfire Events Over the Years")
# st.dataframe(historical_data, use_container_width=True)
import streamlit as st
import pandas as pd

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

@st.cache_data
def load_history_data():
    # Replace with your historical wildfire data file
    return pd.read_csv("historical_wildfire_data.csv")

historical_data = load_history_data()
# st.markdown('<div id="history" class="stHeader">History</div>', unsafe_allow_html=True)
st.header("Historical Data")

# Display historical data in a table with full width
st.subheader("Wildfire Events Over the Years")
st.dataframe(historical_data, use_container_width=True)
