from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    deflate_source_model import DeflateSourceModel

DEFLATE_META: dict = {
    'models': {
        DeflateSourceModel.__name__: {
            'public': True,
            # Accepts any input attributes
            'any_inputs': True,
            # Parameters for create()
            'params': ['backend_model_dto'],
            # For queries via get_data(), set_data() is used to issue commands
            'attrs': [
                # output
                'bool',
                'float',
                'int',
                'str',
                'dict',
                'None',
            ]
        }
    }
}
