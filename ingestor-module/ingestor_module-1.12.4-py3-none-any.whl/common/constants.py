CONTENT_NODE = "content_node"
LABEL = "label"
PROPERTIES = "properties"
RELATIONSHIP = "relationship_name"
LEFT = "left"
YES = "yes"
NO = "no"
ADDITIONAL_STOPWORDS = ['and', 'local', 'tv', 'kontent', 'content', 'tag']

"""for user-content network generation"""
USER_CONTENT_RELATIONSHIP_LABEL = "VIEWED"

"""for CONTENT label"""
PAY_TV_CONTENT = "pay_tv_content"
NO_PAY_TV_CONTENT = "no_pay_tv_content"
CONTENT = "content"
CONTENT_ID = "content_id"
TITLE = "title"
YEAR = "year"
STATUS = "status"
DURATION_MINUTE = "duration_minute"
IS_GEO_BLOCK = "is_geo_block"
IS_FREE = "is_free"
IS_ORIGINAL = "is_original"
IS_BRANDED = "is_branded"
IS_EXCLUSIVE = "is_exclusive"
SYNOPSIS = "synopsis"
SYNOPSIS_EN = "synopsis_en"
START_DATE = "start_date"
END_DATE = "end_date"
MODIFIED_ON = "modified_on"
TYPE = "type"

COMBINED_FEATURES = 'combined_features'
CC_SIMILARITY_SCORE = 'cc_similarity_score'
ALL_SIMILARITY_SCORE = 'all_similarity_score'

"""for RATING label"""
RATING = "rating"

"""for CATEGORY label"""
CATEGORY = "category"
CATEGORY_ID = "category_id"
CATEGORY_EN = "category_en"

"""for SUBCATEGORY label"""
SUBCATEGORY = "subcategory"
SUBCATEGORY_ID = "subcategory_id"
SUBCATEGORY_EN = "subcategory_en"

"""for COUNTRY label"""
COUNTRY = "country"
COUNTRY_ID = "country_id"
COUNTRY_NAME = "country_name"
COUNTRY_DESCRIPTION = "country_description"

"""for TAG label"""
TAGS = "tags"
TAGS_ID = "tags_id"
TAGS_NAME = "tags_name"
DEFAULT_TAGS_DESCRIPTION = "Tidak Ada Deskripsi Tag"

"""for ACTOR label"""
ACTOR = "actor"
ACTORS = "actors"
ACTOR_NAME = "actor_name"
ACTOR_ID = "actor_id"

"""for Director label"""
DIRECTORS = "directors"
DIRECTOR_NAME = "director_name"
DIRECTOR_ID = "director_id"

"""for SEASON label"""
SEASON = "season"
SEASON_ID = "season_id"
SEASON_NAME = "season_name"

"""for CONTENT_CORE label"""
CONTENT_CORE = "content_core"
CONTENT_CORE_ID = "content_core_id"
CONTENT_CORE_SYNOPSIS = "content_core_synopsis"

"""for PACKAGE label"""
PACKAGE = "package"
PACKAGES = "packages"
PACKAGE_ID = "package_id"
PACKAGE_NAME = "package_name"
PACKAGE_NAME_EN = "package_name_en"

"""for PRODUCT label"""
PRODUCT = "product"
PRODUCTS = "products"
PRODUCT_ID = "product_id"
PRODUCT_NAME = "product_name"
PRODUCT_NAME_EN = "product_name_en"

"""for Paytv provider label"""
PAYTV_PROVIDER = "paytv_provider"
PAYTVPROVIDER_ID = "paytvprovider_id"
PAYTVPROVIDER_NAME = "paytvprovider_name"

"""for HOMEPAGE label"""
HOMEPAGE = "homepage"
HOMEPAGE_ID = "homepage_id"
HOMEPAGE_TITLE = "homepage_title"
HOMEPAGE_TITLE_EN = "homepage_title_en"
HOMEPAGE_STATUS = "homepage_status"
HOMEPAGE_TYPE = "homepage_type"
IS_CONNECTED = "is_connected"

"""for homepage having content"""
HOMEPAGE_HAVING_CONTENT_ID = "id"

"""for preprocessing_utils"""
WHITESPACE_REGEX = "\s+"
SINGLE_SPACE = " "

"""for merge df : content profile"""
CONTENT_BUNDLE_ID = "content_bundle_id"

