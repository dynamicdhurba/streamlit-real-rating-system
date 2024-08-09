import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

def calculate_score(response):
    if "Unable" in response:
        return 0
    elif "Seldom (25%)" in response:
        return 1
    elif "Occasionally (50%)" in response:
        return 2
    elif "Frequently (75%)" in response:
        return 3

def generate_report(responses, user_details):
    # Convert the session state responses to a DataFrame
    response_df = pd.DataFrame([
        {"Domain": domain, "Category": category, "Question No": question_no, "Response": response}
        for (domain, category, question_no), response in responses.items()
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
        "Housework Chores": 42,
        "Managing Money and Shopping": 24,
        "Meal Preparation": 24,
        "Personal Safety": 39,
        "Traveling": 21,
        "School Related Skills": 24,
        "Personal Care Devices": 6,
        "Female Dressing": 6
    }

    # Sum the scores for each category
    category_scores = response_df.groupby('Category')['Score'].sum().reset_index()

    # Add the total possible scores to the category scores dataframe
    category_scores['Total Possible Score'] = category_scores['Category'].apply(lambda x: total_possible_scores.get(x, 0))

    # Calculate the raw score percentage
    category_scores['Raw Score'] = category_scores['Score'].astype(str) + '/' + category_scores['Total Possible Score'].astype(str)

    # Calculate total raw scores for ADL and IADL
    adl_categories = ["Dressing", "Hygiene and Grooming", "Feeding", "Toileting","Female Dressing", "Other Functional Mobility"]
    iadl_categories = ["Housework Chores", "Managing Money and Shopping", "Meal Preparation", "Personal Safety", "Traveling", "School Related Skills"]

    adl_total_score = category_scores[category_scores['Category'].isin(adl_categories)]['Score'].sum()
    adl_total_possible = category_scores[category_scores['Category'].isin(adl_categories)]['Total Possible Score'].sum()
    adl_percentage = adl_total_score / adl_total_possible
    adl_total_raw_score = f"{adl_total_score}/{adl_total_possible}"

    iadl_total_score = category_scores[category_scores['Category'].isin(iadl_categories)]['Score'].sum()
    iadl_total_possible = category_scores[category_scores['Category'].isin(iadl_categories)]['Total Possible Score'].sum()
    iadl_percentage = iadl_total_score / iadl_total_possible
    iadl_total_raw_score = f"{iadl_total_score}/{iadl_total_possible}"

    # Custom CSS for emerald background and text color in table headers and total raw score section
    st.markdown(
        """
        <style>
        .emerald-header th {
            background-color: #009999 !important;
            color: white !important;
            font-weight: bold !important;
        }
        .emerald-score {
            background-color: #009999 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 5px;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the report table using Streamlit
    st.markdown(f"<p style='font-size: 24px; font-weight: 600;'>Activities of Daily Living (ADL) and Instrumental Activities of Daily Living (IADL) Report</p>", unsafe_allow_html=True)

    # Display ADL Self-Care Domain
    st.markdown(f"<p style='font-size: 20px; font-weight: 600;'>Activities of Daily Living (ADL) Self-Care Domain</p>", unsafe_allow_html=True)
    adl_scores = category_scores[category_scores['Category'].isin(adl_categories)]
    st.table(adl_scores[['Category', 'Raw Score']].style.set_table_styles([
        {'selector': 'thead', 'props': [('class', 'emerald-header')]}
    ]))

    # Display total ADL score with emerald background
    st.markdown(f"<div class='emerald-score'>**Total Raw Score**: {adl_total_raw_score}</div>", unsafe_allow_html=True)

    # Display IADL Home and Community Domain
    st.markdown(f"<p style='font-size: 20px; font-weight: 600;'>Instrumental Activities of Daily Living (IADL) Home and Community Domain</p>", unsafe_allow_html=True)
    iadl_scores = category_scores[category_scores['Category'].isin(iadl_categories)]
    st.table(iadl_scores[['Category', 'Raw Score']].style.set_table_styles([
        {'selector': 'thead', 'props': [('class', 'emerald-header')]}
    ]))

    # Display total IADL score with emerald background
    st.markdown(f"<div class='emerald-score'>**Total Raw Score**: {iadl_total_raw_score}</div>", unsafe_allow_html=True)

    # Generate the REAL Interpretation summary
    pronoun = 'he' if user_details['child_sex'] == 'Male' else 'she'
    pronoun_possessive = 'his' if user_details['child_sex'] == 'Male' else 'her'
    
    if adl_percentage >= 0.8 and iadl_percentage >= 0.8:
        summary_text = (
            f"{user_details['child_first_name']} is already independent in both self-care and home/community activities. "
            f"{pronoun.capitalize()} has a raw ADL score of {adl_total_raw_score} and a raw IADL score of {iadl_total_raw_score}."
        )
    elif adl_percentage >= 0.8:
        summary_text = (
            f"{user_details['child_first_name']} is independent in self-care activities with a raw ADL score of {adl_total_raw_score}. "
            f"However, {pronoun} needs to become more independent in home and community skills as indicated by {pronoun_possessive} raw IADL score of {iadl_total_raw_score}."
        )
    elif iadl_percentage >= 0.8:
        summary_text = (
            f"{user_details['child_first_name']} is independent in home and community activities with a raw IADL score of {iadl_total_raw_score}. "
            f"However, {pronoun} needs to become more independent in self-care skills as indicated by {pronoun_possessive} raw ADL score of {adl_total_raw_score}."
        )
    else:
        summary_text = (
            f"{user_details['child_first_name']} needs to become more independent in both self-care and home/community activities. "
            f"{pronoun.capitalize()} has a raw ADL score of {adl_total_raw_score} and a raw IADL score of {iadl_total_raw_score}."
        )

    st.markdown(f"<p style='font-size: 20px; font-weight: 600;'>REAL Interpretation:</p>", unsafe_allow_html=True)
    
    st.write(summary_text)
    st.write("Regards,")
    st.write(user_details['evaluating_therapist'])
    st.write("Occupational Therapist")

    # Serialize response_df and category_scores to JSON
    response_json = response_df.to_json(orient='records') 
    category_scores_json = category_scores.to_json(orient='records')
    user_details_json = str(user_details)

    # Log data to the browser console
    components.html(f"""
        <script>
            console.log('Response DataFrame:', {response_json});
            console.log('Category Scores:', {category_scores_json});
            console.log('User Details:', {user_details_json});
        </script>
    """, height=0)
