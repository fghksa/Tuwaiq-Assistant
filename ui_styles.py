import streamlit as st

def load_styles():
    st.markdown(
        """
        <style>
        .rtl {
            direction: rtl;
            text-align: right;
            font-family: "Tahoma", "Arial", sans-serif;
            line-height: 1.8;
            font-size: 17px;
        }

        .center {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
