def navigate(
    location,
    new_tab=False,
    external=False
):
    return {
        "method": "navigate",
        "params": [location, new_tab, external]
    }
