from neo4j import GraphDatabase as GD
import pandas as pd
from sklearn.linear_model import LogisticRegression
import numpy as np

import pkg_resources
import os

DATA_PATH = pkg_resources.resource_filename(__name__, 'data/')

X_PATH = os.path.join(DATA_PATH, 'x_train.csv')
Y_PATH = os.path.join(DATA_PATH, 'y_train.csv')
CAT_PATH = os.path.join(DATA_PATH, 'categories_sample.csv')
RTG_PATH = os.path.join(DATA_PATH, 'ratings_sample.csv')
POD_PATH = os.path.join(DATA_PATH, 'podcast_sample_title.csv')

class PodcastRecommendation:
    def __init__(self, uri:str, auth:str, x_path:str = None, y_path:str = None, verbose:bool = False)->None:
        """Creates object. Reads files to train Logistic Regression model.
        

        Args:
            uri (str): neo4j uri
            auth (str): neo4j (user, psw)
            x_path (str, optional): path to x_train. Defaults to X_PATH.
            y_path (str, optional): path to y_train. Defaults to Y_PATH.
            verbose (bool, optional): verbose. Defaults to False.
        """ 
        if x_path is None:
            x_path = X_PATH 
        if y_path is None:
            y_path = Y_PATH
        
        
        self.driver = GD.driver(uri, auth = auth)
        self.features = ['cat_based', 'cat_cnt', 'user_based', 'user_cnt',
            'adamic_adar', 'resource_allocation', 'link_cnt', 'cat_avg', 'user_avg',
            'adar_avg', 'ra_avg']
        self.lr = LogisticRegression(solver='liblinear', C=0.5)
        if verbose: print("Reading x_train")
        X = pd.read_csv(x_path)
        if verbose: print("Reading y_train")
        Y = pd.read_csv(y_path)
        if verbose: print("Training model")
        self.lr.fit(X[self.features], Y.values.reshape(1,-1)[0])
        if verbose: print("Training complete")
        
        if verbose: print("Reading podcasts")
        self.pod = pd.read_csv(POD_PATH)
    
    def build_graph(self, cat_path:str = None, rtg_path:str = None, delete_all:bool = True,
                    verbose:bool = False)->None:
        """Builds graph in neo4j

        Args:
            cat_path (str, optional): path to categories_sample. Defaults to CAT_PATH.
            rtg_path (str, optional): path to ratings_sample. Defaults to RTG_PATH.
            delete_all (bool, optional): if to delete graph before writting. Defaults to True.
            verbose (bool, optional): verbose. Defaults to False.
        """ 
        if cat_path is None:
            cat_path = CAT_PATH
        if rtg_path is None:
            rtg_path = RTG_PATH
        
        if delete_all:
            if verbose: print("Deleting all nodes and relationships")
            self.delete_all()
        
        if verbose: print("Reading categories")
        cat = pd.read_csv(cat_path)
        if verbose: print("Reading ratings")
        rtg = pd.read_csv(rtg_path)
        
        if verbose: print("Creating podcasts, categories and IsA")
        cat.apply(self.build_cat, axis=1)
        
        if verbose: print("Creating users, categories and ratings")
        rtg.apply(self.build_rtg, axis=1)
        
        if verbose: print("Build complete")
        
        
    def build_cat(self, row:pd.Series)->None:
        """Builds relations in categories_sample dataset

        Args:
            row (pd.Series): dataframe row
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__build_cat, row['category'], row['category_id'], row['podcast_id'])
            
    @staticmethod
    def __build_cat(tx, category:str, category_id:str, podcast_id:str)->None:
        """Helper for build_cat

        Args:
            tx (_type_): transaction
            category (str): category name
            category_id (str): category id
            podcast_id (str): podcast id
        """
        query = (
            "MERGE (p:Podcast{id: $podcast_id}) "
            "MERGE (c:Category{id: toInteger($category_id), name: $category}) "
            "MERGE (p)-[r:IsA]->(c) "
        )
        tx.run(query, podcast_id=podcast_id, category_id=category_id, category=category)
        
    def build_rtg(self, row:pd.Series)->None:
        """Builds relations in ratings_sample dataset

        Args:
            row (pd.Series): dataframe row
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__build_rtg, row['user_id'], row['podcast_id'], row['rating'])
            
    @staticmethod
    def __build_rtg(tx, user_id:str, podcast_id:str, rating:int)->None:
        """Helper for build_rtg

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id
            rating (int): rating
        """
        query = (
            "MERGE (u:User{id: $user_id}) "
            "MERGE (p:Podcast{id: $podcast_id}) "
            "MERGE (u)-[r:Rating{rating: toInteger($rating)}]->(p) "
        )
        tx.run(query, user_id=user_id, podcast_id=podcast_id, rating=rating)
    
    
    def close(self)->None:
        """Closes driver.
        """
        self.driver.close()
       
    def delete_all(self)->None:
        """Deletes all elements in the graph
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__delete_all)
            
    @staticmethod
    def __delete_all(tx)->None:
        """Helper for delete all

        Args:
            tx (_type_): transaction
        """
        query = "MATCH (m)-[r]->(n) DELETE m, n, r"
        tx.run(query)
     
    def recommend(self, user_id:str)->pd.DataFrame:
        """Generates podcast recommendation for user

        Args:
            user_id (str): user id

        Returns:
            pd.DataFrame: podcasts and probabilities
        """
        df = self.gen_df(user_id)
        
        df = self.gen_data(df)
        df['proba'] = self.lr.predict_proba(df[self.features])[:,1]
        df = df.sort_values(by='proba', ascending=False)
        
        pod = self.pod.copy().set_index('podcast_id')
        df['title'] = df['podcast_id'].map(pod['title'])
        
        return df[['proba', 'title']]
    
    def gen_data(self, df:pd.DataFrame)->pd.DataFrame:
        """Generates data for podcast recommendation

        Args:
            df (pd.DataFrame): podcasts

        Returns:
            pd.DataFrame: dataframe with attributes
        """
        c_names = ['cat_based', 'cat_cnt', 'user_based', 'user_cnt',
                   'adamic_adar', 'resource_allocation', 'link_cnt']
        df[c_names] = df.apply(self.gen_data_row, axis=1, result_type='expand')
        df['cat_avg'] = df['cat_based'] / df['cat_cnt']
        df['user_avg'] = df['user_based'] / df['user_cnt']
        df['adar_avg'] = df['adamic_adar'] / df['link_cnt']
        df['ra_avg'] = df['resource_allocation'] / df['link_cnt']
        df = df.fillna(0)
        return df 
    
    def gen_data_row(self, row:pd.Series)->list:
        """Helper for gen_data

        Args:
            row (pd.Series): row of data

        Returns:
            list: list of attributes
        """
        u_id, p_id = row['user_id'], row['podcast_id']
        
        result = self.get_cat_based(u_id, p_id)
        result += self.get_user_based(u_id, p_id)
        result += self.adamic_adar(u_id, p_id)
        result += self.resource_allocation(u_id, p_id)
        
        return result
    
    def delete_rtg(self, user_id:str, podcast_id:str)->None:
        """Deletes rating relationship

        Args:
            user_id (str): user id
            podcast_id (str): podcast id
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__delete_rtg, user_id, podcast_id)
    
    @staticmethod
    def __delete_rtg(tx, user_id:str, podcast_id:str)->None:
        """Helper for delete_rtg

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id
        """
        query = (
            "MATCH (u:User)-[r]->(p:Podcast) "
            "WHERE u.id = $user_id AND p.id = $podcast_id "
            "DELETE r"
        )
        tx.run(query, user_id=user_id, podcast_id=podcast_id)

        
    def create_rtg(self, user_id:str, podcast_id:str, rating:int)->None:
        """Create rating relationship

        Args:
            user_id (str): user id
            podcast_id (str): podcast id
            rating (int): rating
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__create_rtg, user_id, podcast_id, rating)
    
    @staticmethod
    def __create_rtg(tx, user_id:str, podcast_id:str, rating:int)->None:
        """Helper for create_rtg

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id
            rating (int): rating
        """
        query = (
            "MATCH (u:User) MATCH (p:Podcast) "
            "WHERE u.id = $user_id AND p.id = $podcast_id "
            "MERGE (u)-[r:Rating{rating:toInteger($rating)}]->(p) "
        )
        tx.run(query, user_id=user_id, podcast_id=podcast_id, rating=rating)
        
    def create_user(self, user_id:str)->None:
        """Creates user

        Args:
            user_id (str): user id
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__create_user, user_id)
    
    @staticmethod
    def __create_user(tx, user_id:str)->None:
        """Helper for create_user

        Args:
            tx (_type_): transaction
            user_id (str): user id
        """
        query = (
            "MERGE (u:User{id:$user_id}) "
        )
        tx.run(query, user_id=user_id)
        
    def create_podcast(self, podcast_id:str, title:str)->None:
        """Creates a podcast

        Args:
            podcast_id (str): podcast id
            title (str): title
        """
        self.pod.loc[len(self.pod)] = [podcast_id, title]
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__create_podcast, podcast_id)
    
    @staticmethod
    def __create_podcast(tx, podcast_id:str)->None:
        """Helper for create_podcast

        Args:
            tx (_type_): transaction
            podcast_id (str): podcast id
        """
        query = (
            "MERGE (u:Podcast{id:$podcast_id}) "
        )
        tx.run(query, podcast_id=podcast_id)
        
    def create_category(self, category:str, category_id:int)->None:
        """Creates category

        Args:
            category (str): category name
            category_id (int): category id
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__create_category, category, category_id)
    
    @staticmethod
    def __create_category(tx, category:str, category_id:int)->None:
        """Helper for create_category

        Args:
            tx (_type_): transaction
            category (str): category name
            category_id (int): category id
        """
        query = (
            "MERGE (u:Podcast{id:$category_id, name:$category}) "
        )
        tx.run(query, category_id=category_id, category=category)
        
    def create_IsA(self, podcast_id:str, category:str)->None:
        """Creates an IsA relationship

        Args:
            podcast_id (str): podcast id
            category (str): category name
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__create_IsA, podcast_id, category)
    
    @staticmethod
    def __create_IsA(tx, podcast_id:str, category:str)->None:
        """Helper for create_IsA

        Args:
            tx (_type_): transaction
            podcast_id (str): podcast id
            category (str): category name
        """
        query = (
            "MATCH (c:Category) MATCH (p:Podcast) "
            "WHERE c.name = $category AND p.id = $podcast_id "
            "MERGE (p)-[r:IsA]->(c) "
        )
        tx.run(query, category=category, podcast_id=podcast_id)
        
    def get_cat_based(self, user_id:str, podcast_id:str)->list:
        """Generates data from paths
        (user)->(podcast)->(category)<-(podcast)

        Args:
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: sum of ratings and count of paths
        """
        with self.driver.session() as sess:
            result = sess.write_transaction(
                self.__get_cat_based, user_id, podcast_id)
            return result
        
    @staticmethod
    def __get_cat_based(tx, user_id:str, podcast_id:str)->list:
        """Helper for get_cat_based

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: sum of ratings and count of paths
        """
        query = (
            "MATCH (u:User)-[r]->(Podcast)-->(Category)<--(p:Podcast) "
            "WHERE u.id = $user_id AND p.id = $podcast_id "
            "RETURN r"
        )
        result = tx.run(query, user_id=user_id, podcast_id=podcast_id)
        total = 0
        cnt = 0
        for rec in result:
            total += rec['r']['rating']
            cnt += 1
        return [total, cnt]
    
    def get_user_based(self, user_id:str, podcast_id:str)->list:
        """Generates data from paths
        (user)->(podcast)<-(user)->(podcast)

        Args:
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: sum of ratings and count of paths
        """
        with self.driver.session() as sess:
            result = sess.write_transaction(
                self.__get_user_based, user_id, podcast_id)
            return result
        
    @staticmethod
    def __get_user_based(tx, user_id:str, podcast_id:str)->list:
        """Helper for get_user_based

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: sum of ratings and count of paths
        """
        query = (
            "MATCH (u:User)-[r1]->(Podcast)<-[r2]->(User)-[r3]->(p:Podcast) "
            "WHERE u.id = $user_id AND p.id = $podcast_id "
            "RETURN r1.rating + r2.rating + r3.rating "
            "AS total"
        )
        result = tx.run(query, user_id=user_id, podcast_id=podcast_id)
        total = 0
        cnt = 0
        for rec in result:
            total += rec['total']
            cnt += 1
        return [total, cnt]
    
    def adamic_adar(self, user_id:str, podcast_id:str)->list:
        """Generates data from Adamic Adar metric

        Args:
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: adamic adar
        """
        with self.driver.session() as sess:
            result = sess.write_transaction(
                self.__adamic_adar, user_id, podcast_id)
            return result
        
    @staticmethod
    def __adamic_adar(tx, user_id:str, podcast_id:str)->list:
        """Helper for adamic_adar

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: adamic adar
        """
        query = (
            "MATCH (u:User)-[r]->(p1:Podcast) MATCH (p:Podcast)"
            "WHERE u.id = $user_id AND p.id = $podcast_id "
            "RETURN r.rating * gds.alpha.linkprediction.adamicAdar(p1, p) "
            "AS score "
        )
        result = tx.run(query, user_id=user_id, podcast_id=podcast_id)
        total = 0
        for rec in result:
            total += rec['score']
        return [total]
    
    def resource_allocation(self, user_id:str, podcast_id:str)->list:
        """Generates data from resource allocation metric

        Args:
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: resource allocation and count of paths
        """
        with self.driver.session() as sess:
            result = sess.write_transaction(
                self.__resource_allocation, user_id, podcast_id)
            return result
        
    @staticmethod
    def __resource_allocation(tx, user_id:str, podcast_id:str)->list:
        """Helper for resource_allocation

        Args:
            tx (_type_): transaction
            user_id (str): user id
            podcast_id (str): podcast id

        Returns:
            list: resource allocation and count of paths
        """
        query = (
            "MATCH (u:User)-[r]->(p1:Podcast) MATCH (p:Podcast)"
            "WHERE u.id = $user_id AND p.id = $podcast_id "
            "RETURN r.rating * gds.alpha.linkprediction.resourceAllocation(p1, p) "
            "AS score "
        )
        result = tx.run(query, user_id=user_id, podcast_id=podcast_id)
        total = 0
        cnt = 0
        for rec in result:
            total += rec['score']
            cnt += 1
        return [total, cnt]
    
    def gen_df(self, user_id:str)->pd.DataFrame:
        """Generates df with podcasts of interest

        Args:
            user_id (str): user id

        Returns:
            pd.DataFrame: dataframe with podcasts
        """
        podcasts = self.gen_podcasts(user_id)
        df = pd.DataFrame({'podcast_id':podcasts})
        if len(df) == 0:
            pod = self.pod.copy()
            df = pod[np.random.rand(len(pod)) < 0.2]
            df = df['podcast_id']
            df = df.iloc[:50,:]
        df['user_id'] = user_id
        return df.drop_duplicates().reset_index().iloc[:50, 1:]
        
    def gen_podcasts(self, user_id:str)->list:
        """Helper for gen_df. Uses paths (user)-[*3]->(podcast)

        Args:
            user_id (str): user id

        Returns:
            list: list with podcasts
        """
        with self.driver.session() as sess:
            result = sess.write_transaction(
                self.__gen_podcasts, user_id)
            return result
        
    @staticmethod
    def __gen_podcasts(tx, user_id:str)->list:
        """Helper for gen_podcasts

        Args:
            tx (): transaction
            user_id (str): user id

        Returns:
            list: podcasts
        """
        query = (
            "MATCH (u:User)-[*3]-(p:Podcast) "
            "WHERE u.id = $user_id "
            "RETURN p.id AS p_id "
        )
        result = tx.run(query, user_id=user_id)
        ans = []
        for rec in result:
            ans.append(rec['p_id'])
        return ans
    
    def delete_user(self, user_id:str)->None:
        """Deletes user

        Args:
            user_id (str): user id
        """
        with self.driver.session() as sess:
             sess.write_transaction(
                self.__delete_user, user_id)
        
    @staticmethod
    def __delete_user(tx, user_id:str)->None:
        """Helper for delete_user

        Args:
            tx (_type_): transaction
            user_id (str): user id
        """
        query = (
            "MATCH (u:User)-[r]->() WHERE u.id = $user_id "
            "DELETE r, u "
        )
        tx.run(query, user_id=user_id)
        
    def delete_podcast(self, podcast_id:str)->None:
        """Deletes podcast

        Args:
            podcast_id (str): podcast id
        """
        with self.driver.session() as sess:
             sess.write_transaction(
                self.__delete_podcast, podcast_id)
             
    @staticmethod
    def __delete_podcast(tx, podcast_id:str)->None:
        """Helper for delete_podcast

        Args:
            tx (_type_): transaction
            podcast_id (str): podcast id
        """
        query = (
            "MATCH (p:Podcast)-[r]-() WHERE p.id = $podcast_id "
            "DELETE r, p "
        )
        tx.run(query, podcast_id=podcast_id)
    
    def delete_cat(self, category:str)->None:
        """Deletes category

        Args:
            category (str): category name
        """
        with self.driver.session() as sess:
             sess.write_transaction(
                self.__delete_cat, category)
             
    @staticmethod
    def __delete_cat(tx, category:str)->None:
        """Helper for delete_cat

        Args:
            tx (_type_): transaction
            category (str): category name
        """
        query = (
            "MATCH (c:Category)<-[r]-() WHERE c.name = $category "
            "DELETE r, c "
        )
        tx.run(query, category=category)
    
    def delete_IsA(self, podcast_id:str, category:str)->None:
        """Deletes IsA relationship

        Args:
            podcast_id (str): podcast id    
            category (str): category name
        """
        with self.driver.session() as sess:
            sess.write_transaction(
                self.__delete_IsA, podcast_id, category)
    
    @staticmethod
    def __delete_IsA(tx, podcast_id:str, category:str)->None:
        """Helper for delete_IsA

        Args:
            tx (_type_): transaction
            podcast_id (str): podcast id
            category (str): category name
        """
        query = (
            "MATCH (p:Podcast)-[r]->(c:Category) "
            "WHERE p.id = $podcast_id AND c.name = $category "
            "DELETE r"
        )
        tx.run(query, podcast_id=podcast_id, category=category)