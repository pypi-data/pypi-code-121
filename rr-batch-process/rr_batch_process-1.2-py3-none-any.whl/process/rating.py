import numpy as np
import pandas as pd
from rankset.common import my_sql
from sklearn.linear_model import Ridge
from rr_batch.constants import General, Keys
from rr_batch.sql import Get


class CalculateRating:
    def __init__(self, tour_id: int, team_id: int, rival_team_name: str):
        self.__tour_id = tour_id
        self.__team_id = team_id
        self.__rival_team_name = rival_team_name
        self.__team_data_df = self.__get_data
        self.__df_team = None
        self.__df_rival = None

    @property
    def __get_data(self):
        db = my_sql.MySqlConnection(database=General.SOFA_SCORE_DB_NAME)
        data = db.get_data(query=Get.get_goals_data(self.__tour_id, self.__team_id), return_data_frame=True,
                           close_connection=True)
        return data

    def __add_goal_difference_section(self):
        """First, we create the goal_difference variable as the difference between home_goals and visitor_goals. It is
        greater than 0 when the home team wins and less than 0 when the home team loses while being 0 when two teams tie. """
        self.__team_data_df['goal_difference'] = self.__team_data_df['team_goals'] - self.__team_data_df['rival_goals']

        # create new variables to show home team win or loss result
        """We also add two indicators home_win and home_loss to consider the home advantage impact on the teams."""
        self.__team_data_df['win'] = np.where(self.__team_data_df['goal_difference'] > 0, 1, 0)
        self.__team_data_df['loss'] = np.where(self.__team_data_df['goal_difference'] < 0, 1, 0)

    def __set_dummy_variable_matrices_section(self):
        """Next, we create two dummy variable matrices df_visitor and df_home recording the visiting and home team."""
        # self.__df_team = pd.get_dummies(self.__team_data_df['team_name'], dtype=np.int64)
        self.__df_team = pd.get_dummies(self.__team_data_df['rival_name'], dtype=np.int64)
        self.__df_rival = pd.get_dummies(self.__team_data_df['rival_name'], dtype=np.int64)

    def __model_section(self):
        # subtract home from visitor
        # df_model = self.__df_team.sub(self.__df_rival)
        df_model = self.__df_team
        df_model['goal_difference'] = self.__team_data_df['goal_difference']
        df_model = df_model.dropna(axis='columns')
        # print(df_model)
        """It is a linear regression model with an additional term as the penalty.
         Due to multicollinearity among the independent
        variables, the traditional linear regression doesn’t create stable results.
        Fit the ridge regression model
        We use the goal_difference feature as the target variable."""
        df_train = df_model  # not required, but I like to rename my dataframe with the name train.
        lr = Ridge(alpha=0.001, max_iter=1000)
        x = df_train.drop(['goal_difference'], axis=1)
        y = df_train['goal_difference']
        lr.fit(x, y)
        final_df = pd.DataFrame(data={'team': x.columns, 'rating': lr.coef_}).sort_values(by='rating', ascending=False)
        if not self.__rival_team_name:
            return final_df
        else:
            if self.__rival_team_name in str(final_df):
                return General.DECIMAL_FORMAT.format(
                    float(final_df[final_df[Keys.TEAM] == self.__rival_team_name].values[0][1]))

    def get_team_flow(self):
        if len(self.__team_data_df) > 0:
            self.__add_goal_difference_section()
            self.__set_dummy_variable_matrices_section()
            return self.__model_section()

# d = CalculateRating(tour_id=266, team_id=5399).get_team_flow()
# print(d)
