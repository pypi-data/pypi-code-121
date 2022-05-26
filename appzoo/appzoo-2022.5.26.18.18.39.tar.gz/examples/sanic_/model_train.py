#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : model_train
# @Time         : 2019-08-29 17:12
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from sklearn.preprocessing import MaxAbsScaler

X = [[1],[2],[3]]

model = MaxAbsScaler()

print(model.fit_transform(X))

import joblib
joblib.dump(model, './sklearn.MaxAbsScaler.demo')