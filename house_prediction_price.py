import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, cross_val_predict, KFold
import xgboost as xgb
from sklearn.preprocessing import StandardScaler, PolynomialFeatures,MinMaxScaler
from sklearn.pipeline import Pipeline
plt.style.use('seaborn')

#importing csv file with seperator ";" into pandas
df = pd.read_csv(r'C:\Users\meysam-sadat\PycharmProjects\houseprice_prediction\Predicting_real_estate_prices_using_scikit-learn\house_price.csv',sep=";")

def changing_into_numeric(data):
    data = data[data.price_new.str.contains("aanvraag") == False].dropna()
    data[['price_new']] = data[['price_new']].apply(pd.to_numeric)
    return data

def removing_outliers_price(data):
    data = data[np.abs(data["price_new"] - data["price_new"].mean()) <= (3 * data["price_new"].std())]
    plt.scatter(x='surface', y='price_new', data=data)
    return data

def removing_unrelated_features(df):
    df = df.drop(['zipcode_new','rooms_new'],axis=1)
    return df

def seperating_target_column_splite(df):
    y = df.price_new
    X = df.drop('price_new', axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
    return  X_train, X_test, y_train, y_test,X,y

# executing one by one
df = changing_into_numeric(df)
df = removing_outliers_price(df)
df = removing_unrelated_features(df)
X_train, X_test, y_train, y_test ,X,y = seperating_target_column_splite(df)


def model(pipeline, parameters, X_train, y_train, X, y):
    grid_object = GridSearchCV(estimator=pipeline,
                            param_grid=parameters,
                            cv=3,scoring='r2',
                            verbose=2,
                            n_jobs=-1,
                            refit=True)
    grid_object.fit(X_train, y_train)

    '''Results'''
    results = pd.DataFrame(pd.DataFrame(grid_object.cv_results_))
    results_sorted = results.sort_values(by=['mean_test_score'], ascending=False)
    print("##### Results")
    print(results_sorted)
    print("best_index", grid_object.best_index_)
    print("best_score", grid_object.best_score_)
    print("best_params", grid_object.best_params_)
    '''Cross Validation'''
    estimator = grid_object.best_estimator_
    '''
    if estimator.named_steps['scl'] == True:
        X = (X - X.mean()) / (X.std())
        y = (y - y.mean()) / (y.std())
    '''
    shuffle = KFold(n_splits=5,shuffle=True,random_state=0)
    cv_scores = cross_val_score(estimator,X,y.values.ravel(),cv=shuffle,scoring='r2')

    print("##### CV Results")
    print("mean_score", cv_scores.mean())

    '''Show model coefficients or feature importances'''

    try:
        print("Model coefficients: ", list(zip(list(X), estimator.named_steps['clf'].coef_)))
    except:
        print("Model does not support model coefficients")

    try:
        print("Feature importances: ", list(zip(list(X), estimator.named_steps['clf'].feature_importances_)))
    except:
        print("Model does not support feature importances")

    '''Predict along CV and plot y vs. y_predicted in scatter'''

    y_pred = cross_val_predict(estimator, X, y, cv=shuffle)

    plt.scatter(y, y_pred)
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    plt.plot([xmin, xmax], [ymin, ymax], "g--", lw=1, alpha=0.4)
    plt.xlabel("True prices")
    plt.ylabel("Predicted prices")
    plt.annotate(' R-squared CV = {}'.format(round(float(cv_scores.mean()), 3)), size=9,xy=(xmin,ymax), xytext=(10, -15), textcoords='offset points')
    plt.annotate(grid_object.best_params_, size=9, xy=(xmin, ymax), xytext=(10, -35), textcoords='offset points', wrap=True)
    plt.title('Predicted prices (EUR) vs. True prices (EUR)')
    plt.show()

# Pipeline and Parameters - Linear Regression
pipe_LR = Pipeline([('scl', StandardScaler()),('clf', LinearRegression())])
param_LR = {}

# Pipeline and Parameters - XGBoost
pipe_xgb = Pipeline([('clf', xgb.XGBRegressor())])
param_xgb = {'clf__max_depth':[5],
             'clf__min_child_weight':[6],
             'clf__gamma':[0.01],
             'clf__subsample':[0.7],
             'clf__colsample_bytree':[1]}

# Pipeline and Parameters - KNN
pipe_knn = Pipeline([('clf', KNeighborsRegressor())])
param_knn = {'clf__n_neighbors':[5, 10, 15, 25, 30]}

# Pipeline and Parameters - Lasso
pipe_lasso = Pipeline([('scl', StandardScaler()),('clf', Lasso(max_iter=1500))])
param_lasso = {'clf__alpha': [0.01, 0.1, 1, 10]}

# Pipeline and Parameters - Ridge
pipe_ridge = Pipeline([('scl', StandardScaler()),('clf', Ridge(max_iter='any'))])
param_ridge = {'clf__alpha': [0.01, 0.1, 1, 10]}

# Pipeline and Parameters - Polynomial Regression
pipe_poly = Pipeline([('scl', StandardScaler()),
                       ('polynomial', PolynomialFeatures()),
                       ('clf', LinearRegression())])

param_poly = {'polynomial__degree': [2, 4, 6]}


# Pipeline and Parameters - Decision Tree Regression
pipe_tree = Pipeline([('clf', DecisionTreeRegressor())])
param_tree = {'clf__max_depth': [2, 5, 10],
             'clf__min_samples_leaf': [5,10,50,100]}

# Pipeline and Parameters - Random Forest
pipe_forest = Pipeline([('clf', RandomForestRegressor())])
param_forest = {'clf__n_estimators': [10, 20, 50],
                'clf__max_features': [None, 1, 2],
                'clf__max_depth': [1, 2, 5]}

# Pipeline and Parameters - MLP Regression
pipe_neural = Pipeline([('scl', StandardScaler()),('clf', MLPRegressor())])
param_neural = {'clf__alpha': [0.001, 0.01, 0.1, 1, 10, 100],
                'clf__hidden_layer_sizes': [(5),(10,10),(7,7,7)],
                'clf__solver': ['lbfgs'],
                'clf__activation': ['relu', 'tanh'],
                'clf__learning_rate' : ['constant', 'invscaling']}


pipe_svr = Pipeline([('scl', StandardScaler()),('clf', SVR())])
param_svr = {}


# Execute model hyperparameter tuning and crossvalidation
model(pipe_svr, param_svr, X_train, y_train, X, y)
model(pipe_ols, param_ols, X_train, y_train, X, y)
model(pipe_xgb, param_xgb, X_train, y_train, X, y)
model(pipe_knn, param_knn, X_train, y_train, X, y)
model(pipe_lasso, param_lasso, X_train, y_train, X, y)
model(pipe_ridge, param_ridge, X_train, y_train, X, y)
model(pipe_poly, param_poly, X_train, y_train, X, y)
model(pipe_tree, param_tree, X_train, y_train, X, y)
model(pipe_forest, param_forest, X_train, y_train, X, y)
model(pipe_neural, param_neural, X_train, y_train, X, y)

