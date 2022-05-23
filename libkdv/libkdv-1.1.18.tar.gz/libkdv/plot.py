def plot(result,config=None):
    import matplotlib.pyplot as plt
    from keplergl import KeplerGl
    if config is not None:
        map_1 = KeplerGl(height=500,show_docs=False,config=config)
    else:
        map_1 = KeplerGl(height=500,show_docs=False)
    map_1.add_data(data=result,name='data_1')
    return map_1