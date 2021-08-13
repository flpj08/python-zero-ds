from re import template
import pandas           as pd
import streamlit        as st
import plotly.express   as px
import numpy            as np
import folium
import geopandas

from folium.plugins         import MarkerCluster
from streamlit_folium       import folium_static
from datetime               import datetime

# Layout Configuration
st.set_page_config(layout='wide')
pd.options.display.float_format = '{:.2f}'.format

@st.cache(allow_output_mutation = True)
def get_data(path):
    data = pd.read_csv(path)

    return data

@st.cache( allow_output_mutation= True )
def get_geofile(url):
    geofile = geopandas.read_file( url )

    return geofile

def transform_data(data):
    data['date'] = pd.to_datetime(data['date'])
    data['price_by_sqft'] = data['price'] / data['sqft_lot']

    return data

def navigation_sidebar():
    st.sidebar.title('House Rocket')
    rad = st.sidebar.radio('Escolha o que você quer ver...', ['Overview', 'Distrubuição Comercial', 'Overview por Região', 'Recomendações', 'Validação de Hipóteses'])

    return rad

def data_overview(data):
    st.title('Overview dos Dados')
    st.write('Nesta seção você vai poder observar informações resumidas do dataset, podendo filtrá-las por zipcode.')
    #Filtering by zipcode
    f_zipcode = st.multiselect('Selecione o(s) zipcode(s):', data['zipcode'].unique())

    if (f_zipcode != []):
        data_f = data.loc[ data['zipcode'].isin(f_zipcode), : ]
    else:
        data_f = data.copy()

    #-------------------------------
    # Statistic Descriptive
    #-------------------------------
    #Type selection
    num_attributes = data_f.select_dtypes( include=['int64', 'float64'] )
    
    #Central metrics
    media = pd.DataFrame( num_attributes.apply(np.mean))
    mediana = pd.DataFrame( num_attributes.apply(np.median))
    
    #Tendency
    std = pd.DataFrame( num_attributes.apply(np.std))
    max_ = pd.DataFrame( num_attributes.apply( np.max ))
    min_ = pd.DataFrame( num_attributes.apply( np.min ))

    #Data Concat
    df1 = pd.concat([max_, min_, media, mediana, std], axis=1).reset_index()
    df1.columns = ['attributes', 'max', 'min', 'mean', 'median', 'sdt']

    st.header('Análise Descritiva')
    st.dataframe(df1, height=700)


    #-------------------------------
    # Metrics by zipcode
    #-------------------------------
    df1 = data_f[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df2 = data_f[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df3 = data_f[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = data_f[['price_by_sqft', 'zipcode']].groupby('zipcode').mean().reset_index()

    #merge
    m1 = pd.merge(df1, df2, on='zipcode', how='inner')
    m2 = pd.merge(m1, df3, on='zipcode', how='inner')
    df_z = pd.merge(m2, df4, on='zipcode', how='inner')

    df_z.columns = ['ZIPCODE', 'TOTAL HOUSES', 'AVG PRICE', 'AVG SQFT LIVING', 'AVG PRICE/SQFT']
    
    st.header('Valores por Zipcode')
    st.dataframe(df_z, height=558)

    return None

def commercial_distribution( data ):
    st.title('Atributos Comerciais')
    #------ Average Price per Year
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

    #filters
    min_year_built = int( data['yr_built'].min() )
    max_year_built = int( data['yr_built'].max() )
    st.subheader( 'Selecionar Máx. de \'Year Built\'')
    f_year_built = st.slider('Year Built', min_year_built, max_year_built, max_year_built)

    #data selection
    df = data.loc[data['yr_built'] < f_year_built]
    df= df[['yr_built','price']].groupby('yr_built').mean().reset_index()

    #plot
    fig = px.line( df, x='yr_built', y='price' )
    st.plotly_chart( fig, use_container_width=True )

    #------ Average Price per Day
    st.header('Média de Preço por Dia')
    st.subheader('Selecionar Máx de \'Date\' ')

    #filters
    min_date = datetime.strptime( data['date'].min(), '%Y-%m-%d' )
    max_date = datetime.strptime( data['date'].max(), '%Y-%m-%d' )

    f_date = st.slider('Date', min_date, max_date, max_date)

    #data filtering
    data['date'] = pd.to_datetime( data['date'] )
    df = data.loc[data['date'] < f_date]
    df= df[['date','price']].groupby('date').mean().reset_index()

    #plot
    fig = px.line( df, x='date', y='price' )
    st.plotly_chart( fig, use_container_width=True )

    #------ Histograma
    st.header('Distribuição de Preço')
    st.subheader('Selecionar Máx de \'Price\'')

    #filter
    min_price= int( data['price'].min())
    max_price= int( data['price'].max())
    avg_price= int( data['price'].mean())

    #data filtering
    f_price = st.slider('Price', min_price, max_price, avg_price)
    df = data.loc[data['price']< f_price]

    #data plot
    fig = px.histogram( df, x='price', nbins=50 )
    st.plotly_chart( fig, use_container_width=True )

    return None

def region_overview( data, geofile ):
    st.title('Overview por Região')
    st.write('Nesta seção você verá como o dataset está distribuído geograficamente. Além disso, poderá observar a densidade de preço por região.')

    c1, c2 = st.beta_columns( (1,1) )

    df = data.copy()
    #-------------------------------
    #Portifolio Density
    #-------------------------------
    density_map = folium.Map( location=[data['lat'].mean(), data['long'].mean()],
                            default_zoom_start = 10 )

    marker_cluster = MarkerCluster().add_to( density_map )
    for name, row in df.iterrows():
        folium.Marker( [ row['lat'], row['long'] ],
                    popup= 'Sold R${0} on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, Year built: {5}'.format(
                        row['price'],
                        row['date'],
                        row['sqft_living'],
                        row['bedrooms'],
                        row['bathrooms'],
                        row['yr_built']
                    )).add_to(marker_cluster)


    st.header('Portifolio Density')
    folium_static( density_map )


    #-------------------------------
    #Price Density
    #-------------------------------
    df= data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df.columns= ['ZIP', 'PRICE']

    geofile = geofile[geofile['ZIP'].isin( df['ZIP'].tolist() )]

    region_price_map = folium.Map( location=[data['lat'].mean(), data['long'].mean()],
                            default_zoom_start = 10 )

    region_price_map.choropleth(data = df,
                                geo_data = geofile,
                                columns= ['ZIP', 'PRICE'],
                                key_on= 'feature.properties.ZIP',
                                fill_color='YlOrRd',
                                fill_opacity = 0.7,
                                line_opacity = 0.2,
                                legend_name='AVG PRICE'
    )
    st.header('Price Density')
    folium_static(region_price_map)

    return None

def recommendations_area(data_purchase, data_sale):
    st.title('Recomendações para House Rocket')
    st.write('O modelo de negócio da House Rocket consiste em comprar e revender imóveis usando técnologia.')
    st.write('Afim de encontrar as melhores oportunidades de negócio, a House Rocket forneceu um dataset com imóveis vendidos de 05/2014 até 05/2015 e fez as seguintes perguntas.')

    #==================
    #Question 1 (Purchasing)
    #================== 
    st.subheader('1. Quais casas o CEO da House Rocket deveria comprar e por qual preço de compra?')
    st.write('Através do portifólio disponibilizado pela empresa, foi possível encontrar 10502 com potencial para compra.')
    st.write('Esses imóveis foram encontrados com base em duas condições: 1 - O preço do imóvel precisava estar abaixo do valor da mediana da região; 2. A condição do imóvel precisava estar boa, ou seja, maior ou igual a 3.')
    st.write('Tendo essas caracteríscas, o imóvel foi considerado como apropriado para compra. Segue abaixo a tabela com os imóveis selecionados.')

    st.dataframe(data_purchase)

    #==================
    #Question 2 (Selling)
    #================== 
    st.subheader('2. Uma vez que algumas casas tivessem em posse da empresa, qual o melhor momento para vendê-las e qual seria o preço da venda?')
    st.write("""Para responder essa questão, primeiramente foi calculada a mediana de preços para cada região nas quatro estações dentro do periodo de todo o dataset, desde 05/2014 até 05/2015. 
                Com isso, foi possível identificar qual estação do ano possuia a mediana de preços mais alta em cada região para determinar qual o melhor momento para vender um imóvel.
                """)
    st.write("""A mediana de preço mais alta de cada região foi também utilizada para o cálculo do preço de venda. 
                O qual, recebeu 30% a mais do valor de compra do imóvel quando o mesmo ficava abaixo do preço mediano da região na estação considerada como a melhor para a venda. 
                Nas situações em que o preço de compra do imóvel ficava abaixo do melhor preço mediano, o valor de venda recebia um acréscimo de 10%.
                 """)

    st.write('A tabela abaixo traz 10 imóveis, que se comprados, trariam o maior lucro para a empresa caso vendidos na estação de ano sugerida.')

    st.dataframe(data_sale)

    investment = data_sale['Purchase Price'].sum()
    profit = data_sale['Profit'].sum()

    st.write('Seguindo a sugestão acima, a empresa teria que fazer um investimento total de **${:,.2f}**, sendo que o lucro previsto seria de **${:,.2f}**.'.format(investment, profit))

    return None

def hypotheses_area(data):
    st.title('Validação de Hipóteses')
    st.write('Afim de realizar uma análise exploratória dos dados, foram colocadas algumas hipóteses para serem validadas.')
    st.write('Nesta seção, você poderá observar a validação de cada hipótese levantada.')

    #==================
    #Hypothesis 1
    #================== 
    c1, c2 = st.beta_columns(2)
    h1_data_diff = data[['waterfront', 'price']].copy()
    
    h1_data_diff = h1_data_diff[['waterfront', 'price']].groupby('waterfront').mean().reset_index()
    h1_data_diff.columns = ['waterfront', 'Mean Price']

    h1_data_diff['pct_change'] = h1_data_diff['Mean Price'].pct_change()*100
    
    h1_data_diff['Waterfront Desc'] = 'NA'
    h1_data_diff.loc[h1_data_diff['waterfront']==0, 'Waterfront Desc'] = 'No Waterfront'
    h1_data_diff.loc[h1_data_diff['waterfront']==1, 'Waterfront Desc'] = 'Waterfront'

    h1_data = h1_data_diff[['Waterfront Desc', 'Mean Price']]

    fig = px.bar(h1_data[['Waterfront Desc','Mean Price']], x='Waterfront Desc', y='Mean Price', color= 'Waterfront Desc')
    fig.update_layout(showlegend = False)

    c1.subheader('H1: Imóveis que possuem vista para água, são 30% mais caros, na média.')
    c1.write('**Resultado:** Imóveis com vista para água são, em média, {:.2f}% mais caros dos que os que não possuem esse atributo.'.format(
        h1_data_diff.loc[h1_data_diff['waterfront']==1, 'pct_change'].values[0]))
    c1.plotly_chart(fig, use_container_width = True)


    #==================
    #Hypothesis 2
    #==================    
    h2_data_diff = data[['price', 'yr_built']].copy()

    h2_data_diff['old_house'] = 'NA'
    #yr_built before 1955 is an Old House
    h2_data_diff.loc[h2_data_diff['yr_built']<1955, 'old_house'] = 'Old Houses'
    #yr_built after 1955 is a New House
    h2_data_diff.loc[h2_data_diff['yr_built']>=1955, 'old_house'] = 'New Houses'

    h2_data_diff = h2_data_diff[['old_house','price']].groupby('old_house').mean().reset_index()
    h2_data_diff.columns = ['House Type', 'Mean Price']
    
    h2_data_diff['pct_change'] = h2_data_diff['Mean Price'].pct_change()*100

    h2_data = h2_data_diff[['House Type', 'Mean Price']]

    fig = px.bar(h2_data, x='House Type', y='Mean Price', color='House Type')
    fig.update_layout(showlegend = False)

    c2.subheader('H2: Imóveis com data de construção menor que 1955, são 50% mais baratos, na média.')
    c2.write('**Resultado:** Imóveis antigos (construidos antes de 1955) são {:.2f}% mais baratos que imóveis considerados novos.'.format(
        -1*h2_data_diff.loc[h2_data_diff['House Type']== 'Old Houses', 'pct_change'].values[0]))
    c2.plotly_chart(fig, use_container_width = True) 


    #==================
    #Hypothesis 3
    #==================    
    c1, c2 = st.beta_columns(2)
    h3_data_diff = data[['sqft_basement', 'sqft_lot']].copy()
    
    h3_data_diff['Basement'] = 'NA'
    h3_data_diff.loc[h3_data_diff['sqft_basement']>0, 'Basement'] = 'With Basement'
    h3_data_diff.loc[h3_data_diff['sqft_basement']==0, 'Basement'] = 'No Basement'

    h3_data_diff = h3_data_diff[['Basement', 'sqft_lot']].groupby('Basement').mean().reset_index()
    h3_data_diff.columns = ['Basement', 'Mean Lot Size']

    h3_data_diff = h3_data_diff.sort_values(by=['Mean Lot Size'], ascending=True)
    
    h3_data_diff['pct_change'] = h3_data_diff['Mean Lot Size'].pct_change()*100
    
    h3_data = h3_data_diff[['Basement', 'Mean Lot Size']]

    fig = px.bar(h3_data, x='Basement', y='Mean Lot Size', color='Basement')
    fig.update_layout(showlegend = False)

    c1.subheader('H3: Imóveis sem porão possuem área total (sqrt_lot) 40% maiores do que os imóveis com porão.')
    c1.write('**Resultado:** A área total de imóveis com porão é {:.2f}% maior que os outros imóveis, que possuem este atributo.'.format(
        h3_data_diff.loc[h3_data_diff['Basement']== 'No Basement', 'pct_change'].values[0]))
    c1.plotly_chart(fig, use_container_width = True)


    #==================
    #Hypothesis 4
    #==================
    h4_data_diff = data[['date', 'price']].copy()
    h4_data_diff['date_year'] = h4_data_diff['date'].dt.year

    h4_data_diff = h4_data_diff[['date_year', 'price']].groupby('date_year').mean().reset_index()
    h4_data_diff.columns = ['Year', 'Mean Price']
    h4_data_diff['Year'] = h4_data_diff['Year'].astype('str')

    h4_data_diff['pct_change'] = h4_data_diff['Mean Price'].pct_change()*100

    h4_data = h4_data_diff[['Year', 'Mean Price']]
    fig = px.bar(h4_data, x='Year', y='Mean Price', color='Year')
    fig.update_layout(showlegend = False)

    c2.subheader('H4: O crescimento do preço dos imóveis YoY (Year over Year) é de 10%.')
    c2.write('**Resultado:** O preço médio dos imóveis cresceu {:.2f}% de 05/2014 à 05/2015.'.format(
        h4_data_diff.loc[h4_data_diff['Year']== '2015', 'pct_change'].values[0]))
    c2.plotly_chart(fig, use_container_width = True)


    #==================
    #Hypothesis 5
    #==================
    c1, c2 = st.beta_columns(2)
    h5_data_diff = data[['date', 'price', 'bathrooms']].copy()
    h5_data_diff['Month'] = h5_data_diff['date'].dt.strftime('%Y-%m')

    h5_data_diff = h5_data_diff[h5_data_diff['bathrooms']==3]

    h5_data_diff = h5_data_diff[['Month', 'price']].groupby('Month').mean().reset_index()
    h5_data_diff.columns = ['Month', 'Mean Price']

    h5_data_diff['pct_change'] = h5_data_diff['Mean Price'].pct_change()*100

    h5_data = h5_data_diff[['Month', 'pct_change']]
    fig= px.line(h5_data[['Month','pct_change']], x= 'Month', y= 'pct_change')

    c1.subheader('H5: Imóveis com 3 banheiros tem um crescimento de MoM (Month over Month) de 15%, em média.')
    c1.write('**Resultado:**O crescimento médio, mês a mês, de preços dos imóveis que possuem 3 banheiros é de {:.2f}%.'.format(
        h5_data_diff['pct_change'].mean()))
    c1.plotly_chart(fig, use_container_width= True)


    #==================
    #Hypothesis 6
    #==================
    h6_data_diff = data[['bedrooms', 'price']].copy()
    h6_data_diff = pd.concat(
                    [h6_data_diff[h6_data_diff['bedrooms']==2],
                     h6_data_diff[h6_data_diff['bedrooms']==3]],
                     ignore_index=True
                     ).reset_index()
    
    h6_data_diff = h6_data_diff[['bedrooms', 'price']].groupby('bedrooms').mean().reset_index()
    h6_data_diff.columns= ['Bedrooms', 'Mean Price']

    h6_data_diff['pct_change'] = h6_data_diff['Mean Price'].pct_change()*100

    h6_data = h6_data_diff[['Bedrooms', 'Mean Price']]
    h6_data['Bedrooms'] = h6_data['Bedrooms'].astype('str')

    fig = px.bar(h6_data, x= 'Bedrooms', y= 'Mean Price', color='Bedrooms')
    fig.update_layout(showlegend = False, )

    c2.subheader('H6: Imóveis com 3 quartos são 10% mais caros do que os que possuem 2 quartos.')
    c2.write('**Resultado:** Imóveis com 3 banheiros são {:.2f}% mais caros do que os que possuem 2 quartos.'.format(
        h6_data_diff.loc[h6_data_diff['Bedrooms']==3, 'pct_change'].values[0]))
    c2.plotly_chart(fig, use_container_width= True)
    

    #==================
    #Hypothesis 7
    #==================
    c1, c2 = st.beta_columns(2)
    h7_data_diff = data[['id', 'date', 'sqft_living']].copy()
    
    h7_data_diff = h7_data_diff[h7_data_diff['sqft_living'] > 0]
    
    h7_data_diff['Month'] = h7_data_diff['date'].dt.strftime('%Y-%m')

    h7_data_diff = h7_data_diff[['id', 'Month']].groupby('Month').count().reset_index()
    h7_data_diff = h7_data_diff.rename(columns={'id': 'Quantity'})

    h7_data_diff['pct_change'] = h7_data_diff['Quantity'].pct_change()*100

    h7_data = h7_data_diff[['Month', 'pct_change']]
    fig = px.line(h7_data, x= 'Month', y= 'pct_change')


    c1.subheader('H7: Imóveis com sqft_living maior que 1614sqft (150m2) tiveram um crescimento nas vendas de 20% nos últimos meses.')
    c1.write('**Resultado:** Analisando mês a mês, as vendas de imóveis com sqft_living maior que 150m2 tiveram uma média de {:.2f}% de queda.'.format(
        h7_data_diff['pct_change'].mean()))
    c1.plotly_chart(fig, use_container_width= True)


    #==================
    #Hypothesis 8
    #==================
    h8_data_diff = data[['id', 'date', 'bedrooms']].copy()
    
    h8_data_diff = h8_data_diff[h8_data_diff['bedrooms']==1]

    h8_data_diff['Month'] = h8_data_diff['date'].dt.strftime('%Y-%m')
    
    h8_data_diff = h8_data_diff[['id', 'Month']].groupby('Month').count().reset_index()
    h8_data_diff = h8_data_diff.rename(columns= {'id': 'Quantity'})

    h8_data_diff['pct_change'] = h8_data_diff['Quantity'].pct_change()*100

    h8_data = h8_data_diff[['Month', 'pct_change']]
    fig = px.line(h8_data, x= 'Month', y= 'pct_change')

    c2.subheader('H8: Imóveis com 1 quarto tiveram, em média, uma queda de 10% nas vendas quando analisado mês a mês (MoM).')
    c2.write('**Resultado:** Analisando mês a mês, as vendas de imóveis com 1 quarto tiveram uma média de {:.2f}% de cresimento.'.format(
        h8_data_diff['pct_change'].mean()))
    c2.plotly_chart(fig, use_container_width=True)


    #==================
    #Hypothesis 9
    #==================
    c1, c2 = st.beta_columns(2)
    h9_data_prop = data[['id', 'condition', 'bedrooms']].copy()

    h9_data_prop = h9_data_prop[h9_data_prop['bedrooms']==1]

    h9_data_prop = h9_data_prop[['id', 'condition']].groupby('condition').count().reset_index()
    h9_data_prop = h9_data_prop.rename(columns= {'id': 'Quantity'})

    sum_quantity = h9_data_prop['Quantity'].sum()
    h9_data_prop['proportion'] = h9_data_prop['Quantity']*100 / sum_quantity

    cond_1_2 = h9_data_prop.loc[:1, 'proportion'].sum()

    c1.subheader('H9: 10% dos imóveis com 1 quarto possuem condições menor ou igual a 2.')
    c1.write('**Resultado:** Foi observado que {:.2f}% dos imóveis com 1 quarto possuem condições menores ou igual a 2.'.format(cond_1_2))
    c1.dataframe(h9_data_prop)


    #==================
    #Hypothesis 10
    #==================
    h10_data_diff = data[['bedrooms', 'condition', 'price']].copy()
    
    h10_data_diff = h10_data_diff[h10_data_diff['bedrooms']==1]
    
    h10_data_diff = h10_data_diff[['condition', 'price']].groupby('condition').mean().reset_index()
    h10_data_diff = h10_data_diff.rename(columns= {'price': 'Mean Price'})

    h10_data_diff['pct_change'] = h10_data_diff['Mean Price'].pct_change()*100

    c2.subheader('H10 - Imóveis com 1 quarto e condição 3 são 40% mais caros do que os imóveis com 1 quarto e condição 2.')
    c2.write('Imóveis que possuem 1 quarto e condição 3 são {:.2f}% mais caros que imóveis com condição 2 e com a mesma quantidade de quartos.'.format(
        h10_data_diff.loc[h10_data_diff['condition'] == 3, 'pct_change'].values[0]
    ))
    c2.dataframe(h10_data_diff)

if __name__ == '__main__':
    #Extraction Data
    path_data = 'datasets/kc_house_data.csv'
    path_purchase = 'datasets/purchase_table.csv'
    path_sale = 'datasets/sales_table.csv'
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'

    data = get_data(path_data)
    purchase_table = get_data(path_purchase)
    sale_table = get_data(path_sale)
    geofile = get_geofile(url)

    #Transformation
    data_trasnformed = transform_data(data)

    #Show data
    page = navigation_sidebar()
        
    if page == 'Distrubuição Comercial':
        commercial_distribution( data_trasnformed )

    elif page == 'Overview por Região':
        region_overview(data_trasnformed, geofile)
    
    elif page == 'Recomendações':
        recommendations_area(purchase_table, sale_table)

    elif page == 'Validação de Hipóteses':
        hypotheses_area(data_trasnformed)
    
    else:
        data_overview(data_trasnformed)