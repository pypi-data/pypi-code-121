import streamlit as st
import ktrain
from cached_path import cached_path

_MODEL_PATH = (
    "https://github.com/PathwayCommons/pathway-abstract-classifier/releases/download/"
    "pretrained-models/title_abstract_model.zip"
)


# Function to load predictor, cache to improve performance
@st.cache(allow_output_mutation=True, max_entries=1)
def loadpredictor():

    model_path = cached_path(_MODEL_PATH, extract_archive=True)
    model = ktrain.load_predictor(model_path)
    return model


if __name__ == "__main__":
    # Visual/interactive elements
    st.title("Determine if Article is Suitable for Biofactoid")
    title = st.text_input("Enter title here")
    abstract = st.text_area("Enter abstract here", height=300)

    predictor = loadpredictor()
    # Load sep token expected by transformer/predictor
    sep_token = predictor.preproc.get_tokenizer().sep_token

    if st.button("Submit"):
        input = " ".join([title, sep_token, abstract])
        if predictor.predict(input):
            st.write("This article is likely suitable for Biofactoid")
            st.write("Certainty: {}".format(predictor.predict_proba(input)[1]))
        else:
            st.write("This article is likely not suitable for Biofactoid")
