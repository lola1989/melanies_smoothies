import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """)

name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your Smoothie will be: ', name_on_order)

# Get the current credentials
cnx = st.connection("snowflake")
session = cnx.session()

# Show Fruit options from FRUIT_OPTIONS Table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)


# Fruit Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# Fruit Selection Stored in Orders Table
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
      # Display smoothiefroot nutrition information
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("(https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)  
        sf_df = st.dataframe(data=smoothiefroot_response.json(). use_containter_width=True)

    #st.write(ingredients_string)
  
    # Insert Name_On_Order and Ingredients into DB
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.stop()
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
      

