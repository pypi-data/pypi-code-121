import pandas as pd

progtemp_config = pd.DataFrame(
    {
    'mode': ['MOS']*3 + ['LIFU']*3 + ['mIFU']*3,
    'resolution': ['low', 'high', 'high']*3,
    'red_vph': [1, 2, 2]*3,
    'blue_vph': [1, 2, 3]*3
    }, index=range(1, 10)
)
