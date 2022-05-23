from importlib.util import find_spec


if find_spec('streamlit') is None:
    raise ImportError(
        "\n  Streamlit not found! The lumipy.streamlit module requires streamlit to be installed."
        "\n  Can be installed with 'pip install streamlit'."
        "\n  For more information go to https://streamlit.io"
    )
else:
    from lumipy.streamlit.utility_functions import (
        get_atlas,
        run_and_report,
        use_full_width,
        Reporter
    )
