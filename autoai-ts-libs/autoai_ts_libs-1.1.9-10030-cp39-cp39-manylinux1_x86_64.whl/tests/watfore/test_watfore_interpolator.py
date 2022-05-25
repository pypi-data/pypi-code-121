# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2021, 2022, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************

"""
@author: Syed Yousaf Shah (syshah@us.ibm.com)
Date: Feb-19-2020
"""
import logging
import unittest
#import math
import numpy as np

from autoai_ts_libs.watfore.watfore_interpolator import WatForeInterpolator

logger = logging.getLogger()
#logger.setLevel('INFO')
#TODO: Check the working of interpolation of algorithm
class TestWatForeInterpolator(unittest.TestCase):

    def setUp(self):
        print('.......................Testing WatFore Interpolators.......................')
        self.imputer_types = ['linear',  'prev', 'next','nearest', 'fill'] #, 'cubic'
        self.watfore_interpolators = []
        self.missing_value = -100#np.nan
        for impu in self.imputer_types:
            self.watfore_interpolators.append(WatForeInterpolator(interpolator_type=impu, append_tranform=False, ts_ocol_loc=[0]
                                           , ts_icol_loc=[0], default_value=self.missing_value,missing_val_identifier = self.missing_value, debug=False)
                                     )
        self.watfore_interpolators.append( WatForeInterpolator(interpolator_type='prev', append_tranform=False, ts_ocol_loc=[6]
                                , ts_icol_loc=-1, default_value=-1,missing_val_identifier = self.missing_value, debug=True))

        self.watfore_interpolators.append( WatForeInterpolator(interpolator_type='fill', append_tranform=False, ts_ocol_loc=-1
                                , ts_icol_loc=[0],missing_val_identifier = self.missing_value, debug=False))

        self.ts_val =[[0, 10], [1, 20], [2, 30], [3, 40], [4, 50], [5, self.missing_value], [6, 70], [7, 80], [8, 90], [9, 100]]
       #  import tspy
       #  import pandas as pd
       #  dataframe = pd.DataFrame( self.ts_val, columns=['timestamp', 'value'])
       #  dataframe = dataframe.astype(dtype={"timestamp": "int64", "value": "float64"})
       #  print('Dataframe ',dataframe)
       #  self._timeseries = tspy.time_series(list(dataframe['value']))#tspy.time_series(dataframe, ts_column="timestamp", value_column="value")
       #
       #  print('STARTUP============',self._timeseries.fillna(tspy.functions.interpolators.cubic(fill_value=0.0),np.nan))
        #print('TimeSeries ', self._timeseries)
    def test_transformer_get_params(self):
        param1, param2 = None, None
        param1 = WatForeInterpolator.get_param_ranges()
        param2 = WatForeInterpolator.get_param_dist()

        self.assertFalse(param1==None)
        self.assertFalse(param2 == None)

    def test_wrong_params(self):
        try:

            intp = WatForeInterpolator(interpolator_type='next', append_tranform=False, ts_ocol_loc=[0]
                                , ts_icol_loc=[-1],missing_val_identifier = self.missing_value, debug=True)
            intp.transform(self.ts_val)
        except:
            self.assertRaises(AssertionError)

    def test_interpolator_append_params(self):
        try:

            intp = WatForeInterpolator(interpolator_type='prev', append_tranform=True, ts_ocol_loc=[4]
                                , ts_icol_loc=-1, missing_val_identifier = self.missing_value, debug=True)
            intp.transform(self.ts_val)
        except Exception as e:
            self.fail(e)

    def test_watfore_interpolator(self):
        print(self.watfore_interpolators)

        try:
            print('WatFore Interpolator Tests')
            for w_imputer in self.watfore_interpolators:
                print('Input Values', self.ts_val, type(self.ts_val))
                print("Parameters=============",w_imputer.get_model_params())
                interpolated = w_imputer.transform(self.ts_val)
                print('Imputed Values',interpolated)
                #print('Imputed Values', tspy.functions.interpolators.cubic())
                self.assertFalse(np.any(np.isnan(interpolated)))

        except Exception as e:
            logger.warning(e)
            self.fail(e)


    def test_imputer_helper_impute_list(self):
        try:
            import autoai_ts_libs.utils.imputer_helper as imputer_helper

            # ts_vals1 = np.asarray([[0, 10], [1, 20], [2, 30], [5, np.nan], [4, 50], [5, np.nan]])
            # impute_vals1 = imputer_helper.impute_list(ts_vals1)
            #
            # self.assertFalse(np.isnan(impute_vals1.any()))
            #
            # print('Imputed Values ',impute_vals1)
            ts_vals1 = [np.nan,10, 20, 30, np.nan, 50]

            impute_vals1 = imputer_helper.impute_list(ts_vals1)
            self.assertFalse(np.isnan(impute_vals1.any()))
            print('Imputed list ', impute_vals1)

        except Exception as e:
            self.fail(e)

        # def test_impute_multi_array(self):
        #     try:
        #         import autoai_ts_libs.utils.imputer_helper as imputer_helper
        #
        #         ts_vals1 = np.asarray([[np.nan, np.nan], [1, 20], [np.nan, 30], [5, np.nan], [4, 50], [5, np.nan]])
        #         #ts_vals1 = np.asarray([[0, 10], [1, 20], [2, 30], [3, 40], [4, 50], [5, 60]])
        #         default_vals = [-10,300]
        #         impute_vals1 = imputer_helper.impute_multi_array(ts_vals1,default_values=default_vals,
        #                                                          impute_column_indices=[0,1])
        #         print('Imputed X ', impute_vals1)
        #         self.assertFalse(np.isnan(impute_vals1.any()))
        #
        #         ts_vals1 = np.asarray([[1,np.nan, np.nan], [1,1, 20], [1,np.nan, 30], [1,5, np.nan], [1,4, 50], [1,5, np.nan]])
        #         #ts_vals1 = np.asarray([[0, 10], [1, 20], [2, 30], [3, 40], [4, 50], [5, 60]])
        #         default_vals = [-10,300]
        #         impute_vals1 = imputer_helper.impute_multi_array(ts_vals1,default_values=default_vals,
        #                                                          impute_column_indices=[1,2])
        #         print('Imputed X ', impute_vals1)
        #         self.assertFalse(np.isnan(impute_vals1.any()))
        #
        #
        #
        #     except Exception as e:
        #         self.fail(e)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()