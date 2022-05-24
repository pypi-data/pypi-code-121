#!/usr/bin/env python
# coding: utf-8


def generate_augmento_simple(transform_featuress, los, magnitudes, nb_selecteds, leading_correlationss):
    parameters = []
    for transform_features in transform_featuress:
        for lo in los:
            for magnitude in magnitudes:
                for nb_selected in nb_selecteds:
                    for leading_correlations in leading_correlationss:
                        parameters.append({
                            'transform_features':transform_features,
                            'lo':lo,
                            'magnitude':magnitude,
                            'nb_selected':nb_selected,
                            'leading_correlations':leading_correlations
                        })
    return parameters

def generate_simple_baseline(thresholds, signal_action_types, mixing_types):
    parameters = []
    for threshold in thresholds:
        for signal_action_type in signal_action_types:
            for mixing_type in mixing_types:
                parameters.append({
                    'threshold': threshold,
                    'signal_action_type': signal_action_type,
                    'mixing_type': mixing_type,
                })
    return parameters

def generate_anova_like(signal_action_types, mixing_types):
    parameters = []
    for signal_action_type in signal_action_types:
        for mixing_type in mixing_types:
            parameters.append({
                'signal_action_type': signal_action_type,
                'mixing_type': mixing_type,
            })
    return parameters

def generate_past_perf_mod(looks, threshs,lows,highs):
    parameters = []
    for look in looks:
        for thresh in threshs:
            for low in lows:
                for high in highs:
                    parameters.append((look, thresh, high, low))
    return parameters

def generate_volume_strength(lags, middles, low_levs, high_levs, contravariants, colmuns, signals):
    parameters = []
    for lag in lags:
        for middle in middles:
            for low_lev in low_levs:
                for high_lev in high_levs:
                    for contravariant in contravariants:
                        for colmun in colmuns:
                            for signal in signals:
                                parameters.append((lag, middle, low_lev, high_lev, contravariant,colmun,signal))
    return parameters

def generate_volume_filter_rsi(lags, middles, low_levs, high_levs, contravariants, colmuns):
    parameters = []
    for lag in lags:
        for middle in middles:
            for low_lev in low_levs:
                for high_lev in high_levs:
                    for contravariant in contravariants:
                        for colmun in colmuns:
                            parameters.append((lag, middle, low_lev, high_lev, contravariant,colmun))
    return parameters

rolling_windows = [5,10,20,50,100,150,200,250,300,350,400,450,500]

instantaneous_slope_fin_diff_hs = [1,2,5,10,15]
thresholds = [0,0.01,0.05,0.1]
signal_vol_windows = [1,3,5,10,15,20]

def generate_fin_diffs(instantaneous_slope_fin_diff_hs, rolling_windows, thresholds, signal_vol_windows):
    parameters = []
    for fin_h in instantaneous_slope_fin_diff_hs:
        for rolling_window in rolling_windows:
            for threshold in thresholds:
                for signal_vol_window in signal_vol_windows:
                    parameters.append((fin_h,rolling_window,threshold,signal_vol_window))
    return parameters

def generate_fin_diffs_slope_double(instantaneous_slope_fin_diff_hs, slope_rolling_windows, second_rolling_windows, rolling_windows, slope_thresholds, second_slope_thresholds, thresholds, signal_vol_windows,moderates, use_zscores):
    parameters = []
    for fin_h in instantaneous_slope_fin_diff_hs:
        for rolling_window in rolling_windows:
            for threshold in thresholds:
                for slope_threshold in slope_thresholds:
                    for second_slope_threshold in second_slope_thresholds:
                        for signal_vol_window in signal_vol_windows:
                            for slope_rolling_window in slope_rolling_windows:
                                for second_rolling_window in second_rolling_windows:
                                    for moderate in moderates:
                                        for use_zscore in use_zscores:
                                            parameters.append((fin_h,slope_rolling_window, second_rolling_window,rolling_window,slope_threshold, second_slope_threshold, threshold,signal_vol_window, moderate, use_zscore))
    return parameters

def generate_rolling_fin_diffs_slope(zscore_windows, instantaneous_slope_fin_diff_hs, slope_rolling_windows, second_rolling_windows, rolling_windows, slope_thresholds,):
    parameters = []
    for zscore_window in zscore_windows:
        for fin_h in instantaneous_slope_fin_diff_hs:
            for rolling_window in rolling_windows:
                for slope_threshold in slope_thresholds:
                    for slope_rolling_window in slope_rolling_windows:
                        for second_rolling_window in second_rolling_windows:
                            parameters.append((zscore_window, fin_h,slope_rolling_window, second_rolling_window,rolling_window,slope_threshold))
    return parameters

