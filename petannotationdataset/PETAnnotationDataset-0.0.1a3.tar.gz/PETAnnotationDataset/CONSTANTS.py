
PROCESS_ELEMENTS = [
                    'Activity',
                    'Activity Data',
                    'Further Specification',
                    'Condition Specification',
                    'Actor',
                    'XOR Gateway',
                    'AND Gateway',
                    ]

PROCESS_ANNOTATION_LAYERS = [
                    'Behavioral',
                    'Organizational',
                    'Activity Data',
                    'Further Specification'
                    ]

# { layer: list of process elements}
# this link the theoretical layers with the annotation layers
PROCESS_MODEL_LAYERS = {
                    'Behavioral': ['Activity', 'Further Specification', 'Condition Specification', 'XOR Gateway', 'AND Gateway'],
                    'Data Object': ['Activity Data'],
                    'Organizational': ['Actor']
                    }