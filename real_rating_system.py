import streamlit as st
import pandas as pd

# Define the categories and their corresponding CSV files
categories = [
    ("Dressing", "files/Dressing.csv"),
    ("Hygiene and Grooming", "files/Hygiene_and_Grooming.csv")
]

# Initialize session state to track the current category, question index, and responses
if 'current_category_index' not in st.session_state:
    st.session_state.current_category_index = 0
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}

# Get the current category and load the corresponding CSV file
current_category_index = st.session_state.current_category_index
category_name, csv_file = categories[current_category_index]
df = pd.read_csv(csv_file)

# Streamlit app
st.title("The REAL Rating Form")

current_index = st.session_state.current_question_index
total_questions = len(df)

if current_index < total_questions:
    question_no = df.iloc[current_index]["no"]
    question_prompt = df.iloc[current_index]["question_prompt"]

    st.write(f"Category: {category_name}")
    st.write(f"Question {current_index + 1} of {total_questions}")
    st.write(f"{question_no}. {question_prompt}")

    response = st.radio(
        "",
        options=["0: Unable", "1: Seldom (25%)", "2: Occasionally (50%)", "3: Frequently (75%)"],
        key=f"q{category_name}_{question_no}",
    )

    if st.button("Next"):
        st.session_state.responses[(category_name, question_no)] = response
        st.session_state.current_question_index += 1
        # Set query params to force a rerun
        st.experimental_set_query_params(rerun=True)
else:
    st.write(f"You have completed the {category_name} category!")

    # Move to the next category if available
    if current_category_index + 1 < len(categories):
        if st.button("Next Category"):
            st.session_state.current_category_index += 1
            st.session_state.current_question_index = 0
            st.experimental_set_query_params(rerun=True)
    else:
        st.write("You have completed the entire survey!")

        # Display the responses
        st.write("Responses:")
        for (category, question_no), response in st.session_state.responses.items():
            st.write(f"Category: {category}, Question {question_no}: {response}")

        # Optionally, save the responses to a CSV file
        if st.button("Save Responses"):
            response_df = pd.DataFrame([
                {"Category": category, "Question No": question_no, "Response": response}
                for (category, question_no), response in st.session_state.responses.items()
            ])
            response_df.to_csv("responses.csv", index=False)
            st.write("Responses saved to responses.csv")