def generate_fin_diffs_slope(instantaneous_slope_fin_diff_hs, slope_rolling_windows, second_rolling_windows, rolling_windows, slope_thresholds,):
    parameters = []
    for fin_h in instantaneous_slope_fin_diff_hs:
        for rolling_window in rolling_windows:
            for slope_threshold in slope_thresholds:
                for slope_rolling_window in slope_rolling_windows:
                    for second_rolling_window in second_rolling_windows:
                        parameters.append((fin_h,slope_rolling_window, second_rolling_window,rolling_window,slope_threshold))
    return parameters

def generate_fin_diffs_slope_zscore(instantaneous_slope_fin_diff_hs, zscore_windows, rolling_windows, slope_thresholds, thresholds, signal_vol_windows):
    parameters = []
    for fin_h in instantaneous_slope_fin_diff_hs:
        for zscore_window in zscore_windows:
            for rolling_window in rolling_windows:
                for threshold in thresholds:
                    for slope_threshold in slope_thresholds:
                        for signal_vol_window in signal_vol_windows:
                            parameters.append((fin_h,zscore_window,rolling_window,slope_threshold, threshold,signal_vol_window))
    return parameters

def generate_fin_diffs_advanced(instantaneous_slope_fin_diff_hs, rolling_windows, thresholds, signal_vol_windows, slope_windows, second_rolling_windows):
    parameters = []
    for fin_h in instantaneous_slope_fin_diff_hs:
        for rolling_window in rolling_windows:
            for threshold in thresholds:
                for signal_vol_window in signal_vol_windows:
                    for slope_window in slope_windows:
                        for second_rolling_window in second_rolling_windows:
                            parameters.append((fin_h,rolling_window,threshold,signal_vol_window, slope_window, second_rolling_window))
    return parameters


def generate_volume_filter_lead_lag(leads, lags, low_levs, high_levs, percentage_longs, coliumns):
    parameters = []
    for lead in leads:
        for lag in lags:
            for low_lev in low_levs:
                for high_lev in high_levs:
                    for percentage_long in percentage_longs:
                        for column in coliumns:
                            if lead < lag:
                                parameters.append((lead,lag,low_lev,high_lev, percentage_long, column))
    return parameters

def generate_lead_lag(lookback_windows, lead_lags, contravariants, ):
    parameters = []
    for contravariant in contravariants:
        for lookback_window in lookback_windows:
            for lead in lead_lags:
                if lead < lookback_window:
                    parameters.append({
                        'lead':lead,
                        'lookback_window':lookback_window,
                        'contravariant':contravariant
                    })
    return parameters

def generate_dd_threshold_lo_without_lag(lookback_windows, up_thresholds):
    parameters = []
    for lookback_window in lookback_windows:
        for up_threshold in up_thresholds:
                parameters.append({
                    'lookback_window':lookback_window,
                    'up_threshold':up_threshold,
                })
    return parameters

def generate_dd_threshold_ls_without_lag(lookback_windows, low_thresholds, up_thresholds):
    parameters = []
    for lookback_window in lookback_windows:
        for up_threshold in up_thresholds:
            for low_threshold in low_thresholds:
                parameters.append({
                    'lookback_window':lookback_window,
                    'up_threshold':up_threshold,
                    'low_threshold':low_threshold
                })
    return parameters


def generate_looklag_pente(lookback_windows, lags, pente_windows):
    parameters = []
    for lookback_window in lookback_windows:
        for lag in lags:
            for pente_window in pente_windows:
                if lag <= int(lookback_window / 2.):
                    if pente_window <= int(lookback_window/lag):
                        parameters.append({
                            'lookback_window': lookback_window,
                            'lag': lag,
                            'pente_window':pente_window
                        })
    return parameters

def generate_looklag(lookback_windows, lags):
    parameters = []
    for lookback_window in lookback_windows:
        for lag in lags:
            if lag <= int(lookback_window / 2.):
                parameters.append({
                    'lookback_window': lookback_window,
                    'lag': lag
                })

    return parameters

