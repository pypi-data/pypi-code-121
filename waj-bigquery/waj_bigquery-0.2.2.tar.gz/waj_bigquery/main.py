from core.bigquery.bigquery import bigquery as bq
from core.config import settings

models_to_run = [
    "twitter",
    "facebook",
    "google",
    "instagram",
    "tiktok",
    "youtube",
    "summary",
]

if __name__ == "__main__":
    for model in models_to_run:
        output = bq.create_or_update_model(model)
        print(output)
