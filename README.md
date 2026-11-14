# EcoScan

Projeto acadêmico de Mineração de Dados para classificação de resíduos por imagem.

## Bases

- **RealWaste** (principal): imagens reais de nove tipos de resíduos. Neste projeto são usadas as seis classes compatíveis.
- **TrashNet** (complementar): imagens controladas em fundo claro.

Classes comuns: `papel`, `papelao`, `vidro`, `metal`, `plastico` e `rejeito`.

Os arquivos brutos não são enviados ao GitHub. Consulte `data/README.md` para obter as bases.

## Execução

```powershell
python -m pip install -r requirements.txt
python run_pipeline.py
```

O pipeline:

1. extrai os arquivos ZIP;
2. valida e cataloga as imagens;
3. gera a análise exploratória;
4. extrai características HOG e histogramas de cor;
5. compara Regressão Logística, Random Forest e SVM;
6. avalia a generalização de TrashNet para RealWaste;
7. salva o melhor modelo em `models/best_model.joblib`.

## API opcional

```powershell
uvicorn api.main:app --reload
```

Abra `http://127.0.0.1:8000/docs` e envie uma imagem no endpoint `/predict`.

## Saídas

- `data/processed/manifest.csv`: catálogo das imagens válidas;
- `reports/figures/`: gráficos e matrizes de confusão;
- `reports/tables/`: métricas e relatórios;
- `models/best_model.joblib`: modelo final;
- `article/`: artigo acadêmico e versão PDF.