def generate_dd_threshold_lo(lookback_windows, up_thresholds, lags, contravariants):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for up_threshold in up_thresholds:
                for lag in lags:
                    if lag <= int(lookback_window/2.):
                        parameters.append({
                            'lookback_window':lookback_window,
                            'contravariant':contravariant,
                            'up_threshold':up_threshold,
                            'lag':lag
                        })
    return parameters

def generate_dd_threshold_ls(lookback_windows, low_thresholds, up_thresholds, lags, contravariants):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for low_threshold in low_thresholds:
                for up_threshold in up_thresholds:
                    for lag in lags:
                        if lag <= int(lookback_window/2.):
                            parameters.append({
                                'lookback_window':lookback_window,
                                'contravariant':contravariant,
                                'low_threshold':low_threshold,
                                'up_threshold':up_threshold,
                                'lag':lag
                            })
    return parameters

def generate_lookback_only(lookback_windows):
    parameters = []
    for lookback_window in lookback_windows:
                parameters.append({
                    'lookback_window':lookback_window
                })
    return parameters


def generate_lo_slope_ma(lookback_windows, pente_windows, contravariants,):
    parameters = []
    for lookback_window in lookback_windows:
        for pente_window in pente_windows:
            for contravariant in contravariants:
                if pente_window <= lookback_window:
                    parameters.append({
                        'lookback_window':lookback_window,
                        'pente_window':pente_window,
                        'contravariant':contravariant
                    })
    return parameters


# def generate_fourier_wvt_decomposition(lookback_windows,contravariants,n_harms,fft_filter_types,dec_levels,thresholds,obs_covs):
#     parameters = []
#     for lookback_window in lookback_windows:
#         for contravariant in contravariants:
#             for fft_filter_type in fft_filter_types:
#                 for n_harm in n_harms:
#                     for dec_level in dec_levels:
#                         for threshold in thresholds:
#                             for observation_covariance in obs_covs:
#                                 if n_harm < lookback_window:
#                                     parameters.append({
#                                         'lookback_window':lookback_window,
#                                         'contravariant':contravariant,
#                                         'fft_filter_type':fft_filter_type,
#                                         'n_harm':n_harm,
#                                         'dec_level':dec_level,
#                                         'threshold':threshold,
#                                         'observation_covariance':observation_covariance
#                                     })
#     return parameters

def generate_fourier_wvt_decomposition(lookback_windows,contravariants,n_harms,fft_filter_types,wavelet_filters,dec_levels,optimize_filtering_states, thresholds, soft_filtering_states):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for fft_filter_type in fft_filter_types:
                for n_harm in n_harms:
                    for dec_level in dec_levels:
                        for filter_name in wavelet_filters:
                            for threshold in thresholds:
                                for optimize_filtering in optimize_filtering_states:
                                    for soft_filtering in soft_filtering_states:
                                        if n_harm < lookback_window:
                                            if optimize_filtering:
                                                parameters.append({
                                                    'lookback_window':lookback_window,
                                                    'contravariant':contravariant,
                                                    'fft_filter_type':fft_filter_type,
                                                    'n_harm':n_harm,
                                                    'filter_name':filter_name,
                                                    'dec_level':dec_level,
                                                    'threshold':threshold,
                                                    'optimize_filtering':optimize_filtering,
                                                    'soft_filtering':soft_filtering
                                                })
                                            else:
                                                parameters.append({
                                                    'lookback_window': lookback_window,
                                                    'contravariant': contravariant,
                                                    'fft_filter_type': fft_filter_type,
                                                    'n_harm': n_harm,
                                                    'filter_name': filter_name,
                                                    'dec_level': dec_level,
                                                    'optimize_filtering': optimize_filtering,
                                                    'soft_filtering': soft_filtering
                                                })

    return parameters

def generate_fourier_wvt_ortho_decomposition(lookback_windows,n_harms,fft_filter_types,wavelet_filters,dec_levels,coef_factors, independent_selection_states):
    parameters = []
    for lookback_window in lookback_windows:
        for fft_filter_type in fft_filter_types:
            for n_harm in n_harms:
                for dec_level in dec_levels:
                    for filter_name in wavelet_filters:
                        for coeff_index_factor in coef_factors:
                            for independent_selection in independent_selection_states:
                                if n_harm < lookback_window:
                                    parameters.append({
                                        'lookback_window':lookback_window,
                                        'fft_filter_type':fft_filter_type,
                                        'n_harm':n_harm,
                                        'filter_name':filter_name,
                                        'dec_level':dec_level,
                                        'coeff_index_factor':coeff_index_factor,
                                        'independent_selection':independent_selection
                                    })
    return parameters

