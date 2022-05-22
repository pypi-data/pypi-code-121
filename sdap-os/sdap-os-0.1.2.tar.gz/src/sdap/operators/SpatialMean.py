import xarray
import numpy as np

class SpatialMean:

    def __init__(self):
        pass

    def consolidate(self, inputs: [xarray.DataArray]):

        combined_inputs = inputs[0]
        for i in range(len(inputs))[1:]:
            combined_inputs = combined_inputs.combine_first(inputs[i])

        # consolidate mean
        weights = combined_inputs['weight'].fillna(0)
        weighted_input = combined_inputs.weighted(weights)
        output_mean = weighted_input.mean(dim=['x', 'y'], skipna=True)
        del output_mean['weight']
        x_mean = combined_inputs.x.mean()
        y_mean = combined_inputs.y.mean()
        output_mean = output_mean.expand_dims(
            {
                'x': [x_mean],
                'y': [y_mean],
            }
        )

        request_x_mean = np.mean([input.request_x for input in inputs if 'request_x' in input.coords])
        request_y_mean = np.mean([input.request_y for input in inputs if 'request_y' in input.coords])
        output_mean.coords['request_x'] = (('x'), [request_x_mean])
        output_mean.coords['request_y'] = (('y'), [request_y_mean])

        # consolidate weights
        output_weights = combined_inputs['weight'].sum(dim=['x', 'y'], skipna=True)
        output_weights = output_weights.expand_dims(
            {
                'x': [x_mean],
                'y': [y_mean],
            }
        )
        output_counted_mean = xarray.Dataset()
        output_counted_mean = output_counted_mean.assign(var=output_mean['var'], weight=output_weights)

        return output_counted_mean

    def tile_calc(self, input: xarray.DataArray):
        # average the observation values
        output_mean = input.mean(dim=['x', 'y'])
        # set weights for averages, on the same grid
        # TODO check that this does not count also the nan values
        output_weights = input.count(dim=['x', 'y'])
        output_weights.name = 'weight'
        output = xarray.merge([output_mean, output_weights])

        x_mean = input.x.data.mean()
        y_mean = input.y.data.mean()
        output = output.expand_dims(
            {
                'x': [x_mean],
                'y': [y_mean],
            }
        )

        request_x_mean = input.request_x.data.mean()
        request_y_mean = input.request_y.data.mean()
        output.coords['request_x'] = (('x'), [request_x_mean])
        output.coords['request_y'] = (('y'), [request_y_mean])

        return output
