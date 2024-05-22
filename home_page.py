import streamlit as st

class HomePage:

    def load_project_intro():
        with open('docs/project_intro.md', 'r') as file:
            project_intro_text = file.read()
        st.markdown(project_intro_text )

    