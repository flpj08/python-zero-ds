# House Rocket
A House Rocket é uma empresa fictícia, que possui como modelo de negócio a compra e a venda de imóveis usando tecnologia.
Este projeto segue as recomendações do blog [Seja um Data Scientist](https://sejaumdatascientist.com/os-5-projetos-de-data-science-que-fara-o-recrutador-olhar-para-voce/)

---
## 1. Business Problem
A House Rocket está querendo maximizar seus lucros, encontrando as melhores oportunidades de compra e venda de imóveis, utilizando dados.

Desta forma, o Cientista de Dados deverá criar um dashboard online para que o CEO da empresa visualize algumas informações do dataset disponibilizado, bem como possa verificar as sugestões de compra e venda indicada pela análise dos dados.


## 2. Business Assumption
- Os dados são de 05/2014 até 05/2015.
- A definição para cada um dos atributos encontra-se abaixo:

|    Atributos    |                         Significado                          |
| :-------------: | :----------------------------------------------------------: |
|       id        |       Numeração única de identificação do imóvel             |
|      date       |                    Data da venda do imóvel                   |
|      price      |    Preço que o imóvel está sendo vendido pelo proprietário   |
|    bedrooms     |                      Número de quartos                       |
|    bathrooms    | Número de banheiros (0.5 = banheiro em um quarto, mas sem chuveiro) |
|   sqft_living   | Medida (em pés quadrado) do espaço interior dos imóveis      |
|    sqft_lot     |     Medida (em pés quadrados) quadrada do espaço terrestre   |
|     floors      |                 Número de andares do imóvel                  |
|   waterfront    | Variável que indica a presença ou não de vista para água (0 = não e 1 = sim) |
|      view       | Um índice de 0 a 4 que indica a qualidade da vista da propriedade. Varia de 0 a 4, onde: 0 = baixa  4 = alta |
|    condition    | Um índice de 1 a 5 que indica a condição do imóvel. Varia de 1 a 5, onde: 1 = baixo \|-\| 5 = alta |
|      grade      | Um índice de 1 a 13 que indica a construção e o design do edifício. Varia de 1 a 13, onde: 1-3 = baixo, 7 = médio e 11-13 = alta |
|   sqft_above    | A metragem quadrada do espaço habitacional interior acima do nivel do solo  |
|  sqft_basement  | A metragem quadrada do espaço habitacional interior abaixo do nível do solo |
|    yr_built     |               Ano de construção de cada imóvel               |
|  yr_renovated   |                Ano de reforma de cada imóvel                 |
|     zipcode     |                         CEP do imóvel                        |
|       lat       |                           Latitude                           |
|      long       |                          Longitude                           |
| sqft_livining15 | Medida (em pés quadrado) do espaço interno de habitação para os 15 vizinhos mais próximo |
|   sqft_lot15    | Medida (em pés quadrado) dos lotes de terra dos 15 vizinhos mais próximo |
- Condição do imóvel >=3, é considerada BOA.


## 3. Solution Strategy
1. **Entendimento do negócio:** Através post no blog do Seja um Data Scientist, mencionado anteriormente, é possível ter um entendimento do negócio em que a House Rocket está inserida.

2. **Entendimento do problema de negócio:** Questões para responder: <br>
 **- Quais imóveis a House Rocket deveria comprar e por qual preço de compra?** <br>
 **- Uma vez os imóveis em posse da empresa, qual o melhor momento para vendê-los e qual seria o preço da venda?**

3. **Coleta de dados:** <br>
*- Dataset House Rocket*<br>
Para obter o dataset de imóveis da House Rocket foi acessado o site Kaggle, em https://www.kaggle.com/harlfoxem/housesalesprediction, e realizado download do dataset no formato '.csv'.<br>
*- GeoFile: Zipcodes* <br>
Em tempo de execução é realizado um acesso na url abaixo para realização do download de um arquivo geojson, que tráz coordenadas para o desenho das áreas no mapa disponibilizado na seção de Overview por Região.<br>
https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson

4. **Preparação dos dados:** Apenas preparações simples foram realizadas, como a conversão do tipo de dado e cálculo de preço por pé quadrado, para utilização posterior.

5. **Exploração de dados através das hipóteses levantadas:** Nessa etapa, algumas hipóteses foram levantadas, as quais podem ser encontradas na seção de "Validação de Hipóteses".

6. **Montagem de uma tabela no formato '.csv' indicando quais os imóveis que a House Rocket deveria comprar e por qual preço.**<br>
 Os imóveis serão considerados 'bons para comprar' se respeitarem as seguintes regras:<br>
 *1- O preço do imóvel precisava estar abaixo do valor da mediana da região*<br>
 *2- A condição do imóvel precisava estar boa, ou seja, maior ou igual a 3.*<br>
 Com isso, será criada uma tabela chamada purchase_table, no formato '.csv', contendo as seguintes informações: id, zipcode, price, median_price, condition, buy.

7. **Montagem de uma tabela no formato '.csv' indicando quais imóveis comprar, em que momento e por quanto vender.**<br>
 - Os imóveis serão agrupados por região (zipcode) e por sazonalidade.
 - Dentro de cada região e sazonalidade, eu vou calcular a mediana de preço.
 - Condições de venda:<br>
  *Se o preço da compra for maior que a mediana da região+sazonalidade. O preço da venda será igual ao peço da compra + 10%*<br>
  *Se o preço da compra for menor que a mediana da região+sazonalidade. O preço da venda será igual ao peço da compra + 30%*

8. **Construção do Dashboard online para apresentação dos dados:** Será criado um dashboard utilizando a biblioteca Streamlit e este estará disponível através da ferramenta Heroku. Dessa forma o dashboard estará disponível para acesso online.

## 4. Business Results
Ao final da análise, foram criadas duas tabelas, apresentadas na seção Recomendações.
A primeira, 'purchase_table.csv', mostra os imóveis considerados bons para compra, e o preço de compra.
A segunda, 'sales_table.csv', sugere 10 imóveis para que a House Rocket compre e revenda com o preço sugerido, na estação de ano considerada a melhor para obter o maior lucro na transação.

Executando o que é sugerido pela segunda tabela, chega-se nos resultados abaixo:
|        |                         Valor USD                          |
| :-------------: | :----------------------------------------------------------: |
|       Investimento Inicial        |         17,275,750.00           |
|      Lucro Estimado       |                 5,182,725.00                 |

## 5. Conclusion
O objetivo desse projeto foi alcançado, visto que um dashboard online foi disponibilizado para a House Rocket, utilizando a plataforma Heroku.

Nesse dashboard será possível observar validações de hipóteses levantadas, bem como o acesso às tabelas  montadas conforme proposto neste projeto.

[<img alt="Heroku" src="https://img.shields.io/badge/heroku-%23430098.svg?style=for-the-badge&logo=heroku&logoColor=white"/>](https://househouse.herokuapp.com)

## 6. Next Steps to Improve
 - Melhorar a apresentação dos valores dos gráficos apresentados. Atualmente o usuário é obrigado a colocar o mouse por cima da barra no gráfico para ver o valor que aquela barra representa, por exemplo.
 - Melhorar a apresentação dos dados do imóvel nos mapas.
 - Adicionar um mapa na seção de recomendação, para que o CEO consiga visualizar a localização dos imóveis sugeridos para compra.
 - Sugestões dinâmicas: Ter a sujestão de compra e venda de imóveis, considerando a estação do ano atual.
 - Adicionar novas características do imóvel para considerar uma sugestão de compra + reforma afim de revender depois e identificação do novo preço.