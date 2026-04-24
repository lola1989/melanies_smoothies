import streamlit as st
import requests
import pandas as pd
import time
import base64
from snowflake.snowpark.functions import col
from pathlib import Path

def set_background(image_path: str):
    img_data = Path(image_path).read_bytes()
    b64 = base64.b64encode(img_data).decode()
    ext = image_path.split(".")[-1]
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/{ext};base64,{b64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: top center;  /* ← anchors image to the top */
    }}
    .block-container {{
        background-color: rgba(255, 255, 255, 0.88);
        border-radius: 16px;
        padding: 2rem 2.5rem !important;
    }}
    /* Fix unreadable text in inputs */
    .stTextInput input {{
        background-color: white !important;
        color: #111111 !important;
    }}
    .stMultiSelect > div {{
        background-color: white !important;
        color: #111111 !important;
    }}
    p, label, .stMarkdown {{
        color: #111111 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

set_background("background.jpg")  # ← put your filename here

# Write directly to the app
st.title(f":cup_with_straw: Customize your Smoothie!")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """)

# ← ADD: Initialize session state defaults
if 'name_on_order' not in st.session_state:
    st.session_state['name_on_order'] = ''
if 'ingredients_list' not in st.session_state:
    st.session_state['ingredients_list'] = []
  
# ← ADD: key= parameter to both inputs  
name_on_order = st.text_input("Name on Smoothie:", key='name_on_order')
st.write('The name on your Smoothie will be: ', name_on_order)

# Get the current credentials
cnx = st.connection("snowflake")
session = cnx.session()

# Show Fruit options from FRUIT_OPTIONS Table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

# Convert Snowpart DF to a Pandas DF
pd_df=my_dataframe.to_pandas()
#st.stop()

# Fruit Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5,
    key='ingredients_list'
)

# Fruit Selection Stored in Orders Table
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
      
        # Display smoothiefroot nutrition information
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}") 
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
  
    # Insert Name_On_Order and Ingredients into DB
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.stop()
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
        time.sleep(5)
        del st.session_state['name_on_order']
        del st.session_state['ingredients_list']
        st.rerun()
      

