import streamlit as st
import pandas as pd
from generate_report import generate_report
import streamlit.components.v1 as components

# Define the domains and their corresponding categories and CSV files
domains = {
    "Activities of Daily Living (ADL) Self-Care Domain": [
        ("Dressing", "files/ADL/Dressing.csv"),
        ("Feeding", "files/ADL/Feeding.csv"),
        ("Female Dressing", "files/ADL/Female_Dressing.csv"),
        ("Hygiene and Grooming", "files/ADL/Hygiene_and_Grooming.csv"),
        ("Other Functional Mobility", "files/ADL/Other_Functional_Mobility.csv"),
        ("Personal Care Devices", "files/ADL/Personal_Care_Devices.csv"),
        ("Toileting", "files/ADL/Toileting.csv")
    ],
    "Instrumental Activities of Daily Living (IADL) Home and Community Domain": [
        ("Housework Chores", "files/IADL/Housework_Chores.csv"),
        ("Managing Money and Shopping", "files/IADL/Managing_Money_and_Shopping.csv"),
        ("Meal Preparation", "files/IADL/Meal_Preparation.csv"),
        ("Personal Safety", "files/IADL/Personal_Safety.csv"),
        ("School Related Skills", "files/IADL/School_Related_Skills.csv"),
        ("Traveling", "files/IADL/Traveling.csv")
    ]
}

# Flatten the domains structure to make it easier to work with
categories = [(domain, cat_name, file) for domain, cats in domains.items() for cat_name, file in cats]

# Initialize session state to track the current domain, category, question index, and responses
if 'current_category_index' not in st.session_state:
    st.session_state.current_category_index = 0
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'child_first_name' not in st.session_state:
    st.session_state.child_first_name = ""
if 'child_last_name' not in st.session_state:
    st.session_state.child_last_name = ""
if 'person_completing_form' not in st.session_state:
    st.session_state.person_completing_form = ""
if 'relationship_to_child' not in st.session_state:
    st.session_state.relationship_to_child = ""
if 'evaluating_therapist' not in st.session_state:
    st.session_state.evaluating_therapist = ""
if 'child_sex' not in st.session_state:
    st.session_state.child_sex = ""

# Function to load CSV with specified encoding and handle errors
def load_csv_with_encoding(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8', encoding_errors='replace')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='latin1', encoding_errors='replace')
    except pd.errors.ParserError:
        st.error(f"Error parsing the file {file_path}. Please check the file format.")
        return pd.DataFrame()

# Function to save responses to CSV in real-time
def save_responses():
    response_df = pd.DataFrame([
        {"Domain": domain, "Category": category, "Question No": question_no, "Response": response}
        for (domain, category, question_no), response in st.session_state.responses.items()
    ])
    response_df.to_csv("responses.csv", index=False)

# Get the current category and load the corresponding CSV file
current_category_index = st.session_state.current_category_index
domain_name, category_name, csv_file = categories[current_category_index]
df = load_csv_with_encoding(csv_file)

# Apply custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stApp * {
        color: black !important;
    }
    .stButton>button {
        color: white !important;
    }
    input[type="text"], .stRadio>div>div {
        border: 1px solid gray !important;
        padding: 5px !important;
    }
    .stTextInput>div>label, .stRadio>div>label {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app
st.title("The REAL Rating Form")

# User details form
if not st.session_state.form_submitted:
    with st.form(key='user_details_form'):
        st.write("Please fill out the following details before starting the survey:")
        
        st.session_state.child_first_name = st.text_input("Child's First Name", placeholder="Please enter data here")
        st.session_state.child_last_name = st.text_input("Child's Last Name", placeholder="Please enter data here")
        st.session_state.person_completing_form = st.text_input("Person Completing the Form", placeholder="Please enter data here")
        st.session_state.relationship_to_child = st.radio("Relationship to Child", options=["Parent", "Caregiver"], index=None)
        st.session_state.evaluating_therapist = st.text_input("Evaluating Therapist", placeholder="Please enter data here")
        st.session_state.child_sex = st.radio("Child's Sex", options=["Male", "Female"], index=None)
        
        form_submit_button = st.form_submit_button("Start Survey")

        if form_submit_button:
            st.session_state.form_submitted = True
            # Add JavaScript to reload the page
            st.write('<script>window.location.reload()</script>', unsafe_allow_html=True)

else:
    if not df.empty:
        current_index = st.session_state.current_question_index
        total_questions = len(df)

        if current_index < total_questions:
            question_no = df.iloc[current_index]["no"]
            question_prompt = df.iloc[current_index]["question_prompt"]

            with st.form(key='question_form'):
                st.write(f"Domain: {domain_name}")
                st.write(f"Category: {category_name}")
                st.write(f"Question {current_index + 1} of {total_questions}")
                st.write(f"{question_no}. {question_prompt}")

                response = st.radio(
                    "",
                    options=["0: Unable", "1: Seldom (25%)", "2: Occasionally (50%)", "3: Frequently (75%)"],
                    key=f"q{domain_name}_{category_name}_{question_no}",
                )

                submit_button = st.form_submit_button("Next")

            if submit_button:
                st.session_state.responses[(domain_name, category_name, question_no)] = response
                st.session_state.current_question_index += 1
                save_responses()  # Save responses in real-time
                # Add JavaScript to reload the page
                st.write('<script>window.location.reload()</script>', unsafe_allow_html=True)

        else:
            st.write(f"You have completed the {category_name} category!")

            # Move to the next category if available
            if current_category_index + 1 < len(categories):
                if st.button("Next Category"):
                    st.session_state.current_category_index += 1
                    st.session_state.current_question_index = 0
                    st.write('<script>window.location.reload()</script>', unsafe_allow_html=True)
            else:
                st.write("You have completed the entire survey!")

    # Always show the "View Report" button
    if st.button("View Report"):
        user_details = {
            'child_first_name': st.session_state.child_first_name,
            'child_last_name': st.session_state.child_last_name,
            'person_completing_form': st.session_state.person_completing_form,
            'relationship_to_child': st.session_state.relationship_to_child,
            'evaluating_therapist': st.session_state.evaluating_therapist,
            'child_sex': st.session_state.child_sex
        }
        generate_report(st.session_state.responses, user_details)
        # Log the user details to the browser console
        components.html(f"""
            <script>
                console.log({user_details});
            </script>
        """, height=0)

# Save responses in real-time without requiring a button click
save_responses()
