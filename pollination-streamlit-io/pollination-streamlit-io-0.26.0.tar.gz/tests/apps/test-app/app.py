import streamlit as st

from pollination_streamlit_io import (button, 
    inputs,
    special)

# get the platform from the query uri
query = st.experimental_get_query_params()
platform = special.get_host()

if platform == 'rhino':
    # special controls
    # just one!
    st.subheader('Pollination Token for Sync')
    po_token = special.sync(key='pollination-special-sync',
        delay=5000)
    st.write(po_token)

    # common controls
    length = st.slider('Change segment length',
        min_value=1,
        max_value=50,
        value=10)

    # common controls
    st.subheader('Pollination, Get Geometry Button')
    geometry = button.get(key='pollination-button-get-01')
    if geometry:
        st.write(geometry)
    
    st.subheader('Pollination, Get Pollination Model Button Sync')
    model = button.get(is_pollination_model=True,
        sync_token=po_token,
        key='pollination-button-get-02')
    if model:
        st.write(model)

    st.subheader('Pollination, Get Pollination Model Button')
    model = button.get(is_pollination_model=True, 
        key='pollination-button-get-03')
    if model:
        st.write(model)

    st.subheader('Pollination, Bake Geometry Button')

    data_to_pass = [{
            'type': 'Mesh3D',
            'vertices': [(0, 0, 0), (10, 0, 0), (0, 10, 0)],
            'faces': [(0, 1, 2)],
            'colors': [{'r': 255, 'g': 0, 'b': 0}]
        }, 
        { 
            'type': 'Polyline2D',
                'vertices': [[0, 0], [10, 0], [0, 10]] 
        }]

    option = st.selectbox(
        'What command do you want to use?',
            (
                'BakeGeometry', 
                'ClearGeometry', 
                'DrawGeometry', 
                'DisableDraw', 
                'WrongCommand'
            )
        )
    command_active = button.send(option,
        data_to_pass, 'unique-id-01', 
        options={'layer':'StreamlitLayer', 'units': 'Feet'}, 
        key='pollination-button-send-01')
    st.write('Command in action: %s !' % command_active)
        
    st.write(data_to_pass)

    st.subheader('Pollination, Display Checkbox')

    # text_input = st.text_input(label='Type a', value='a')
    # if text_input == 'a':

    # prepare legend
    legend = {
        'type': 'LegendScreen',
        'x': '50',
        'y': '50',
        'height': '600',
        'width': '25',
        'min': 0,
        'max': 100,
        'num': 8,
        'font': 17,
        'colors': [{'r': '255', 'g': '0', 'b': '0' },
            {'r': '0', 'g': '255', 'b': '255' }, 
            {'r': '12', 'g': '123', 'b': '255' }, 
            {'r': '0', 'g': '255', 'b': '0' }]
    }

    dynamic_input = { 
        'type': 'Polyline2D',
        'vertices': [[0, 0], [10, 0], [0, length]],
        'color': {'r':255, 'g':0, 'b':0} 
        }
    inputs.send(data=dynamic_input,
        label='GO!',
        default_checked=True,
        unique_id='unique-id-02', 
        options={'layer':'StreamlitLayer'}, 
        key='pollination-inputs-send-02')

    data_model = model if model else '{}'

    command_model = button.send(
        'BakePollinationModel',
        data_model, 
        'unique-id-03', 
        key='pollination-button-send-02')

    st.subheader('Pollination, Command Button')

    name_input = st.text_input('Enter the command here!', 
        value='Line')
    command = button.command(
        command_string=name_input, 
        key='pollination-button-command-01')
    st.write(command)
