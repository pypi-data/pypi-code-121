# import argparse
# from pathlib import Path
#
# import joblib
# import pandas as pd
#
#
# from galib import ga4_report
# from galib import ga4_to_df
# from galib import ua_report
# from galib import ua_to_df
# from utils import make_path
# from utils import pairwise
#
#
# def parse_args():
#     ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#     ap.add_argument("--key", "-k", default="key.json", help="Path to json key file")
#     ap.add_argument(
#         "--dimensions",
#         "-d",
#         nargs="+",
#         required=True,
#         help="Dimensions to operate on (space-separated)",
#     )
#     ap.add_argument(
#         "--metrics",
#         "-m",
#         nargs="+",
#         required=True,
#         help="Metrics to extract (space-separated expressions)",
#     )
#
#     # https://developers.google.com/analytics/devguides/reporting/core/v3/reference#filters
#     ap.add_argument(
#         "--filters",
#         "-f",
#         nargs="+",
#         help="Filter parameter for querying GA (space separted).",
#     )
#     ap.add_argument(
#         "--force",
#         "-F",
#         action="store_true",
#         help="Ignore request cache file and perform new request anyway.",
#     )
#     ap.add_argument("--output", "-o", help="Save path")
#     ap.add_argument("--start", "-s", default="7daysAgo", help="Start date")
#     ap.add_argument("--end", "-e", default="today", help="End date")
#     ap.add_argument(
#         "--period", "-p", type=int, help="How often (days) to sample requests."
#     )
#     ap.add_argument(
#         "--ga4",
#         action="store_true",
#         help="Use GA4 data reporting API, otherwise default to UA.",
#     )
#
#     args = ap.parse_args()
#     return args
#
#
# def request_or_reload(start, end, args, report_fn):
#     # TODO cache requests
#     # TODO verbosity flag in argument parser
#     response = report_fn(
#         start, end, args.dimensions, args.metrics, args.filters, verbose=True
#     )
#     return response
#
#
# def save_outputs(start, end, args, response, to_df_fn):
#     fname = f"{start}_{end}"
#
#     # cache request
#     # TODO bug joblib/pickle/dill can't serialize RunReportResponse even if it's
#     # imported manually with
#     # `from google.analytics.data_v1beta.types.analytics_data_api import
#     # RunReportResponse`.
#     # as it is, ga4 responses aren't cacheable
#
#     # save output dataframe
#     if args.output:
#         make_path(args.output)
#         output = Path(args.output)
#
#         dst_request = (output / fname).with_suffix(".pkl")
#         dst_dataframe = (output / fname).with_suffix(".csv")
#
#         print(f"=> Caching requests to `{dst_request}`")
#         joblib.dump(response, dst_request)
#
#         print(f"=> Saving results to `{dst_dataframe}`")
#         to_df_fn(response).to_csv(dst_dataframe, index=False)
#
#
# def main(args=None):
#     args = args if args is not None else parse_args()
#     # which reporting and df parsing functions to use
#     report_fn = ga4_report if args.ga4 else ua_report
#     to_df = ga4_to_df if args.ga4 else ua_to_df
#
#     # [ PIPELINE ]
#     dates = [(args.start, args.end)]
#
#     single_day_range = args.start == args.end
#     if single_day_range and args.period:
#         raise ValueError(
#             "Do not specify --period/-p when using a single-day date range."
#         )
#
#     if args.period:
#         dates = pd.date_range(args.start, args.end, freq=f"{args.period}D")
#         dates = pairwise(dates)
#
#         # offset end date for all except last date range
#         dates = [(a, (b - pd.DateOffset(1))) for a, b in dates[:-1]] + [dates[-1]]
#
#         # parse dates to string
#         dates = [(a.strftime("%F"), b.strftime("%F")) for (a, b) in dates]
#
#     for start, end in dates:
#         fname = f"{start}_{end}"
#         save_dst = (Path(args.output) / fname).with_suffix(".csv")
#
#         if save_dst.exists() and not args.force:
#             print(f"=> {save_dst} already exists. Skipping...")
#             continue
#
#         response = request_or_reload(start, end, args, report_fn)
#
#         save_outputs(start, end, args, response, to_df)
#
#
# if __name__ == "__main__":
#     main(parse_args())
