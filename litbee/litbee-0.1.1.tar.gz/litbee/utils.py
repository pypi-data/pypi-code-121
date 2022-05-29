"""Prep front cover for sidebar (based on st-bumblebee-st_app.py)."""
from textwrap import dedent

import logzero
import streamlit as st
from logzero import logger
from set_loglevel import set_loglevel

from litbee import __version__

logzero.loglevel(set_loglevel())

msg = dedent(
    """
    What would you like to do?
    The following alignment engines are available.

    **UFast-Engine**: ultra-fast, based on a home-brewed algorithm, faster than blazing fast but can only process en-zh para/sent pairs, not as sophisticated as DL-Engine;

    **SFast-Engine**: super-fast, based on machine translation;

    **Fast-Engine**: based on yet another home-brewed algorithm, blazing fast but can only process en-zh para/sent pairs;

    **DL-Engin**: based on machine learning, multilingual, one para/sent takes about 1s.
    """
).strip()
msg = dedent(
    """
    * ezbee: english-chinese, fast para-align

    * dzbee: german-chinese, fast para-align

    * debee: german-english, fast para-align

    * xbee/bumblebee: other language pairs, normal para-align

    The algorithm for fast para-align is home-brewn. Two sent-align algorithms are used: one based on Gale-Church, the other machine learning.
    """
).strip()


def sb_front_cover():
    """Prep front cover for sidebar"""
    st.sidebar.markdown(f"### litbee {__version__} ")

    sb_tit_expander = st.sidebar.expander("More info (click to toggle)", expanded=False)
    with sb_tit_expander:
        # st.write(f"Showcasing v.{__version__}, refined, quasi-prodction-ready🚧...")
        # branch
        # st.markdown(
        st.markdown(msg)


intructins = dedent(
    f"""
    *   Set up options in the left sidebar

    *   Click expanders / +: to reveal more details; -: to hide them

    *   Press '**Click to start aligning**' to get the ball rolling. (The button will appear when everything is ready.)

    *   litbee v.{__version__} from mu@qq41947782's keyboard in cyberspace. Join **qq group 316287378** for feedback and questions or to be kept updated. litbee is a member of the bee family.
    """
).strip()


def instructions():
    logger.debug("instructions entry")
    back_cover_expander = st.expander("Instructions")
    with back_cover_expander:
        st.markdown(intructins)

    logger.debug("instructions exit")


about_msg = dedent(
    f"""
    # litbee {__version__}

    https://bumblebee.freeforums.net/thread/5/litbee or head to 桃花元 （qq group 316287378）
    """
).strip()

menu_items = {
    "Get Help": "https://bumblebee.freeforums.net/thread/5/litbee",
    "Report a bug": "https://github.com/ffreemt/litbee/issues",
    "About": about_msg,
}
