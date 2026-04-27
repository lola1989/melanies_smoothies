import streamlit as st
import requests
import pandas as pd
import time
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize your Smoothie!")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """)

# ← ADD: Initialize session state defaults
IF 'name_on_order' not IN st.session_state:
    st.session_state['name_on_order'] = ''
IF 'ingredients_list' not IN st.session_state:
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
IF ingredients_list:
    ingredients_string = ''

    FOR fruit_chosen IN ingredients_list:
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

    IF time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
        time.sleep(2)
        del st.session_state['name_on_order']
        del st.session_state['ingredients_list']
        st.rerun()
      

