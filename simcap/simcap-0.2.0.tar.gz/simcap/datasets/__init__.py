# -*- coding: utf-8 -*-

import pandas as pd
from importlib import resources

__all__ = [
    "load_example_asset_price_history",
    "load_example_external_factors",
    "load_example_prototypes",
    "load_all_example_data",
]


CSV_MODULE = "simcap.datasets.csv"


def load_example_asset_price_history():
    """
    Example dataset includes daily closing prices (adjusted for dividends and splits) 
    for the following Exchange Traded Funds (ETFs) over a 2517-day period:

    * SPY — SPDR S&P 500 ETF Trust
    * VO — Vanguard Mid-Cap Index Fund ETF
    * IWM — iShares Russell 2000 ETF
    * EFA — iShares MSCI EAFE ETF
    * VWO — Vanguard Emerging Markets Stock Index Fund ETF
    * AGG — iShares Core US Aggregate Bond ETF
    * IBND — SPDR Bloomberg International Corporate Bond ETF
    * VNQ — Vanguard Real Estate Index Fund ETF

    Returns
    -------
    asset_price_history : pandas DataFrame
    
    Examples
    --------
    >>> asset_price_history = load_example_asset_price_history()
    >>> print(asset_price_history.head)
              SPY         VO        IWM  ...        AGG       IBND        VNQ
    0  106.796135  64.467972  66.440186  ...  86.689796  29.319653  39.604931
    1  107.976936  65.523827  67.623489  ...  86.580055  29.563057  39.880756
    2  108.546638  65.999840  68.041145  ...  86.438980  29.675386  40.035488
    3  108.951248  65.800781  68.084663  ...  86.219429  29.675386  40.284424
    4  108.670502  65.913300  67.997643  ...  86.148888  29.946869  40.479504

    """
    with resources.open_text(CSV_MODULE, "asset_price_history.csv") as csv_file:
        asset_price_history = pd.read_csv(csv_file)
    return asset_price_history


def load_example_external_factors():
    """
    Example dataset includes daily values for the following indices over a 2517-day 
    period:

    * ^FVX — Treasury Yield 5 Years
    * ^TNX — Treasury Yield 10 Years
    * ^TYX — Treasury Yield 30 Years
    * ^VIX — CBOE Volatility Index
    
    Note
    ----
    The 2517-day period represented in this dataset is the same 2517-day period 
    represented in the example asset price history dataset.

    Returns
    -------
    external_factors : pandas DataFrame
    
    Examples
    --------
    >>> external_factors = load_example_external_factors()
    >>> print(external_factors.head)
        ^FVX   ^TNX   ^TYX       ^VIX
    0  0.778  1.850  2.891  22.200001
    1  0.804  1.897  2.954  20.889999
    2  0.851  1.972  3.039  19.870001
    3  0.891  2.028  3.101  18.280001
    4  0.911  2.067  3.146  18.670000

    """
    with resources.open_text(CSV_MODULE, "external_factors.csv") as csv_file:
        external_factors = pd.read_csv(csv_file)
    return external_factors


