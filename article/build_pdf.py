from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "EcoScan_Artigo_Final.pdf"
GREEN = colors.HexColor("#1B5E20")
BLUE = colors.HexColor("#0D47A1")
LIGHT_GREEN = colors.HexColor("#E8F5E9")
LIGHT_BLUE = colors.HexColor("#E3F2FD")
GRAY = colors.HexColor("#616161")


def register_fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("EcoArial", str(regular)))
        pdfmetrics.registerFont(TTFont("EcoArialBold", str(bold)))
        return "EcoArial", "EcoArialBold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


class ArticleDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=2.3 * cm,
            rightMargin=2.3 * cm,
            topMargin=2.2 * cm,
            bottomMargin=2.1 * cm,
            title="EcoScan - Classificacao de residuos por imagem",
            author="Leonardo Bonatto Fernandes; Gustavo Toledo Denig",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="article",
        )
        self.addPageTemplates(PageTemplate(id="normal", frames=frame, onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setFont(FONT, 8.5)
            canvas.setFillColor(GRAY)
            canvas.drawCentredString(A4[0] / 2, 1.15 * cm, str(doc.page))
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=19,
            leading=24,
            alignment=TA_CENTER,
            textColor=GREEN,
            spaceAfter=18,
        ),
        "authors": ParagraphStyle(
            "Authors",
            parent=base["Normal"],
            fontName=FONT,
            fontSize=11,
            leading=17,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=14,
            leading=17,
            textColor=GREEN,
            spaceBefore=14,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=11.5,
            leading=14,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=9.5,
            leading=13.3,
            alignment=TA_JUSTIFY,
            firstLineIndent=1.0 * cm,
            spaceAfter=5,
        ),
        "body_no_indent": ParagraphStyle(
            "BodyNoIndent",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=9.5,
            leading=13.3,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=9,
            leading=12.5,
            alignment=TA_JUSTIFY,
            leftIndent=0.6 * cm,
            rightIndent=0.6 * cm,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName=FONT,
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=GRAY,
            spaceBefore=3,
            spaceAfter=8,
        ),
        "reference": ParagraphStyle(
            "Reference",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=8.5,
            leading=11.5,
            alignment=TA_LEFT,
            leftIndent=0.8 * cm,
            firstLineIndent=-0.8 * cm,
            spaceAfter=5,
        ),
    }


S = styles()


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def H1(text: str) -> Paragraph:
    return Paragraph(text, S["h1"])


def H2(text: str) -> Paragraph:
    return Paragraph(text, S["h2"])


def figure(filename: str, caption: str, width: float = 15.2 * cm):
    path = ROOT / "images" / filename
    image = Image(str(path))
    ratio = image.imageHeight / image.imageWidth
    image.drawWidth = width
    image.drawHeight = width * ratio
    return KeepTogether([image, P(caption, "caption")])


