# TODO
import statsmodels.formula.api as smf
from IPython.core.display import display


# Un example of y_and_X variable "conversions ~ date + fb_pr_spend + fb_re_spend + g_discovery_spend +
# g_display_spend + g_performance_max_spend + g_search_spend + g_video_spend"
def mlm(df, y_and_X, groups_column_name, re_formula=''):
    model = smf.mixedlm(y_and_X, df, groups=df[groups_column_name], re_formula=re_formula)

    result = model.fit()

    display(result.summary())

    return result, model
