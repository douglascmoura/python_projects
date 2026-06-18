# 🚢 Análise Preditiva do Titanic: Machine Learning e Visualização de Dados

Este repositório contém uma análise completa do clássico dataset do Titanic. O objetivo é explorar os dados de sobrevivência dos passageiros e construir modelos preditivos de classificação para determinar quem sobreviveria ao naufrágio.

O projeto une a exploração visual detalhada através de gráficos interativos com a aplicação de algoritmos de Machine Learning otimizados e pipelines robustos.

---

## 🎯 Fundamentação Teórica e Objetivo

O problema consiste em uma tarefa de classificação binária baseada no perfil e nas características da viagem dos passageiros (idade, gênero, classe do bilhete, tarifa, família a bordo, etc). A variável alvo (Target) é `Survived`, indicando sobrevivência (1) ou óbito (0).

A modelagem engloba o tratamento de dados faltantes (imputação), engenharia de atributos avançada (Feature Engineering, como extração de pronomes de tratamento e agrupamento familiar) e o treinamento de três algoritmos essenciais:
* **Logistic Regression:** Para estabelecer uma baseline probabilística robusta.
* **Random Forest:** Um poderoso *ensemble* baseado em árvores de decisão.
* **XGBoost (Gradient Boosting):** Algoritmo de alta performance selecionado para maximizar a precisão na submissão final do Kaggle.

---

## 🚀 Diferenciais Técnicos e Performance

* **Otimização de Hiperparâmetros:** Utilização de métodos de busca como `GridSearchCV` e `RandomizedSearchCV` aliados à validação cruzada (Cross-Validation com 5 *folds*) para garantir modelos precisos e sem *overfitting*.
* **Prevenção de Data Leakage:** Pipeline de pré-processamento estruturado com rigorosa separação de Treino e Validação (80/20) aplicando o escalonamento (StandardScaler) da maneira correta.
* **Visualização Interativa Premium:** Geração de painéis de performance (Dashboards) comparativos utilizando a biblioteca `Plotly`. Os gráficos incluem matrizes de confusão, curvas ROC-AUC e Precision-Recall, com um design consistente em *Dark Theme*.

---

## 📂 Estrutura do Repositório

```text
├── analise_titanic_ml.ipynb              # Notebook central de exploração, Feature Engineering e modelagem
├── train.csv                             # Dataset base contendo a variável alvo para o treinamento
├── test.csv                              # Dataset de avaliação/teste
└── submission.csv                        # Arquivo preditivo final
```

---

## 🛠️ Tecnologias e Dependências

### Python:
* `pandas` / `numpy`: Manipulação vetorial e estruturação do banco de dados.
* `scikit-learn`: Funções de pré-processamento, *scaling*, métricas e algoritmos (Logistic Regression, Random Forest).
* `xgboost`: Biblioteca dedicada à modelagem de Gradient Boosting.
* `plotly` / `matplotlib`: Motores gráficos para as visualizações estáticas e interativas.
* `wordcloud`: Geração analítica baseada nas frequências de sobrenomes a bordo.