import os
from typing import List, Optional, Union

import streamlit.components.v1 as components

_RELEASE = True
COMPONENT_NAME = "streamlit_fb_post"

if _RELEASE:  # use the build instead of development if release is true
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, "frontend/build")

    _streamlit_fb_post = components.declare_component(
        COMPONENT_NAME,
        path = build_dir
    )
else:
    _streamlit_fb_post = components.declare_component(
        COMPONENT_NAME,
        url = "http://localhost:3000"
    )

def post(text: str, 
         legend: str,
         link: str,
         picture: Optional[Union[List[str], str]] = None,
         key: Optional[str] = None):
    """Create a facebook post.

    Args:
        text (str): The text of the post.
        picture (Optional[Union[List[str], str]], optional): The images that we want to render. Defaults to None.
        key (Optional[str], optional): A unique key for the component. Defaults to None.
    """
    _streamlit_fb_post(text=text, picture=picture, legend=legend, link=link, key=key)


if not _RELEASE:
    post("Happy birthday to the main character in our family!", legend="25 feb", link="https://www.facebook.com/", picture="https://scontent-cdg2-1.xx.fbcdn.net/v/t39.30808-6/278578494_5384646104881436_4922253203700321374_n.jpg?_nc_cat=100&ccb=1-5&_nc_sid=0debeb&_nc_ohc=BC56DTddwCsAX-37NyT&_nc_ht=scontent-cdg2-1.xx&oh=00_AT-jvreQ3HnnuWI-Igk7I4BD3sBuFlBWoaI2yoGqonmSaw&oe=626F1A6B")
