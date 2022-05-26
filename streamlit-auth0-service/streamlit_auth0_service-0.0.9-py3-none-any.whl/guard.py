from streamlit_auth0_service.auth0_service import StreamlitAuth0Service
import streamlit as st


def authorized(func):
    def wrapper():
        auth_service = StreamlitAuth0Service()
        is_authorized = auth_service.is_authorized()

        if is_authorized:
            func()
        else:
            st.write("Unauthorized! Access Denied.")

    return wrapper


