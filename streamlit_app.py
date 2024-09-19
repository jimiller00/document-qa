import streamlit as st

lab_1 = st.Page("lab1.py", title = "Lab 1")
lab_2 = st.Page("lab2.py", title = "Lab 2")
lab_3 = st.Page("lab3.py", title = "Lab 3")
lab_4 = st.Page("lab4.py", title = "Lab 4")

pg = st.navigation([lab_1, lab_2, lab_3, lab_4])
st.set_page_config(page_title="test title",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
pg.run()