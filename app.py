import streamlit as st
from docx import Document
import spacy
import pandas as pd

import spacy
import subprocess
import sys

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def is_functional_requirement(sentence):
    return 'shall' in sentence.text.lower()

def extract_function_parts(sentence):
    actor = action = obj = condition = ""
    for token in sentence:
        if token.dep_ == "nsubj":
            actor = token.text
        elif token.dep_ == "ROOT":
            action = token.lemma_
        elif token.dep_ in ("dobj", "attr", "prep"):
            obj = token.text
        elif token.dep_ == "advcl":
            condition = token.text
    return {
        "actor": actor,
        "action": action,
        "object": obj,
        "condition": condition,
        "raw_sentence": sentence.text
    }

def extract_functional_requirements(text):
    doc = nlp(text)
    return [
        extract_function_parts(sent)
        for sent in doc.sents if is_functional_requirement(sent)
    ]

st.title("Functional Requirement Extractor")
st.write("Upload a Word document (.docx) to extract functional requirements.")

uploaded_file = st.file_uploader("Choose a Word document", type="docx")

if uploaded_file is not None:
    with st.spinner("Processing..."):
        text = extract_text_from_docx(uploaded_file)
        extracted = extract_functional_requirements(text)
        df = pd.DataFrame(extracted)

    st.success(f"Extracted {len(df)} functional requirements.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "functional_requirements.csv", "text/csv")

    json = df.to_json(orient="records", indent=2)
    st.download_button("Download JSON", json, "functional_requirements.json", "application/json")