def styled_table(data, widths, header_fill=LIGHT_GREEN):
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_fill),
                ("TEXTCOLOR", (0, 0), (-1, 0), GREEN),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 8.3),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BDBDBD")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_story():
    story = []
    story += [Spacer(1, 2.1 * cm), P("EcoScan", "title")]
    story += [
        Paragraph(
            "Classificação de resíduos por imagem com Mineração de Dados",
            ParagraphStyle(
                "Subtitle", parent=S["authors"], fontName=FONT_BOLD, fontSize=14,
                leading=18, textColor=BLUE, spaceAfter=35
            ),
        )
    ]
    story += [
        P(
            "Leonardo Bonatto Fernandes<br/>Gustavo Toledo Denig",
            "authors",
        ),
        Spacer(1, 2.0 * cm),
        P("Novembro de 2026", "authors"),
        PageBreak(),
    ]

    story += [H1("Resumo")]
    story += [
        P(
            "A separação incorreta de resíduos reduz o aproveitamento de materiais recicláveis e aumenta o esforço necessário para a triagem. Este trabalho apresenta o EcoScan, um projeto de Mineração de Dados voltado à classificação de resíduos em seis categorias: metal, papel, papelão, plástico, rejeito e vidro. Foram integradas as bases públicas TrashNet e RealWaste, totalizando 6.114 imagens válidas. O processo foi organizado segundo o CRISP-DM e incluiu validação dos arquivos, padronização de rótulos, análise exploratória, tratamento do desbalanceamento, transformação das imagens em atributos numéricos e comparação de três modelos do Scikit-Learn. As características foram representadas por HOG e histogramas de cor HSV. A SVM com kernel RBF apresentou o melhor resultado, com acurácia de 66,88% e F1 macro de 65,06%. Um experimento adicional mostrou que o F1 macro caiu de 67,49% em imagens controladas da TrashNet para 17,21% em imagens reais da RealWaste. O resultado evidencia que a representatividade dos dados é determinante para a aplicação prática. O protótipo inclui uma API em FastAPI para consulta do modelo.",
            "abstract",
        ),
        P("<b>Palavras-chave:</b> mineração de dados; classificação de imagens; resíduos recicláveis; aprendizado de máquina; CRISP-DM.", "abstract"),
    ]

    story += [H1("1 Introdução")]
    story += [
        P("A separação de resíduos é uma etapa importante para a reciclagem, pois materiais descartados na categoria errada podem ser contaminados e perder seu potencial de reaproveitamento. Em empresas, condomínios, instituições de ensino e centrais de triagem, a identificação do material depende frequentemente de avaliação humana. Esse processo pode ser repetitivo e sujeito a divergências, sobretudo quando os objetos estão deformados, sujos ou misturados."),
        P("O EcoScan foi proposto como uma ferramenta de apoio à classificação inicial de resíduos por imagem. A pergunta principal é: <i>um modelo treinado com imagens de resíduos em ambiente controlado mantém seu desempenho quando aplicado a imagens capturadas em condições reais?</i> A pergunta incorpora uma preocupação central do projeto: um resultado satisfatório em uma base organizada não garante funcionamento no ambiente de uso."),
        P("O objetivo geral foi desenvolver e avaliar um fluxo completo de Mineração de Dados capaz de classificar imagens de resíduos. Os objetivos específicos foram integrar duas bases públicas, analisar a qualidade e o balanceamento dos dados, transformar imagens em variáveis numéricas, comparar modelos do Scikit-Learn, avaliar a mudança de domínio entre imagens controladas e reais e disponibilizar o melhor modelo por uma API experimental."),
        P("Foram consideradas quatro hipóteses: um modelo supervisionado alcança desempenho superior a uma classificação aleatória; classes visualmente próximas apresentam mais confusões; quantidade e diversidade de imagens influenciam o desempenho; e um modelo treinado apenas em imagens controladas perde desempenho quando aplicado a imagens reais."),
    ]

    story += [H1("2 Fundamentação teórica"), H2("2.1 Mineração de Dados e CRISP-DM")]
    story += [P("Mineração de Dados é o processo de identificação de padrões úteis em conjuntos de dados por técnicas estatísticas e computacionais. Neste trabalho foi adotado o CRISP-DM, que organiza o projeto em compreensão do negócio, compreensão dos dados, preparação, modelagem, avaliação e implantação. A metodologia foi escolhida por permitir revisar decisões conforme novos resultados são encontrados.")]
    story += [H2("2.2 Representação das imagens")]
    story += [P("Modelos tradicionais não recebem diretamente o significado visual de uma fotografia. Cada imagem foi, portanto, convertida em um vetor de atributos. O HOG descreve bordas e formas pela distribuição das orientações dos gradientes. Para complementar a textura, foram calculados histogramas dos canais de matiz, saturação e brilho no espaço HSV. A combinação representa forma e cor sem utilizar uma rede neural profunda.")]
    story += [H2("2.3 Modelos avaliados")]
    story += [P("Foram avaliados Regressão Logística, Random Forest e máquina de vetores de suporte com kernel RBF. A Regressão Logística funciona como referência linear; o Random Forest representa relações não lineares por um conjunto de árvores; e a SVM RBF permite construir fronteiras não lineares em espaços de muitas dimensões.")]

    story += [H1("3 Metodologia"), H2("3.1 Compreensão do problema")]
    story += [P("O problema de negócio consiste em apoiar a triagem inicial e produzir informações úteis para ações de conscientização e gestão. O modelo não substitui a análise humana em situações ambíguas. Sua função é oferecer uma sugestão de classe e uma pontuação de confiança para apoiar a decisão.")]
    story += [H2("3.2 Bases de dados")]
    story += [
        P("A RealWaste foi adotada como base principal por conter imagens coletadas em um ambiente real de aterro, no Whyte's Gully Waste and Resource Recovery Centre, em Wollongong, Austrália. Das 4.752 imagens originais, foram utilizadas 3.587 pertencentes às seis classes compatíveis."),
        P("A TrashNet foi utilizada como base complementar. Ela contém 2.527 imagens fotografadas predominantemente sobre fundo branco. As categorias das duas fontes foram padronizadas para metal, papel, papelão, plástico, rejeito e vidro."),
    ]
    class_data = [
        ["Classe", "TrashNet", "RealWaste", "Total"],
        ["Metal", "410", "790", "1.200"], ["Papel", "594", "500", "1.094"],
        ["Papelão", "403", "461", "864"], ["Plástico", "482", "921", "1.403"],
        ["Rejeito", "137", "495", "632"], ["Vidro", "501", "420", "921"],
        ["Total", "2.527", "3.587", "6.114"],
    ]
    story += [styled_table(class_data, [4.2 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm]), P("Tabela 1 - Quantidade de imagens por classe e por fonte.", "caption")]
    story += [figure("01_distribuicao_classes.png", "Figura 1 - Distribuição das classes nas bases TrashNet e RealWaste.", 14.5 * cm)]

    story += [H2("3.3 Limpeza, filtragem e transformação")]
    story += [
        P("O processamento foi realizado em Python com NumPy e Pandas. Os arquivos compactados foram extraídos e todas as imagens aceitas foram catalogadas. Cada arquivo foi aberto com Pillow para verificar integridade, dimensões e modo de cor. Não foram encontrados arquivos corrompidos nas seis classes selecionadas, de modo que as 6.114 imagens foram mantidas."),
        P("Os rótulos foram padronizados em português. As classes exclusivas da RealWaste, como resíduos orgânicos, vegetação e tecidos, foram filtradas. As imagens foram convertidas para RGB, corrigidas conforme a orientação EXIF, redimensionadas para 64 por 64 pixels e normalizadas para o intervalo de zero a um."),
        P("Para cada imagem foram extraídos 1.812 atributos: descritores HOG de textura e 16 intervalos de histograma para cada canal HSV. O manifesto final foi salvo em CSV e a matriz de características foi armazenada com Joblib para permitir a reprodução dos experimentos."),
    ]

    story += [H2("3.4 Análise exploratória e desbalanceamento")]
    story += [P("Os gráficos foram produzidos com Matplotlib e Seaborn. A TrashNet apresenta objetos isolados e fundos mais uniformes; a RealWaste contém sujeira, deformações, sobreposição e fundos complexos.")]
    story += [figure("04_amostras_bases.png", "Figura 2 - Exemplos das seis classes em cada base.", 16.0 * cm)]
    story += [P("O conjunto combinado é desbalanceado. Plástico possui 1.403 imagens, enquanto rejeito possui 632. Não foi utilizada duplicação simples, pois ela poderia aumentar o sobreajuste. O tratamento ocorreu por pesos de classe inversamente relacionados à frequência e por divisão estratificada, preservando as proporções no treino e no teste.")]
    story += [figure("02_balanceamento_percentual.png", "Figura 3 - Participação percentual das classes no conjunto combinado.", 14.0 * cm)]

    story += [H2("3.5 Treinamento e avaliação")]
    story += [
        P("O conjunto combinado foi dividido de forma estratificada em 80% para treinamento e 20% para teste, com semente aleatória 42. Foram utilizadas 4.891 imagens no treino e 1.223 no teste. A padronização dos atributos foi aplicada à Regressão Logística e à SVM dentro de um Pipeline, evitando vazamento de informações."),
        P("A Regressão Logística utilizou C igual a 1 e balanceamento de classes. O Random Forest foi treinado com 300 árvores, mínimo de duas amostras por folha e pesos balanceados por subamostra. A SVM utilizou kernel RBF, C igual a 5, pesos balanceados e gamma definido em função da variância."),
        P("Foram avaliadas acurácia, precisão macro, recall macro e F1 macro. A média macro atribui a mesma importância a todas as classes. Também foi realizado um experimento de mudança de domínio: o melhor algoritmo foi treinado somente com 80% da TrashNet e testado no restante da TrashNet e em todas as 3.587 imagens compatíveis da RealWaste."),
    ]

    story += [H1("4 Resultados"), H2("4.1 Comparação dos modelos")]
    story += [P("A SVM RBF obteve o maior F1 macro, 65,06%, seguida pelo Random Forest, com 64,08%. O Random Forest apresentou a maior precisão macro, 70,34%, e treinamento muito mais rápido. A SVM foi escolhida como modelo final porque o F1 macro foi definido como critério principal.")]
    model_data = [
        ["Modelo", "Acurácia", "Precisão", "Recall", "F1 macro", "Tempo"],
        ["SVM RBF", "66,88%", "67,38%", "64,58%", "65,06%", "112,99 s"],
        ["Random Forest", "66,56%", "70,34%", "63,51%", "64,08%", "5,25 s"],
        ["Regressão Logística", "51,84%", "50,57%", "50,27%", "50,30%", "1,98 s"],
    ]
    story += [styled_table(model_data, [4.0 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm], LIGHT_BLUE), P("Tabela 2 - Desempenho dos modelos no conjunto de teste.", "caption")]
    story += [figure("05_comparacao_modelos.png", "Figura 4 - Comparação entre as métricas dos modelos.", 14.6 * cm)]

    story += [H2("4.2 Resultados por classe")]
    story += [P("Papel, papelão, plástico e metal apresentaram F1 próximo ou superior a 68%. Rejeito teve precisão de 69,70%, mas recall de 36,51%, indicando que o modelo deixou de reconhecer grande parte dos rejeitos reais.")]
    per_class = [
        ["Classe", "Precisão", "Recall", "F1", "Amostras"],
        ["Metal", "67,35%", "68,75%", "68,04%", "240"],
        ["Papel", "68,28%", "70,78%", "69,51%", "219"],
        ["Papelão", "67,96%", "71,10%", "69,49%", "173"],
        ["Plástico", "64,67%", "72,95%", "68,56%", "281"],
        ["Rejeito", "69,70%", "36,51%", "47,92%", "126"],
        ["Vidro", "66,31%", "67,39%", "66,85%", "184"],
    ]
    story += [styled_table(per_class, [3.7 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm]), P("Tabela 3 - Métricas por classe da SVM RBF.", "caption")]
    story += [P("Os principais erros envolveram plástico confundido com metal ou vidro, papel confundido com papelão e rejeito confundido com plástico ou metal. Isso é coerente com as semelhanças entre embalagens transparentes, superfícies metálicas e materiais deformados.")]
    story += [figure("matriz_confusao_svm_rbf.png", "Figura 5 - Matriz de confusão da SVM RBF.", 12.6 * cm)]

    story += [H2("4.3 Generalização entre bases")]
    story += [P("O experimento de mudança de domínio apresentou a evidência mais relevante. Treinada somente na TrashNet, a SVM atingiu acurácia de 68,77% e F1 macro de 67,49% no teste interno. Aplicada à RealWaste, a acurácia caiu para 24,62% e o F1 macro para 17,21%.")]
    domain_data = [
        ["Cenário", "Acurácia", "Precisão", "Recall", "F1 macro"],
        ["Teste interno TrashNet", "68,77%", "71,62%", "65,69%", "67,49%"],
        ["Teste externo RealWaste", "24,62%", "18,97%", "19,51%", "17,21%"],
    ]
    story += [styled_table(domain_data, [5.4 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm], LIGHT_BLUE), P("Tabela 4 - Desempenho do modelo treinado somente na TrashNet.", "caption")]
    story += [figure("06_mudanca_dominio.png", "Figura 6 - Queda de desempenho de imagens controladas para imagens reais.", 12.2 * cm)]
    story += [P("A hipótese de perda de desempenho fora do ambiente controlado foi confirmada. O modelo aprendeu características específicas da TrashNet, como fundo claro, iluminação e enquadramento. O treinamento combinado elevou o F1 macro geral para 65,06%, reforçando a necessidade de amostras representativas do ambiente de aplicação.")]

    story += [H1("5 Implantação experimental e valor gerado")]
    story += [
        P("O melhor modelo foi salvo em Joblib e integrado a uma API em FastAPI. O endpoint recebe uma imagem, aplica o mesmo pré-processamento do treino e devolve a classe prevista, o modelo utilizado e uma confiança aproximada calculada a partir das pontuações da SVM. A API é um protótipo de apoio e não um sistema de decisão automática."),
        P("Em uma aplicação futura, registros da API poderão apoiar o acompanhamento de erros e a seleção de novas imagens para retreinamento. Para uma organização, essas informações podem orientar campanhas de descarte, capacitação de equipes e ajustes nos coletores. Essas decisões exigem dados reais de uso; a quantidade de imagens de um dataset não representa a frequência de resíduos de uma empresa ou cidade."),
        P("O código, as instruções e os resultados estão no repositório https://github.com/leobonatto/Planterra2.0, na pasta EcoScan. Os arquivos brutos não são versionados devido ao tamanho; os endereços oficiais e o procedimento de obtenção estão documentados no projeto."),
    ]

    story += [PageBreak(), H1("6 Limitações e trabalhos futuros")]
    story += [
        P("HOG e histogramas de cor são adequados para comparar modelos tradicionais, mas não capturam toda a complexidade visual. Redes neurais convolucionais e transferência de aprendizado podem melhorar os resultados em trabalhos futuros."),
        P("A RealWaste foi coletada em uma instalação australiana e pode não representar resíduos e condições do Brasil. Cada imagem possui um único rótulo, mesmo quando há materiais misturados. Não existem informações de peso, volume, data, custo ou destino final."),
        P("O experimento utilizou uma divisão estratificada fixa. Uma avaliação futura deve empregar validação cruzada, ajuste sistemático de hiperparâmetros e um conjunto externo brasileiro. Também são necessários testes com usuários para verificar a redução do tempo de triagem."),
    ]

    story += [H1("7 Conclusão")]
    story += [
        P("O projeto aplicou o ciclo completo de Mineração de Dados a 6.114 imagens das bases TrashNet e RealWaste. O fluxo incluiu compreensão do problema, validação e padronização, análise exploratória, transformação das imagens, tratamento do desbalanceamento, comparação de modelos, avaliação e implantação experimental."),
        P("A SVM RBF apresentou o melhor F1 macro, com 65,06%, enquanto o Random Forest obteve resultado próximo com custo muito menor. Rejeito foi a classe mais difícil, principalmente pelo baixo recall. A avaliação externa confirmou que um modelo treinado em fotografias controladas não se transfere automaticamente para imagens reais: o F1 macro caiu de 67,49% para 17,21%."),
        P("Os resultados confirmam que a qualidade depende não apenas da quantidade, mas da semelhança entre o treinamento e o ambiente real. O EcoScan é viável como ferramenta de apoio, desde que receba imagens representativas, seja monitorado por classe e mantenha supervisão humana nas previsões incertas."),
    ]

    story += [H1("Referências")]
    references = [
        "WIRTH, R.; HIPP, J. CRISP-DM: Towards a standard process model for data mining. Proceedings of the 4th International Conference on the Practical Applications of Knowledge Discovery and Data Mining, 2000.",
        "SINGLE, S.; IRANMANESH, S.; RAAD, R. RealWaste: A novel real-life data set for landfill waste classification using deep learning. Information, v. 14, n. 12, p. 633, 2023. DOI: https://doi.org/10.3390/info14120633.",
        "THUNG, G.; YANG, M. TrashNet: Dataset of images of trash. 2016. Disponível em: https://github.com/garythung/trashnet. Acesso em: 13 nov. 2026.",
        "DALAL, N.; TRIGGS, B. Histograms of oriented gradients for human detection. IEEE CVPR, 2005. DOI: https://doi.org/10.1109/CVPR.2005.177.",
        "PEDREGOSA, F. et al. Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, v. 12, p. 2825-2830, 2011.",
        "HARRIS, C. R. et al. Array programming with NumPy. Nature, v. 585, p. 357-362, 2020. DOI: https://doi.org/10.1038/s41586-020-2649-2.",
        "MCKINNEY, W. Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference, 2010.",
        "HUNTER, J. D. Matplotlib: A 2D graphics environment. Computing in Science and Engineering, v. 9, n. 3, p. 90-95, 2007.",
        "WASKOM, M. L. Seaborn: Statistical data visualization. Journal of Open Source Software, v. 6, n. 60, p. 3021, 2021.",
    ]
    story += [Paragraph(ref, S["reference"]) for ref in references]
    return story


def main():
    document = ArticleDocTemplate(str(OUTPUT))
    document.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
