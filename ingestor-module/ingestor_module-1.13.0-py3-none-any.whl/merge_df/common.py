import ast

import pandas as pd

from ingestor.common.constants import CONTENT_ID, YEAR, DURATION_MINUTE, CATEGORY_ID, \
    HOMEPAGE_ID, CONTENT_CORE_ID, SEASON_ID, SUBCATEGORY_ID, CONTENT_BUNDLE_ID, \
    CATEGORY, SUBCATEGORY, COUNTRY, ACTORS, TAGS, HOMEPAGE, CONTENT_CORE, PACKAGES, \
    PRODUCTS, PACKAGE_ID, PRODUCT_ID, TAGS_ID, TITLE, SYNOPSIS, SYNOPSIS_EN, TYPE, \
    STATUS, IS_FREE, IS_ORIGINAL, IS_EXCLUSIVE, IS_BRANDED, IS_GEO_BLOCK, START_DATE, \
    MODIFIED_ON, END_DATE, CUSTOMER_ID, DURATION, BIRTHDAY, GENDER, CUSTOMER_CREATED_ON, \
    CUSTOMER_MODIFIED_ON, PAYTVPROVIDER_ID, UD_KEY, COUNTRY_ID, REGION_NAME, DEVOPS, \
    VIDEO_ID1, ATTRIBUTE1, CATEGORY1, CATEGORY2, ACTOR_ID, DIRECTORS, DIRECTOR_ID, \
    LEFT, CREATED_ON, RATING, AGE, IS_CONNECTED


