import streamlit as st

# Add a title and header to the page
st.title("My First Streamlit App")
st.header("Welcome to the interface!")

# Add interactive widgets
user_text = st.text_input("Enter some text:")
slider_val = st.slider("Select a value:", min_value=0, max_value=100, value=50)

# Display results
st.write(f"You entered: {user_text}")
st.write(f"Slider value: {slider_val}")

# Add a download button widget
st.download_button(
    label="Download text",
    data=user_text,
    file_name="output.txt",
    mime="text/plain"
)