import os
from platform import platform
import streamlit.components.v1 as components
from typing import List, Optional, Union

__all__ = ['sync', 'settings']

_RELEASE = True

if not _RELEASE:
    _component_func_sync = components.declare_component(
        "sync",
        url="http://localhost:3001",
    )
    _component_func_settings = components.declare_component(
        "settings",
        url="http://localhost:3002",
    )
    _component_func_hbjson = components.declare_component(
        "settings",
        url="http://localhost:3003",
    )    
    _component_func_host = components.declare_component(
        "host",
        url="http://localhost:3004",
    )    
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "sync")
    _component_func_sync = components.declare_component("sync", path=build_dir)
    build_dir = os.path.join(parent_dir, "settings")
    _component_func_settings = components.declare_component("settings", path=build_dir)
    build_dir = os.path.join(parent_dir, "hbjson")
    _component_func_hbjson = components.declare_component("get_hbjson", path=build_dir) 
    build_dir = os.path.join(parent_dir, "host")
    _component_func_host = components.declare_component("get_host", path=build_dir) 

def sync(
    default_checked: bool=False,
    delay: Optional[int]=500,
    key: str =None) -> str:
    """Create a sync token generator.

    Parameters
    ----------
    default_checked: bool
        Set if it has to be checked by default.
    delay: int
        Delay of the syncronization in milliseconds.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    Returns
    -------
    str
        Sync token to connect to component to enable the syncronization.
    """
    component_value = _component_func_sync(
        default_checked=default_checked,
        delay=delay,
        key=key, 
        default=None)
    
    return component_value


def settings(
    data: dict,
    default_checked: bool=False,
    delay: Optional[int]=500,
    key: str =None) -> str:
    """Send/get settings to/from a CAD software.

    Parameters
    ----------
    data: dict or string. Dict to SET settings. String to GET settings.

        String MUST start with 'SETTINGS' keyword. You can use 'special.sync' output
        to generate a token when you change document info of the host software automatically.

        Dict MUST have following schema:
        data = {
                'earth_anchor': {
                    'lat': 41.2324,
                    'lon': 12.3234
                },
                units: 1,
                layers: ['Streamlit', 'JS', 'Python']
            }
        
        - Where Units mapping:
            - Millimeter = 2
            - Centimeter = 3
            - Meters = 4
            - Inches = 8
            - Feet = 9
        - layers array contains layers to create

    default_checked: bool
        Set if it has to be checked by default.
    delay: int
        Delay of the syncronization in milliseconds.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    
    return:
        if String as 'data' it returns JSON settings inside streamlit
        because it is in GET mode. Otherwise nothing.
    """
    component_value = _component_func_settings(
        data=data,
        default_checked=default_checked,
        delay=delay,
        key=key, 
        default=None)
    
    units = {
        2: 'Millimeter',
        3: 'Centimeter',
        4: 'Meters',
        8: 'Inches',
        9: 'Feet'
    }

    if component_value:
        out_unit = component_value.get('units')
        if not out_unit:
            return component_value
        
        component_value = { **component_value, 
            **{'units': units.get(out_unit)} }

    return component_value


def get_hbjson(
    delay: Optional[int]=500,
    key: str =None) -> str:
    """Get HBJSON file as json string (WIP).

    Parameters
    ----------
    delay: int
        Delay of the syncronization in milliseconds.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    Returns
    -------
    str
        HBJSON file.
    """
    component_value = _component_func_hbjson(
        delay=delay,
        key=key, 
        default=None)
    
    return component_value


def get_host(
    key: str =None) -> str:
    """Get host platform.

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    Returns
    -------
    str
        Name of the current platform.
    """
    component_value = _component_func_host(
        key=key, 
        default=None)
    
    return component_value

if not _RELEASE:
    import streamlit as st

    my_host = get_host(key='my-host-software')
    st.write(my_host)

    st.subheader("Sync Token in action")

    # just one component like this
    sync_token = sync(default_checked=True, 
        key='my-secret-key')
    st.write(sync_token)
    
    sync_token_2 = sync(default_checked=True, 
        key='my-secret-key-2')
    st.write(sync_token_2)


    data = {
            'earth_anchor': {
                'lat': 41.2324,
                'lon': 12.3234
            },
            'units': 2,
            'layers': ['Streamlit', 'JS']
        }

    test = settings(
        data=data,
        default_checked=True)
    st.write(test)

    my_model = get_hbjson(key='model-key')
    st.write(my_model)

    