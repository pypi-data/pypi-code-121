import xarray


class Identity:

    def __init__(self):
        pass

    def consolidate(self, inputs: [xarray.Dataset]):
        combined_inputs = inputs[0]
        for i in range(len(inputs))[1:]:
            combined_inputs = combined_inputs.combine_first(inputs[i])

        return combined_inputs

    def tile_calc(self, input: xarray.DataArray):
        return xarray.Dataset({'var': input})


