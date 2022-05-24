from newsapi import NewsApiClient


# function to get News for NewsApi
def get_articles_from_newsapi_with_qintitle(qintitle=None
                                            , article_language=None
                                            , from_param='2020-01-01'  # yyyy-mm-dd
                                            , to_param='2020-31-12'
                                            , newsapi_key=''
                                            ):
    all_articles_all_pages_df = pd.DataFrame()
    suchseite = 1
    anzahl_artikel_gefunden_von_api = 1

    newsapi = NewsApiClient(api_key=newsapi_key)

    while anzahl_artikel_gefunden_von_api > 0:
        all_articles_current_page_respone = newsapi.get_everything(
            from_param=from_param
            , to=to_param
            , language=article_language
            , page_size=100
            , page=suchseite
            , qintitle=qintitle
        )

        all_articles_current_page = all_articles_current_page_respone['articles']
        anzahl_artikel_gefunden_von_api = len(all_articles_current_page)
        all_articles_current_page_df = pd.DataFrame.from_dict(all_articles_current_page)
        all_articles_all_pages_df = all_articles_all_pages_df.append(all_articles_current_page_df)

        suchseite += 1
        if suchseite == 100:
            break
    return all_articles_all_pages_df


def get_articles_from_newsapi_with_source(
        from_param='2020-01-01'
        , to_param='2020-31-12'
        , newsapi_key=''
        , article_source_ids=''
):
    """Downloads articles from newsapi using sources

    :param from_param: Format: yyyy-mm-dd
    :type from_param: str

    :param from_param: Format: yyyy-mm-dd
    :type from_param: str

    :param newsapi_key:
    :type from_param: str

    :param article_source_ids:
    :type from_param: str
    """

    all_articles_all_pages_df = pd.DataFrame()
    suchseite = 1
    anzahl_artikel_gefunden_von_api = 1

    newsapi = NewsApiClient(api_key=newsapi_key)

    while anzahl_artikel_gefunden_von_api > 0:
        all_articles_current_page_respone = newsapi.get_everything(
            from_param=from_param
            , to=to_param
            , page_size=100
            , page=suchseite
            , sources=article_source_ids
        )

        all_articles_current_page = all_articles_current_page_respone['articles']
        anzahl_artikel_gefunden_von_api = len(all_articles_current_page)
        all_articles_current_page_df = pd.DataFrame.from_dict(all_articles_current_page)
        all_articles_all_pages_df = all_articles_all_pages_df.append(all_articles_current_page_df)

        suchseite += 1
        if suchseite == 100:
            break
    return all_articles_all_pages_df