class CommonUtils:

    @staticmethod
    def fetch_prepare_content_id(content_df, df_content, result_not_in_df):
        try:
            content_df[CONTENT_ID] = [int(df_content[CONTENT_ID].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_created_on(content_df, df_content, result_not_in_df):
        try:
            content_df[CREATED_ON] = [(df_content[CREATED_ON].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_title(content_df, df_content, result_not_in_df):
        try:
            content_df[TITLE] = [str(df_content[TITLE].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_synopsis(content_df, df_content, result_not_in_df):
        try:
            content_df[SYNOPSIS] = [str(df_content[SYNOPSIS].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_synopsis_en(content_df, df_content, result_not_in_df):
        try:
            content_df[SYNOPSIS_EN] = [str(df_content[SYNOPSIS_EN].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_year(content_df, df_content, result_not_in_df):
        try:
            if not pd.isna(df_content[YEAR].loc[0]):
                content_df[YEAR] = [int(df_content[YEAR].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_type(content_df, df_content, result_not_in_df):
        try:
            content_df[TYPE] = [str(df_content[TYPE].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_status(content_df, df_content, result_not_in_df):
        try:
            content_df[STATUS] = [str(df_content[STATUS].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_rating(content_df, df_content, result_not_in_df):
        try:
            content_df[RATING] = [str(df_content[RATING].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_is_free(content_df, df_content, result_not_in_df):
        try:
            content_df[IS_FREE] = [str(df_content[IS_FREE].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_is_original(content_df, df_content, result_not_in_df):
        try:
            content_df[IS_ORIGINAL] = [str(df_content[IS_ORIGINAL].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_is_exclusive(content_df, df_content, result_not_in_df):
        try:
            content_df[IS_EXCLUSIVE] = [str(df_content[IS_EXCLUSIVE].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_is_branded(content_df, df_content, result_not_in_df):
        try:
            content_df[IS_BRANDED] = [str(df_content[IS_BRANDED].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_is_geo_block(content_df, df_content, result_not_in_df):
        try:
            content_df[IS_GEO_BLOCK] = [str(df_content[IS_GEO_BLOCK].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_duration(content_df, df_content, result_not_in_df):
        try:
            if not pd.isna(df_content[DURATION_MINUTE].loc[0]):
                content_df[DURATION_MINUTE] = int(df_content[DURATION_MINUTE].loc[0])
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_start_date(content_df, df_content, result_not_in_df):
        try:
            content_df[START_DATE] = [pd.to_datetime(df_content[START_DATE].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_end_date(content_df, df_content, result_not_in_df):
        try:
            content_df[END_DATE] = [pd.to_datetime(df_content[END_DATE].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_modified_on(content_df, df_content, result_not_in_df):
        try:
            content_df[MODIFIED_ON] = [pd.to_datetime(df_content[MODIFIED_ON].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_category_id(content_df, df_content, result_not_in_df):
        try:
            if not pd.isna(df_content[CATEGORY_ID].loc[0]):
                content_df[CATEGORY_ID] = [int(df_content[CATEGORY_ID].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_subcategory_id(content_df, df_content, result_not_in_df):
        try:
            if not pd.isna(df_content[SUBCATEGORY_ID].loc[0]):
                content_df[SUBCATEGORY_ID] = [int(df_content[SUBCATEGORY_ID].loc[0])]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_country(content_df, df_content, df_country, result_not_in_df):
        try:
            df_country = df_country[[CONTENT_ID, COUNTRY_ID]]
            merged_with_country = pd.merge(content_df, df_country, left_on=CONTENT_ID,
                                           right_on=CONTENT_ID, how=LEFT)
            if len(merged_with_country) > 0:
                content_df = pd.merge(content_df, df_country, left_on=CONTENT_ID,
                                      right_on=CONTENT_ID, how=LEFT)
                country = []
                for cc in content_df[COUNTRY_ID].values:
                    if not pd.isna(cc):
                        c = {COUNTRY_ID: int(cc)}
                        if c not in country:
                            country.append(c)

                if len(country) > 0:
                    content_df = content_df.assign(country = [country])
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df
    
    @staticmethod
    def fetch_prepare_country_1(content_df, df_content, df_country, result_not_in_df):
        try:
            df_country = df_country[[CONTENT_ID, COUNTRY_ID]]
            merged_with_country = pd.merge(content_df, df_country, left_on=CONTENT_ID,
                                           right_on=CONTENT_ID, how=LEFT)
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df, merged_with_country

    @staticmethod
    def fetch_prepare_product_package(content_df, df_content, df_content_bundle_having_content,
                                      df_package_having_content_bundle, df_product_having_package, result_not_in_df):
        try:
            content_bundle_having_content_df = pd.merge(content_df, df_content_bundle_having_content,
                                                        left_on=CONTENT_ID,
                                                        right_on=CONTENT_ID,
                                                        how=LEFT)
            package_df = pd.merge(content_bundle_having_content_df, df_package_having_content_bundle,
                                  left_on=CONTENT_BUNDLE_ID, right_on=CONTENT_BUNDLE_ID,
                                  how=LEFT)
            packages = []
            for content_package_id in package_df[PACKAGE_ID].values:
                if not pd.isna(content_package_id):
                    content_package = {PACKAGE_ID: int(content_package_id)}
                    if content_package not in packages:
                        packages.append(content_package)

            if len(packages) > 0:
                content_df[PACKAGES] = [packages]

            product_df = pd.merge(package_df, df_product_having_package,
                                  left_on=PACKAGE_ID, right_on=PACKAGE_ID,
                                  how=LEFT)

            products = []
            for content_product_id in product_df[PRODUCT_ID].values:
                if not pd.isna(content_product_id):
                    content_product = {PRODUCT_ID: int(content_product_id)}
                    if content_product not in products:
                        products.append(content_product)

            if len(products) > 0:
                content_df[PRODUCTS] = [products]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_product_package_1(content_df, df_content, df_content_bundle_having_content,
                                      df_package_having_content_bundle, df_product_having_package, result_not_in_df):
        try:
            content_bundle_having_content_df = pd.merge(content_df, df_content_bundle_having_content,
                                                        left_on=CONTENT_ID,
                                                        right_on=CONTENT_ID,
                                                        how=LEFT)
            package_df = pd.merge(content_bundle_having_content_df, df_package_having_content_bundle,
                                  left_on=CONTENT_BUNDLE_ID, right_on=CONTENT_BUNDLE_ID,
                                  how=LEFT)
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df, package_df

    @staticmethod
    def fetch_prepare_content_cores(content_df, df_content, df_content_core, result_not_in_df):
        try:
            content_core_content_df = pd.merge(content_df, df_content_core, left_on=CONTENT_ID, right_on=CONTENT_ID,
                                               how=LEFT)

            content_cores = []
            for index, row in content_core_content_df.iterrows():
                if not pd.isna(row[CONTENT_CORE_ID]):
                    if not pd.isna(row[SEASON_ID]):
                        content_core = {CONTENT_CORE_ID: int(row[CONTENT_CORE_ID]),
                                        SEASON_ID: int(row[SEASON_ID])}
                        if content_core not in content_cores:
                            content_cores.append(content_core)
                    else:
                        content_core = {CONTENT_CORE_ID: int(row[CONTENT_CORE_ID])}
                        if content_core not in content_cores:
                            content_cores.append(content_core)

            if len(content_cores) > 0:
                content_df[CONTENT_CORE] = [content_cores]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df
    
    @staticmethod
    def fetch_prepare_content_cores_1(content_df, df_content, df_content_core, result_not_in_df):
        try:
            content_core_content_df = pd.merge(content_df, df_content_core, left_on=CONTENT_ID, right_on=CONTENT_ID,
                                               how=LEFT)
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df, content_core_content_df

    @staticmethod
    def fetch_prepare_homepages(content_df, df_content, df_homepage, result_not_in_df):
        try:
            homepage_content_df = pd.merge(content_df, df_homepage, left_on=CONTENT_ID, right_on=CONTENT_ID, how=LEFT)

            homepages = []
            for homepage_id in homepage_content_df[HOMEPAGE_ID].values:
                if not pd.isna(homepage_id):
                    homepage = {HOMEPAGE_ID: int(homepage_id)}
                    if homepage not in homepages:
                        homepages.append(homepage)

            if len(homepages) > 0:
                content_df[HOMEPAGE] = [homepages]

        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df
    
    @staticmethod
    def fetch_prepare_homepages_1(content_df, df_content, df_homepage, result_not_in_df):
        try:
            homepage_content_df = pd.merge(content_df, df_homepage, left_on=CONTENT_ID, right_on=CONTENT_ID, how=LEFT)
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df, homepage_content_df

    @staticmethod
    def fetch_prepare_tags(content_df, df_content, df_tag, result_not_in_df):
        try:
            tags_content_df = pd.merge(content_df, df_tag, left_on=CONTENT_ID, right_on=CONTENT_ID, how=LEFT)

            tags = []
            for tag_id in tags_content_df[TAGS_ID].values:
                if not pd.isna(tag_id):
                    tag = {TAGS_ID: int(tag_id)}
                    if tag not in tags:
                        tags.append(tag)

            if len(tags) > 0:
                content_df[TAGS] = [tags]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df
    
    @staticmethod
    def fetch_prepare_tags_1(content_df, df_content, df_tag, result_not_in_df):
        try:
            tags_content_df = pd.merge(content_df, df_tag, left_on=CONTENT_ID, right_on=CONTENT_ID, how=LEFT)
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df, tags_content_df

    @staticmethod
    def fetch_prepare_actors(content_df, df_content, df_actor, result_not_in_df):
        try:
            actor_content_df = pd.merge(content_df, df_actor, left_on=CONTENT_ID, right_on=CONTENT_ID, how=LEFT)

            actors = []
            for actor_id in actor_content_df[ACTOR_ID].values:
                if not pd.isna(actor_id):
                    actor = {ACTOR_ID: int(actor_id)}
                    if actor not in actors:
                        actors.append(actor)

            if len(actors) > 0:
                content_df[ACTORS] = [actors]
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df
    
    @staticmethod
    def fetch_prepare_actors_1(content_df, df_content, df_actor, result_not_in_df):
        try:
            actor_content_df = pd.merge(content_df, df_actor, left_on=CONTENT_ID, right_on=CONTENT_ID, how=LEFT)
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df, actor_content_df

    @staticmethod
    def fetch_prepare_subcategory(content_df, df_content, result_not_in_df):
        try:
            list_sub_category_ids = []
            if not pd.isna(df_content[SUBCATEGORY_ID].loc[0]):
                dict_sub_category1 = {SUBCATEGORY_ID: int(df_content[SUBCATEGORY_ID].loc[0])}
                list_sub_category_ids.append(dict_sub_category1)

            content_df[SUBCATEGORY] = [list_sub_category_ids]

        except Exception:
            result_not_in_df = df_content

        return content_df, result_not_in_df

    @staticmethod
    def fetch_prepare_category(content_df, df_content, result_not_in_df):
        try:
            list_category_ids = []
            if not pd.isna(df_content[CATEGORY_ID].loc[0]):
                dict_category1 = {CATEGORY_ID: int(df_content[CATEGORY_ID].loc[0])}
                list_category_ids.append(dict_category1)

            content_df[CATEGORY] = [list_category_ids]
            #content_df[CATEGORY] = ast.literal_eval(content_df[CATEGORY])
        except Exception:
            result_not_in_df = df_content
        return content_df, result_not_in_df


class UserBehaviourUtils:

    @staticmethod
    def fetch_prepare_customer_id(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[CUSTOMER_ID] = [str(vm_df[CUSTOMER_ID].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_created_on(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[CREATED_ON] = [pd.to_datetime(vm_df[CREATED_ON].loc[0], unit='s')]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_country_id(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[COUNTRY_ID] = [str(vm_df[COUNTRY_ID].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_region_name(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[REGION_NAME] = [str(vm_df[REGION_NAME].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_devops(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[DEVOPS] = [str(vm_df[DEVOPS].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_attribute(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[ATTRIBUTE1] = [str(vm_df[ATTRIBUTE1].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_video_id(video_measure_df, vm_df, result_not_in_df):
        try:
            video_measure_df[VIDEO_ID1] = [int(vm_df[VIDEO_ID1].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_category1(video_measure_df, vm_df, result_not_in_df):
        try:
            if not pd.isna(vm_df[CATEGORY1].loc[0]):
                category = []
                for category_id in vm_df[CATEGORY1]:
                    if not pd.isna(category_id):
                        category_id = {CATEGORY_ID: int(category_id)}
                        category.append(category_id)

                if len(category) > 0:
                    video_measure_df[CATEGORY] = [category]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_category2(video_measure_df, vm_df, result_not_in_df):
        try:
            if not pd.isna(vm_df[CATEGORY2].loc[0]):
                subcategory = []
                for subcategory_id in vm_df[CATEGORY2]:
                    if not pd.isna(subcategory_id):
                        subcategory_id = {SUBCATEGORY_ID: int(subcategory_id)}
                        subcategory.append(subcategory_id)

                if len(subcategory) > 0:
                    video_measure_df[SUBCATEGORY] = [subcategory]

        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_duration(video_measure_df, vm_df, result_not_in_df):
        try:
            if not pd.isna(vm_df[DURATION].loc[0]) and vm_df[DURATION].values is not None:
                video_measure_df[DURATION] = [int(vm_df[DURATION].loc[0])]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_tags_df(video_measure_df, df_content_having_tag, vm_df, result_not_in_df):
        try:
            tags_content_df = pd.merge(video_measure_df, df_content_having_tag, left_on=VIDEO_ID1, right_on=CONTENT_ID,
                                       how=LEFT)

            tags = []
            for tag_id in tags_content_df[TAGS_ID].values:
                if not pd.isna(tag_id):
                    tag = {TAGS_ID: int(tag_id)}
                    tags.append(tag)

            if len(tags) > 0:
                video_measure_df[TAGS] = [tags]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_actor_df(video_measure_df, df_content_having_actor, vm_df, result_not_in_df):
        try:
            actor_content_df = pd.merge(video_measure_df, df_content_having_actor, left_on=VIDEO_ID1,
                                        right_on=CONTENT_ID, how=LEFT)

            actors = []
            for actor_id in actor_content_df[ACTOR_ID].values:
                if not pd.isna(actor_id):
                    actor = {ACTOR_ID: int(actor_id)}
                    actors.append(actor)

            if len(actors) > 0:
                video_measure_df[ACTORS] = [actors]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df

    @staticmethod
    def fetch_prepare_director_df(video_measure_df, df_content_having_director, vm_df, result_not_in_df):
        try:
            df_content_having_director = df_content_having_director.rename({ACTOR_ID: DIRECTOR_ID}, axis=1)
            director_content_df = pd.merge(video_measure_df, df_content_having_director, left_on=VIDEO_ID1,
                                           right_on=CONTENT_ID, how=LEFT)

            directors = []
            for director_id in director_content_df[DIRECTOR_ID].values:
                if not pd.isna(director_id):
                    director = {DIRECTOR_ID: int(director_id)}
                    directors.append(director)

            if len(directors) > 0:
                video_measure_df[DIRECTORS] = [directors]
        except Exception:
            result_not_in_df = vm_df
        return video_measure_df, result_not_in_df


class UserProfileUtils:

    @staticmethod
    def fetch_prepare_customer_id(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[CUSTOMER_ID] = [str(cm_df[CUSTOMER_ID].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_prepare_birthday_id(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[BIRTHDAY] = [pd.to_datetime(cm_df[BIRTHDAY].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_prepare_gender(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[GENDER] = [str(cm_df[GENDER].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_prepare_created_on(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[CUSTOMER_CREATED_ON] = [pd.to_datetime(cm_df[CUSTOMER_CREATED_ON].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_prepare_modified_on(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[CUSTOMER_MODIFIED_ON] = [pd.to_datetime(cm_df[CUSTOMER_MODIFIED_ON].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_prepare_ud_key(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[UD_KEY] = [int(cm_df[UD_KEY].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_user_pay_tv(customer_df, df_user_pay_tv, cm_df, result_not_in_df):
        try:
            customer_df = pd.merge(customer_df, df_user_pay_tv, left_on=UD_KEY,
                                   right_on=UD_KEY, how=LEFT)

            customer_df = customer_df.drop(UD_KEY, axis=1)

            customers_pay_tvs = []
            for payTv_id in customer_df[PAYTVPROVIDER_ID].values:
                if not pd.isna(payTv_id):
                    customer = {PAYTVPROVIDER_ID: int(customer_df[PAYTVPROVIDER_ID].loc[0])}
                    customers_pay_tvs.append(customer)

            if len(customers_pay_tvs) > 0:
                customer_df[PAYTVPROVIDER_ID] = [customers_pay_tvs]

        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df

    @staticmethod
    def fetch_age(customer_df, cm_df, result_not_in_df):
        try:
            customer_df[AGE] = [int(cm_df[AGE].loc[0])]
        except Exception:
            result_not_in_df = cm_df
        return customer_df, result_not_in_df
