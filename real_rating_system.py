import streamlit as st
import pandas as pd

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

# Function to load CSV with specified encoding and handle errors
def load_csv_with_encoding(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8', encoding_errors='replace')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='latin1', encoding_errors='replace')
    except pd.errors.ParserError:
        st.error(f"Error parsing the file {file_path}. Please check the file format.")
        return pd.DataFrame()

# Get the current category and load the corresponding CSV file
current_category_index = st.session_state.current_category_index
domain_name, category_name, csv_file = categories[current_category_index]
df = load_csv_with_encoding(csv_file)

# Apply background color and text color
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
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app
st.title("The REAL Rating Form")

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

            # Display the responses
            st.write("Responses:")
            for (domain, category, question_no), response in st.session_state.responses.items():
                st.write(f"Domain: {domain}, Category: {category}, Question {question_no}: {response}")

            # Optionally, save the responses to a CSV file
            if st.button("Save Responses"):
                response_df = pd.DataFrame([
                    {"Domain": domain, "Category": category, "Question No": question_no, "Response": response}
                    for (domain, category, question_no), response in st.session_state.responses.items()
                ])
                response_df.to_csv("responses.csv", index=False)
                st.write("Responses saved to responses.csv")
else:
    st.error("The selected CSV file is empty or could not be loaded. Please check the file and try again.")