""" for user labels """
USER_DETAIL_HAVING_PACKAGE = "user_detail_having_package"
USER_DETAIL_HAVING_PRODUCT = "user_detail_having_product"
USER_PAY_TV = "user_pay_tv"
CREATED_ON = "created_on"
CUSTOMER_ID = "customer_id"
CUSTOMER_CREATED_ON = "customer_created_on"
CUSTOMER_MODIFIED_ON = "customer_modified_on"
USER_LABEL = "user"
USER_DEMOGRAPHY = "user_demography"
DURATION = "duration"
BIRTHDAY = "birthday"
GENDER = "gender"
UD_KEY = "UserDetail_UDKey"
REGION_NAME = "region_name"
DEVOPS = "devops"
VIDEO_ID1 = "video_id1"
ATTRIBUTE1 = "attribute1"
CATEGORY1 = "category1"
CATEGORY2 = "category2"
CHANNEL_LIVE = "channel_live"
CATCHUP = "catchup"
VOD = "vod"
DEFAULT_DATE = "1970-10-10"
AGE = "age"
MEDIAN_AGE = 52
AGE_UPPER_BOUND = 100
DEFAULT_NUM = "-1"
DEFAULT_NAN = "nan"
UNKNOWN_LABEL = "unknown"
GENDER_VALUES = {"male": "m", "female": "f", "gender": "na"}
ABSURD_VALUE = "\\N"
DUMMY_ATTRIBUTE_SPLIT_ON = "_"
DEFAULT_FEATURE_VALUES = {
    COUNTRY_ID: DEFAULT_NAN,
    REGION_NAME: UNKNOWN_LABEL,
    DEVOPS: UNKNOWN_LABEL,
    ATTRIBUTE1: DEFAULT_NAN,
    RATING: DEFAULT_NAN,
}
LOCAL_CONNECTION_URI = "ws://localhost:8182/gremlin"
CSV_EXTENSION = ".csv"
FINAL_MERGED_DF = "final_merged_df"
SOLO_FEATURE_LIST = [RATING, ATTRIBUTE1]
FEATURE_DICT = {
    CATEGORY: CATEGORY_ID,
    SUBCATEGORY: SUBCATEGORY_ID,
    ACTORS: ACTOR_ID,
    DIRECTORS: DIRECTOR_ID,
    TAGS: TAGS_ID,
}
IS_PAYTV = "is_paytv"

CONTENT_BUNDLE = "content_bundle"

"""cache"""
CONTENT_HAVING_COUNTRY = "content_having_country"
CONTENT_HAVING_ACTOR = "content_having_actor"
CONTENT_HAVING_DIRECTOR = "content_having_director"
CONTENT_HAVING_TAGS = "content_having_tags"
HOMEPAGE_HAVING_CONTENT = "homepage_having_content"
PRODUCT_HAVING_PACKAGE = "product_having_package"
CONTENT_BUNDLE_HAVING_CONTENT = "content_bundle_having_content"
PACKAGE_HAVING_CONTENT_BUNDLE = "package_having_content_bundle"
CUSTOMER = "customer"

"""for RATING label"""
RATING = "rating"

"""for CATEGORY label"""
CATEGORY = "category"
CATEGORY_ID = "category_id"

"""for SUBCATEGORY label"""
SUBCATEGORY = "subcategory"
SUBCATEGORY_ID = "subcategory_id"

"""for COUNTRY label"""
COUNTRY_ID = "country_id"

"""for TAG label"""
TAGS = "tags"
TAGS_ID = "tags_id"
TAGS_DESCRIPTION = "tags_description"

"""for ACTOR label"""
ACTORS = "actors"
ACTOR_ID = "actor_id"

"""for Director label"""
DIRECTORS = "directors"
DIRECTOR_ID = "director_id"

""" for user labels """
REGION_NAME = "region_name"
DEVOPS = "devops"
ATTRIBUTE1 = "attribute1"
DEFAULT_NAN = "nan"
UNKNOWN_LABEL = "unknown"
CONTENT_CORE_TITLE = "content_core_title"
CONTENT_CORE_EPISODE = "content_core_episode"
CONTENT_CORE_SYNOPSIS_EN = "content_core_synopsis_en"
VIEW_COUNT = 'view_count'
VIEW_HISTORY = 'view_history'
CREATE = 'create'
UPDATE = 'update'

'''for preference generation'''
DURATION_WEIGHT = 0.8
CLICK_COUNT_WEIGHT = 0.2
