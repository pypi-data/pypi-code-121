class ModelState():
    def __init__(self, eval_slice=None, test_slice=None, dates_eval_slice=None, dates_test_slice=None, df_eval=None,
                     df_test=None, X_eval=None, X_test=None, y_eval=None, y_test=None, pred_test=None, pred_eval=None):

        self.eval_slice = eval_slice
        self.test_slice = test_slice
        self.dates_eval_slice = dates_eval_slice
        self.dates_test_slice = dates_test_slice
        self.df_eval = df_eval
        self.df_test = df_test
        self.X_eval = X_eval
        self.X_test = X_test
        self.y_eval = y_eval
        self.y_test = y_test
        self.pred_test = pred_test
        self.pred_eval = pred_eval



