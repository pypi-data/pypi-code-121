import os
import streamlit as st
import streamlit.components.v1 as components

_RELEASE = False

if not _RELEASE:
    _custom_notification_box = components.declare_component(
        
        "custom_notification_box",

        url="http://localhost:3001",
    )
else:

    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _custom_notification_box = components.declare_component("custom_notification_box", path=build_dir)


def custom_notification_box(icon, textDisplay, externalLink, url, styles, key=None, defaultIndex=0):

    return _custom_notification_box(icon=icon, 
                                            textDisplay=textDisplay, 
                                            externalLink=externalLink, 
                                            url=url, 
                                            styles=styles,
                                            key=key, 
                                            default=defaultIndex)


#custom_notification_box(icon='info', textDisplay='We are almost done with your registration.', externalLink='more info', url='#', styles=None, key="foo")

def callback():
    return custom_notification_box(icon='info', textDisplay='We are almost done with your registration.', externalLink='more info', url='#', styles=None, key="fo") #st.session_state['button'] = True #t.warning("hi")
    
test_1 = st.button("Test 1", on_click=callback)

#callback()
st.write(test_1)
if test_1:
    st.write("hi")
