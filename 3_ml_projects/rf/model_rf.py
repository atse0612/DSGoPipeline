#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import plotly.express as px
import mlflow # New
import mlflow.sklearn # New

mlflow.set_experiment("predicting_wind_solar") # New, optional

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


# In[5]:


df = pd.read_csv("germany.csv", parse_dates=[0], index_col=0)
df.head()


# In[6]:


X = df[["windspeed", "temperature", "rad_horizontal", "rad_diffuse"]]
y = df[["solar_GW", "wind_GW"]]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# In[15]:


for n_estimators in [4, 9, 25, 64]:
    for max_depth in [2, 4, 10]: # Nasty brute force hyperparameter search
        with mlflow.start_run(run_name="rf"): # New, run_name optional
            model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
            model.fit(X_train, y_train)

            y_predict = model.predict(X_test)
            rmse, mae, r2 = eval_metrics(y_test, y_predict)

            print(f"n_estimators={n_estimators}, max_depth={max_depth}, RMSE={rmse:0.2f}")

            mlflow.log_param("n_estimators", n_estimators) # New
            mlflow.log_param("max_depth", max_depth) # New
            mlflow.log_metric("rmse", rmse) # New
            mlflow.log_metric("mae", mae) # New
            mlflow.log_metric("r2", r2) # New
            mlflow.sklearn.log_model(model, "model") # New


# In[12]:


fig = px.scatter(x=y_test["solar_GW"], y=y_predict[:, 0], 
             color=X_test["temperature"], range_color=[-5, 25],
             color_continuous_scale="ice")
fig.update_layout(xaxis_title="Actual Solar", 
                  yaxis_title="Predicted Solar", 
                  coloraxis_colorbar=dict(title="temperature"))
fig.show()


# In[13]:


fig = px.scatter(x=y_test["wind_GW"], y=y_predict[:, 1], 
                 color=X_test["windspeed"], range_color=[0, 8],
                color_continuous_scale="ice")
fig.update_layout(xaxis_title="Actual Wind", 
                  yaxis_title="Predicted Wind",
                  coloraxis_colorbar=dict(title="windspeed"))
fig.show()


# In[ ]:



