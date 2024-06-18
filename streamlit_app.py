#import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    
    """)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name of the Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        fv_data = fruityvice_response.json()
        st.write(fv_data)  # Display the API response to inspect its structure

        # If API response contains image URL, display it, else use placeholder
        image_url = fv_data.get('image_url', 'https://via.placeholder.com/150')
        st.image(image_url, caption=fruit_chosen)

    ingredients_string = ingredients_string.strip()  # Remove trailing space
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered! {name_on_order}", icon="✅")
