# Projet Getaround
<img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Getaround-Logo---Purple-sq.png" alt="UBER LOGO" style="height: 100px;" />


## 📌 Context
Getaround is a peer-to-peer car rental platform.
The goal of this project is twofold:
1. Analyse the impact of late returns and recommend a minimum delay threshold between two rentals.
2. Optimize pricing with a Machine Learning model exposed through a FastAPI API 
3. Add a Gradio application for user-friendly API usage

## 🗂️ Project content
* <strong>EDA & Analytics</strong>: study of rentals delays, threshold & scope impact, interactive dashboard
* <strong>ML Model</strong>: trained on "get_around_pricing_project.csv" using preprocessing pipeline, XGBoost and GridsearchCV.
* <strong>MLFlow</strong>: experiment tracking, modeland preprocessor storage.
* <strong>Infrastructure</strong>: 
    * Backend store: NeonDB
    * Artifact store: AWS S3
    * Tracking server: MLFlow(hosted)
* <strong>FastAPI</strong>: endpoints /predict and /predicts
* <strong>Docker</strong>: reproducible environment for deployment.
* <strong>Gradio app</strong>: user-friendly interface for testing predictions

### Clone the repository:
```
git clone https://github.com/JCU75/Jedha.git
```
### Go to the project folder:
```
Bloc5/
```

## 🔗 Links

* [Dashboard](https://ungjeanclaude-getaround-analysis-feature.hf.space/)
* [API](https://ungjeanclaude-api-get-around.hf.space/docs#/default/root__get)
* [Gradio App](https://ungjeanclaude-rent-estimate.hf.space/) 

## Built With
  

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" alt="Python logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Jupyter_logo.svg" alt="Jupyter logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/ed/Pandas_logo.svg" alt="pandas logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg" alt="scikit learn logo" height="80"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/8/8a/Plotly-logo.png" alt="plotly logo" height="80"/>
  <img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="streamlit logo" height="80" >
  <img src="https://mlflow.org/docs/2.12.2/_static/MLflow-logo-final-black.png" alt="MLFlow logo" height="80">
  <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="fastAPI logo" height="80" >
  <img src="https://www.gradio.app/_app/immutable/assets/gradio.CHB5adID.svg" alt="gradio logo" height="80">
</p>


## Authors

[Jean-claude Ung](https://github.com/JCU75)