# Resultados do EcoScan

Foram validadas 6.114 imagens, sendo 2.527 da TrashNet e 3.587 da RealWaste, distribuídas entre metal, papel, papelão, plástico, rejeito e vidro.

## Comparação dos modelos

| Modelo | Acurácia | Precisão macro | Recall macro | F1 macro |
|---|---:|---:|---:|---:|
| SVM RBF | 66,88% | 67,38% | 64,58% | 65,06% |
| Random Forest | 66,56% | 70,34% | 63,51% | 64,08% |
| Regressão Logística | 51,84% | 50,57% | 50,27% | 50,30% |

A SVM RBF foi escolhida pelo maior F1 macro. O rejeito foi a classe mais difícil: precisão de 69,70%, recall de 36,51% e F1 de 47,92%.

## Principal conclusão

Treinada apenas na TrashNet, a SVM obteve F1 macro de 67,49% no teste interno, mas somente 17,21% nas imagens reais da RealWaste. Isso confirma que um bom resultado em fotografias controladas não garante generalização para o ambiente real. A diversidade e a representatividade das imagens de treinamento são decisivas.

## Reprodutibilidade

Execute `python run_pipeline.py` na raiz do projeto para refazer o processamento, os gráficos, o treinamento e a avaliação. As bases brutas não são versionadas por causa do tamanho; as fontes e instruções estão em `data/README.md`.
