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

    # Calculate raw ADL and IADL scores
    adl_categories = ["Dressing", "Hygiene and Grooming", "Feeding", "Toileting", "Other Functional Mobility"]
    iadl_categories = ["Housework/Chores", "Managing Money and Shopping", "Meal Preparation", "Personal Safety", "Travelling", "School-Related Skills"]

    adl_score = category_scores[category_scores['Category'].isin(adl_categories)]['Score'].sum()
    iadl_score = category_scores[category_scores['Category'].isin(iadl_categories)]['Score'].sum()

    # Gender-specific pronoun
    pronoun = 'him' if user_details['child_sex'] == 'Male' else 'her'
    pronoun_possessive = 'his' if user_details['child_sex'] == 'Male' else 'her'

    # Create the summary text
    summary_text = (
        f"{user_details['child_first_name']}'s parents, {user_details['person_completing_form']}, would like {pronoun} to become more independent in self-care and home and community skills. "
        f"{pronoun_possessive.capitalize()} raw ADL score was {adl_score}. "
        "Her standard score was less than 81.7 (lowest available score), and her percentile rank was less than 1%, which indicates a delay in self-care abilities compared to her peers. "
        f"{pronoun_possessive.capitalize()} raw IADL score was {iadl_score}. "
        "Her standard score was less than 84.8 (the lowest available score), and her percentile was less than 1%, which again indicates a delay in in-home and community skills."
    )

    st.write(f"The REAL (The Roll Evaluation of Activities of Life) was completed by {user_details['person_completing_form']} ({user_details['relationship_to_child']}).")

    
    st.write("The REAL (The Roll Evaluation of Activities of Life) is a useful screening instrument to help assess children's self-care abilities at home, at school, and in the community. This standardised rating scale provides information on the activities of daily living (ADLs) and instrumental activities of daily living (IADLs).")
    
    # Display the report table using Streamlit
    st.title("Activities of Daily Living (ADL) and Instrumental Activities of Daily Living (IADL) Report")

    # Display ADL Self-Care Domain
    st.subheader("Activities of Daily Living (ADL) Self-Care Domain")
    adl_scores = category_scores[category_scores['Category'].isin(adl_categories)]
    st.table(adl_scores[['Category', 'Score', 'Raw Score']])

    # Display IADL Home and Community Domain
    st.subheader("Instrumental Activities of Daily Living (IADL) Home and Community Domain")
    iadl_scores = category_scores[category_scores['Category'].isin(iadl_categories)]
    st.table(iadl_scores[['Category', 'Score', 'Raw Score']])

    # Display the REAL Interpretation summary
    st.subheader("REAL Interpretation:")
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