# def generate_kalman(lookback_windows,contravariants,n_harms,fft_filter_types,thresholds,obs_covs):
#     parameters = []
#     for lookback_window in lookback_windows:
#         for contravariant in contravariants:
#             for fft_filter_type in fft_filter_types:
#                 for n_harm in n_harms:
#                     for threshold in thresholds:
#                         for observation_covariance in obs_covs:
#                             if n_harm < lookback_window:
#                                 parameters.append({
#                                     'lookback_window':lookback_window,
#                                     'contravariant':contravariant,
#                                     'fft_filter_type':fft_filter_type,
#                                     'n_harm':n_harm,
#                                     'threshold':threshold,
#                                     'observation_covariance':observation_covariance
#                                 })
#     return parameters


def generate_kalman(lookback_windows,contravariants,n_harms,fft_filter_types,obs_covs):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for fft_filter_type in fft_filter_types:
                for n_harm in n_harms:
                    for observation_covariance in obs_covs:
                        if n_harm < lookback_window:
                            parameters.append({
                                'lookback_window':lookback_window,
                                'contravariant':contravariant,
                                'fft_filter_type':fft_filter_type,
                                'n_harm':n_harm,
                                'observation_covariance':observation_covariance
                            })
    return parameters



def generate_fourier_hht(lookback_windows,contravariants,n_harms,fft_filter_types, threshold_1_values, threshold_2_values, alpha_values, n_imfs_values):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for fft_filter_type in fft_filter_types:
                for n_harm in n_harms:
                    for threshold_1 in threshold_1_values:
                        for threshold_2 in threshold_2_values:
                            for alpha in alpha_values:
                                for n_imfs in n_imfs_values:
                                    if n_harm < lookback_window:
                                        parameters.append({
                                            'lookback_window': lookback_window,
                                            'contravariant': contravariant,
                                            'fft_filter_type': fft_filter_type,
                                            'n_harm': n_harm,
                                            'threshold_1':threshold_1,
                                            'threshold_2':threshold_2,
                                            'alpha':alpha,
                                            'n_imfs':n_imfs
                                        })
    return parameters


def generate_fourier_decomposition(lookback_windows,contravariants,n_harms,fft_filter_types,):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for fft_filter_type in fft_filter_types:
                for n_harm in n_harms:
                    if n_harm<lookback_window:
                        parameters.append({
                            'lookback_window':lookback_window,
                            'fft_filter_type': fft_filter_type,
                            'contravariant':contravariant,
                            'n_harm':n_harm
                        })
    return parameters

def generate_rooftingFilter(lookback_windows, periods, n_harms, fft_filter_types, contravariants):
    parameters = []
    for lookback_window in lookback_windows:
        for period in periods:
            for n_harm in n_harms:
                for fft_filter_type in fft_filter_types:
                    for contravariant in contravariants:
                        if period < lookback_window:
                            parameters.append({
                                'lookback_window': lookback_window,
                                'period':period,
                                'n_harm':n_harm,
                                'fft_filter_type':fft_filter_type,
                                'contravariant':contravariant
                            })
    return parameters


def generate_lookback_contravariant(lookback_windows, contravariants):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            parameters.append({
                'lookback_window':lookback_window,
                'contravariant':contravariant
            })
    return parameters

def generate_alpha_5(lookback_windows, lags, contravariants):
    parameters = []
    for lookback_window in lookback_windows:
        for lag in lags:
            for contravariant in contravariants:
                if lag < int(lookback_window/2):
                    parameters.append({
                        'lookback_window':lookback_window,
                        'lag':lag,
                        'contravariant':contravariant
                    })
    return parameters

def generate_alpha_8(lookback_windows, contravariants, lags):
    parameters = []
    for lookback_window in lookback_windows:
        for lag in lags:
            for contravariant in contravariants:
                if lag <= lookback_window/4:
                    parameters.append({
                        'lookback_window':lookback_window,
                        'lag' : lag,
                        'contravariant':contravariant
                    })
    return parameters


