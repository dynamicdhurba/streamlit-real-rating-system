# check_rerun.py

import streamlit as st

def check_streamlit_attributes():
    attributes = dir(st)
    if 'experimental_rerun' in attributes:
        print("experimental_rerun is available in this version of Streamlit.")
    else:
        print("experimental_rerun is NOT available in this version of Streamlit.")

if __name__ == "__main__":
    check_streamlit_attributes()
