import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from sklearn.datasets import load_diabetes
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import train_test_split, \
    KFold, StratifiedKFold, \
    GridSearchCV, RandomizedSearchCV, \
    HalvingGridSearchCV, HalvingRandomSearchCV,\
    cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# 1
x, y = load_diabetes(return_X_y=True)
x_train, x_test , y_train, y_test = train_test_split(
    x, y, random_state=777, train_size=0.8,
)

scaler = MinMaxScaler()
# scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

n_splits = 5
kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=777)
# kfold = KFold(n_splits=n_splits, shuffle=True, random_state=777)

# n_estimators : [100,200,300,400,500,1000] 디폴트 100/ 1~inf/ 정수
# learning_rate : [0.1, 0.2, 0.3, 0.5, 1, 0.01, 0.001] 디폴트0.3 / 0~1/ eta
# max_depth : [None, 2, 3, 4, 5, 6, 7, 8, 9, 10] 디폴트 6 / 0~inf/ 정수
# gamma : [0, 1, 2, 3, 4, 5, 7, 10, 100] 디폴트 0 / 0~inf
# min_child_weight : [0, 0.01, 0.001, 0.1, 0.5, 1, 5, 10, 100] / 디폴트 1 / 0~inf
# subsample : [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1] 디폴트 1 / 0~1
# colsample_bytree : [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1] 디폴트 1 / 0~1
# colsample_bylevel : [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1] 디폴트 1 / 0~1
# colsample_bynode : [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1] 디폴트 1/ 0~1
# reg_alpha : [0, 0.1, 0.01, 0.001, 1, 2, 10] 디폴트0 / 0~inf / L1 절대값 가중치 규제
# / alpha
# reg_lambda : [0, 0.1, 0.01, 0.001, 1, 2, 10] 디폴트 1 / 0~inf / L2 제곱 가중치 규제
# / lambda

parameters = {
    'n_estimators' : [100],
    'learning_rate' : [0.1],
    'max_depth' : [5],
}

# model = XGBClassifier(random_state = 777)
model = XGBRegressor(random_state = 777)

model.fit(x_train, y_train)


results = model.score(x_test,y_test)
print('model.score :', results)

model.set_params(gamma=0.3)

model.fit(x_train, y_train)
results = model.score(x_test,y_test)
print('model.score2 :', results)

model.set_params(learning_rate=0.01)
model.fit(x_train, y_train)
results = model.score(x_test,y_test)
print('model.score3 :', results)

model.set_params(n_estimators=1000)   
model.fit(x_train, y_train)
results = model.score(x_test,y_test)
print('model.score4 :', results)

model.set_params(learning_rate=0.005, n_estimators=400,
                 random_state=666,
                 reg_alpha=0, 
                 reg_lambda=1,
                 min_child_weight=10, 
                 )
model.fit(x_train, y_train)
results = model.score(x_test,y_test)
print('model.score4 :', results)
print('model.get_params :', model.get_params())