def generate_alpha_16(lookback_windows, contravariants, lags):
    parameters = []
    for lookback_window in lookback_windows:
        for lag in lags:
            for contravariant in contravariants:
                if lag <= lookback_window/4 and lag >= 2:
                    parameters.append({
                        'lookback_window':lookback_window,
                        'lag' : lag,
                        'contravariant':contravariant
                    })
    return parameters

def generate_alpha_16_lo(lookback_windows, contravariants, lags, up_thresholds):
    parameters = []
    for lookback_window in lookback_windows:
        for up_threshold in up_thresholds:
            for lag in lags:
                for contravariant in contravariants:
                    if lag <= lookback_window/4 and lag >= 2:
                        parameters.append({
                            'lookback_window':lookback_window,
                            'lag' : lag,
                            'up_threshold': up_threshold,
                            'contravariant':contravariant
                        })
    return parameters

def generate_alpha_16_ls(lookback_windows, contravariants, lags, up_thresholds, low_thresholds):
    parameters = []
    for lookback_window in lookback_windows:
        for up_threshold in up_thresholds:
            for low_threshold in low_thresholds:
                for lag in lags:
                    for contravariant in contravariants:
                        if lag <= lookback_window/4 and lag >= 2:
                            parameters.append({
                                'lookback_window':lookback_window,
                                'lag' : lag,
                                'low_threshold': low_threshold,
                                'up_threshold': up_threshold,
                                'contravariant':contravariant
                            })
    return parameters

def generate_alpha_6_ls(lookback_windows, vol_thresholds, contravariants, lags, display):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for vol_threshold in vol_thresholds:
                for lag in lags:
                    if lag <= int(lookback_window/2):
                        parameters.append({
                            'lookback_window':lookback_window,
                            'contravariant':contravariant,
                            'vol_threshold':vol_threshold,
                            'lag':lag,
                            'display' : display
                        })
    return parameters

def generate_volume_weighted_high_low_vol_lo(lookback_windows, vol_thresholds, up_trend_thresholds, contravariants, lags, display):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for vol_threshold in vol_thresholds:
                for up_trend_threshold in up_trend_thresholds:
                    for lag in lags:
                        if lag <= int(lookback_window/2):
                            parameters.append({
                                'lookback_window':lookback_window,
                                'contravariant':contravariant,
                                'vol_threshold':vol_threshold,
                                'up_trend_threshold':up_trend_threshold,
                                'lag':lag,
                                'display' : display
                            })
    return parameters

def generate_volume_weighted_high_low_vol_ls(lookback_windows, vol_thresholds, up_trend_thresholds,  low_trend_thresholds, contravariants, lags, display):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for vol_threshold in vol_thresholds:
                for up_trend_threshold in up_trend_thresholds:
                    for low_trend_threshold in low_trend_thresholds:
                        for lag in lags:
                            if lag <= int(lookback_window/2):
                                parameters.append({
                                    'lookback_window':lookback_window,
                                    'contravariant':contravariant,
                                    'vol_threshold':vol_threshold,
                                    'up_trend_threshold':up_trend_threshold,
                                    'low_trend_threshold': low_trend_threshold,
                                    'lag':lag,
                                    'display' : display
                                })
    return parameters

def generate_lo_slope_ma(lookback_windows, pente_windows, contravariants,):
    parameters = []
    for lookback_window in lookback_windows:
        for pente_window in pente_windows:
            for contravariant in contravariants:
                if pente_window <= lookback_window:
                    parameters.append({
                        'lookback_window':lookback_window,
                        'pente_window':pente_window,
                        'contravariant':contravariant
                    })
    return parameters

def generate_slope_lo_induced(lookback_windows, pente_windows, contravariants, lags, slope_columns, up_trend_thresholds, display):
    parameters = []
    for slope_column in slope_columns:
        for lookback_window in lookback_windows:
            for pente_window in pente_windows:
                for contravariant in contravariants:
                    for lag in lags:
                        for up_trend_threshold in up_trend_thresholds:
                            if pente_window < int(lookback_window/lag):
                                if lag < int(lookback_window/2):
                                    parameters.append({
                                        'lookback_window':lookback_window,
                                        'pente_window':pente_window,
                                        'contravariant':contravariant,
                                        'up_trend_threshold': up_trend_threshold,
                                        'lag':lag,
                                        'slope_column': slope_column,
                                        'display' : display
                                    })
    return parameters

