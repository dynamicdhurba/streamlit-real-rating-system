# generate_report.py

import pandas as pd
import streamlit as st

def calculate_score(response):
    if "Unable" in response:
        return 0
    elif "Seldom (25%)" in response:
        return 1
    elif "Occasionally (50%)" in response:
        return 2
    elif "Frequently (75%)" in response:
        return 3

def generate_report(responses):
    # Convert the session state responses to a DataFrame
    response_df = pd.DataFrame([
        {"Category": category, "Question No": question_no, "Response": response}
        for (category, question_no), response in responses.items()
    ])

    # Apply the score calculation function to the responses
    response_df['Score'] = response_df['Response'].apply(calculate_score)

    # Define the total possible scores for each category
    total_possible_scores = {
        "Dressing": 60,
        "Hygiene and Grooming": 60,
        "Feeding": 39,
        "Toileting": 33,
        "Other Functional Mobility": 30,
        "Housework/Chores": 42,
        "Managing Money and Shopping": 24,
        "Meal Preparation": 24,
        "Personal Safety": 39,
        "Travelling": 21,
        "School-Related Skills": 24
    }

    # Sum the scores for each category
    category_scores = response_df.groupby('Category')['Score'].sum().reset_index()

    # Add the total possible scores to the category scores dataframe
    category_scores['Total Possible Score'] = category_scores['Category'].apply(lambda x: total_possible_scores.get(x, 0))

    # Calculate the raw score percentage
    category_scores['Raw Score'] = category_scores['Score'].astype(str) + '/' + category_scores['Total Possible Score'].astype(str)

    # Display the report table using Streamlit
    st.title("Activities of Daily Living (ADL) and Instrumental Activities of Daily Living (IADL) Report")

    # Define the categories for each domain
    adl_categories = ["Dressing", "Hygiene and Grooming", "Feeding", "Toileting", "Other Functional Mobility"]
    iadl_categories = ["Housework/Chores", "Managing Money and Shopping", "Meal Preparation", "Personal Safety", "Travelling", "School-Related Skills"]

    # Display ADL Self-Care Domain
    st.subheader("Activities of Daily Living (ADL) Self-Care Domain")
    adl_scores = category_scores[category_scores['Category'].isin(adl_categories)]
    st.table(adl_scores[['Category', 'Raw Score']])

    # Display IADL Home and Community Domain
    st.subheader("Instrumental Activities of Daily Living (IADL) Home and Community Domain")
    iadl_scores = category_scores[category_scores['Category'].isin(iadl_categories)]
    st.table(iadl_scores[['Category', 'Raw Score']])