def load_example_prototypes():
    """
    Example prototype data are daily closing prices (adjusted for dividends and splits) 
    for the following Mutual Funds:

    * VFINX — Vanguard 500 Index Fund Investor Shares
    * VIMSX — Vanguard Mid-Cap Index Fund Investor Shares
    * NAESX — Vanguard Small Capitalization Index Fund Investor Shares
    * VTMGX — Vanguard Developed Markets Index Fund Admiral Shares
    * VEIEX — Vanguard Emerging Markets Stock Index Fund Investor Shares
    * VBMFX — Vanguard Total Bond Market Index Fund Investor Shares
    * PIGLX — PIMCO Global Bond Opportunities Fund (Unhedged) Institutional Class
    * VGSIX — Vanguard Real Estate Index Fund Investor Shares
    
    Each of these prototypes is an element in an a list and has also been given a label 
    based on its asset class:
    
    * VFINX — `'US_large_cap'`
    * VIMSX — `'US_mid_cap'`
    * NAESX — `'US_small_cap'`
    * VTMGX — `'foreign_developed'`
    * VEIEX — `'emerging_markets'`
    * VBMFX — `'total_bond'`
    * PIGLX — `'global_bond'`
    * VGSIX — `'real_estate'`

    Returns
    -------
    prototypes : list of pandas Series
        The list of prototype data.
    prototype_labels : list
        Asset class labels for each element in the prototypes list.
        
    Examples
    --------
    >>> from simcap.datasets import load_example_prototypes
    >>> prototypes, labels = load_example_prototypes()
    >>> us_large_cap = prototypes[labels.index('US_large_cap')]
    print(us_large_cap.head())
    0    4.675410
    1    4.652592
    2    4.711279
    3    4.724318
    4    4.818870
    Name: US_large_cap, dtype: float64
    
    >>> import pandas as pd
    >>> periods = [len(proto) for proto in prototypes]
    >>> periods = pd.DataFrame({'PROTOTYPE': labels, 'DAYS OF HISTORY': periods})
    >>> print(periods)
               PROTOTYPE  DAYS OF HISTORY
    0   emerging_markets             6967
    1  foreign_developed             5632
    2        global_bond             6442
    3        real_estate             6455
    4         total_bond             8836
    5       US_large_cap            10592
    6         US_mid_cap             5944
    7       US_small_cap            10592
    
    """
    files = [
        "proto_emerging_markets.csv",
        "proto_foreign_developed.csv",
        "proto_global_bond.csv",
        "proto_real_estate.csv",
        "proto_total_bond.csv",
        "proto_US_large_cap.csv",
        "proto_US_mid_cap.csv",
        "proto_US_small_cap.csv",
    ]
    prototypes = list()
    prototype_labels = list()
    for file in files:
        with resources.open_text(CSV_MODULE, file) as csv_file:
            prototypes.append(pd.read_csv(csv_file).iloc[:, 0])
            prototype_labels.append(file[6:-4])
    return prototypes, prototype_labels


def load_all_example_data():
    """
    Loads example data from each of the following methods:
        
    * `load_example_asset_price_history`
    * `load_example_external_factors`
    * `load_example_prototypes`

    Returns
    -------
    asset_price_history : pandas DataFrame

    external_factors : pandas DataFrame

    prototypes : list of pandas Series

    prototype_labels : list
    
    Examples
    --------
    >>> from simcap.datasets import load_all_example_data
    >>> assets, ext_factors, protos, labels = load_all_example_data()
    >>> print(assets.head())
              SPY         VO        IWM  ...        AGG       IBND        VNQ
    0  106.796135  64.467972  66.440186  ...  86.689796  29.319653  39.604931
    1  107.976936  65.523827  67.623489  ...  86.580055  29.563057  39.880756
    2  108.546638  65.999840  68.041145  ...  86.438980  29.675386  40.035488
    3  108.951248  65.800781  68.084663  ...  86.219429  29.675386  40.284424
    4  108.670502  65.913300  67.997643  ...  86.148888  29.946869  40.479504
    
    >>> print(ext_factors.head())
        ^FVX   ^TNX   ^TYX       ^VIX
    0  0.778  1.850  2.891  22.200001
    1  0.804  1.897  2.954  20.889999
    2  0.851  1.972  3.039  19.870001
    3  0.891  2.028  3.101  18.280001
    4  0.911  2.067  3.146  18.670000
    
    >>> us_large_cap = protos[labels.index('US_large_cap')]
    >>> print(us_large_cap.head())
    0    4.675410
    1    4.652592
    2    4.711279
    3    4.724318
    4    4.818870
    Name: US_large_cap, dtype: float64
    

    """
    asset_price_history = load_example_asset_price_history()
    external_factors = load_example_external_factors()
    prototypes, prototype_labels = load_example_prototypes()
    return asset_price_history, external_factors, prototypes, prototype_labels
