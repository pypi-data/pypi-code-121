import pandas as pd
from surprise import Reader, Dataset, SVD
from surprise.model_selection import cross_validate

def Rate(user_id,item_id,rating,time):
    f = open("TulipsData.txt","a+")
    f.write(str(user_id) + "," + str(item_id) + "," + str(rating) + "," + str(time)+"\n")
    f.close()


def TOP10(user_id):
    
    r_cols = ['user_id', 'item_id', 'rating', 'time']
    
    ratings = pd.read_csv('TulipsData.txt', sep=',', names=r_cols, encoding='latin-1')
    reader = Reader()
    
    data = Dataset.load_from_df(ratings[['user_id', 'item_id', 'rating']], reader)
    
    svd = SVD()
    
    cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=2, verbose=True)
    
    trainset = data.build_full_trainset()
    testset = trainset.build_testset()
    predictions = svd.test(testset)
    model_pred = pd.DataFrame([[i.uid, i.iid, i.est] for i in predictions], columns=['user_id', 'item_id', 'svd'])
    
    anti_testset = trainset.build_anti_testset()
    anti_predictions = svd.test(anti_testset)
    model_pred_anti = pd.DataFrame([[i.uid, i.iid, i.est] for i in anti_predictions], columns=['user_id', 'item_id', 'svd'])
    model_pred = pd.concat([model_pred, model_pred_anti], ignore_index=True)
    
    
    svd_p = pd.pivot_table(model_pred, values='svd', index='user_id', columns='item_id')
    MovieIDS = strings = [str(x) for x in svd_p.columns] 
    
    Score = []
    for i in MovieIDS:
        Score.append([svd.predict(user_id, (i))[3],(i)])
        
    Score.sort(reverse=True)
    
    Result = []
    M = 0
    for i in Score :
        if((len(ratings[(ratings['user_id']==user_id) & (ratings['item_id']==i[1])]))==0):
            Result.append(i[1])
        M+=1
        if(M==10 or M==len(Score)):
            break
    return Result


    
