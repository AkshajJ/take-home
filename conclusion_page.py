import streamlit as st

class ConclusionPage:

    def load_project_conclusiom():
        with open('docs/project_conclusion.md', 'r') as file:
            project_intro_text = file.read()
        st.markdown(project_intro_text )

    