def generate_slope_lo_to_ls(lookback_windows, pente_windows, pente_windows_bis, contravariants, lags, slope_columns, up_trend_thresholds, up_trend_thresholds_bis, display):
    parameters = []
    for slope_column in slope_columns:
        for lookback_window in lookback_windows:
            for pente_window in pente_windows:
                for pente_window_bis in pente_windows_bis:
                    for contravariant in contravariants:
                        for lag in lags:
                            for up_trend_threshold_bis in up_trend_thresholds_bis:
                                for up_trend_threshold in up_trend_thresholds:
                                    if pente_window < int(lookback_window/lag):
                                        if lag < int(lookback_window/2):
                                            parameters.append({
                                                'lookback_window':lookback_window,
                                                'pente_window':pente_window,
                                                'pente_window_bis':pente_window_bis,
                                                'contravariant':contravariant,
                                                'up_trend_threshold_bis': up_trend_threshold_bis,
                                                'up_trend_threshold': up_trend_threshold,
                                                'lag':lag,
                                                'slope_column': slope_column,
                                                'display' : display
                                            })
    return parameters

def generate_slope_ls_induced(lookback_windows, pente_windows, contravariants, lags, slope_columns, low_trend_thresholds, up_trend_thresholds, display):
    parameters = []
    for slope_column in slope_columns:
        for lookback_window in lookback_windows:
            for pente_window in pente_windows:
                for contravariant in contravariants:
                    for lag in lags:
                        for low_trend_threshold in low_trend_thresholds:
                            for up_trend_threshold in up_trend_thresholds:
                                if pente_window < int(lookback_window/lag):
                                    if lag < int(lookback_window/2):
                                        parameters.append({
                                            'lookback_window':lookback_window,
                                            'pente_window':pente_window,
                                            'contravariant':contravariant,
                                            'low_trend_threshold': low_trend_threshold,
                                            'up_trend_threshold': up_trend_threshold,
                                            'lag':lag,
                                            'slope_column': slope_column,
                                            'display' : display
                                        })
    return parameters

def generate_trending_rank_ls_induced(lookback_windows, contravariants, lags, slope_columns, up_trend_thresholds,  low_trend_thresholds, display):
    parameters = []
    for slope_column in slope_columns:
        for lookback_window in lookback_windows:
            for contravariant in contravariants:
                for lag in lags:
                    for up_trend_threshold in up_trend_thresholds:
                        for low_trend_threshold in low_trend_thresholds:
                            if lag <= int(lookback_window/2):
                                parameters.append({
                                    'lookback_window':lookback_window,
                                    'contravariant':contravariant,
                                    'up_trend_threshold': up_trend_threshold,
                                    'low_trend_threshold': low_trend_threshold,
                                    'lag':lag,
                                    'slope_column': slope_column,
                                    'display' : display
                                })
    return parameters

def generate_trending_rank_lo_induced(lookback_windows, contravariants, lags, slope_columns, up_trend_thresholds, display):
    parameters = []
    for slope_column in slope_columns:
        for lookback_window in lookback_windows:
            for contravariant in contravariants:
                for lag in lags:
                    for up_trend_threshold in up_trend_thresholds:
                        if lag <= int(lookback_window/2):
                            parameters.append({
                                'lookback_window':lookback_window,
                                'contravariant':contravariant,
                                'up_trend_threshold': up_trend_threshold,
                                'lag':lag,
                                'slope_column': slope_column,
                                'display' : display
                            })
    return parameters

def generate_slope_induced_cont(lookback_windows, contravariants, lags, slope_columns, display):
    parameters = []
    for slope_column in slope_columns:
        for lookback_window in lookback_windows:
            for contravariant in contravariants:
                for lag in lags:

                    if lag <= int(lookback_window/2):
                        parameters.append({
                            'lookback_window':lookback_window,
                            'contravariant':contravariant,
                            'lag':lag,
                            'slope_column': slope_column,
                            'display' : display
                        })
    return parameters


def generate_volume_weighted_high_low_vol_cont(lookback_windows, contravariants, lags, display):
    parameters = []
    for lookback_window in lookback_windows:
        for contravariant in contravariants:
            for lag in lags:
                if lag <= int(lookback_window/2):
                    parameters.append({
                        'lookback_window':lookback_window,
                        'contravariant':contravariant,
                        'lag':lag,
                        'display' : display
                    })
    return parameters