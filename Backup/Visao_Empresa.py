
# libraries
from haversine import haversine
from datetime import datetime
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import folium_static


# Import Dataset
df = pd.read_csv('Dataset/train.csv')
df1 = df.copy()

#----------------------------------------------------------------------------------#
# 1. Conversão a coluna Age de texto para número
linhas_selecionadas = (df1 ['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['Delivery_person_Age'] = df1['Delivery_person_Age']. astype( int )
df1.shape

linhas_selecionadas = (df1 ['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1 ['City'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1 ['Festival'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()


# 2. Conversão a coluna de Ratings de texto para número decimal (float)
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings']. astype( float )

# 3. Conversão da coluna order_date de texto para data
df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

# 4. Conversão de Multiple_deliveries para Interiro
linhas_selecionadas = (df1 ['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

# 5. Removendo os espaços dentro de strings/texto/objects
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

# 6. Limpeza sobre a coluna Time_taken(min)
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
#----------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------#
#Barra Lateral do StreamLit
#----------------------------------------------------------------------------------#
st.header("Marketplace - Visão Cliente")

# Carregar imagem
image_path = "Logo.png"
image = Image.open(image_path)
st.sidebar.image(image, width=300)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""___""")
st.sidebar.markdown("## Selecione uma data limite")

# Armazenar o valor do slider em uma variável
data_limite = st.sidebar.slider(
    "Até qual data?",
    value=datetime(2022, 4, 6),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="MM-DD-YYYY")

st.sidebar.markdown("""___""")
traffic_options = st.sidebar.multiselect(
    "Quais as Condições de Trânsito",
    ["Low", "Medium", "High", "Jam"], 
    default=["Low", "Medium", "High", "Jam"])
st.sidebar.markdown("""___""")
st.sidebar.markdown("## Powered by Comunidade DS")

# Filtros (assumindo que a coluna de data se chama 'Order_Date' - ajuste conforme seu DataFrame)
if 'Order_Date' in df1.columns:
    linhas_selecionadas = df1["Order_Date"] < data_limite
    df1 = df1.loc[linhas_selecionadas, :]
else:
    st.warning("Coluna de data não encontrada no DataFrame")

# Filtro de tráfego
linhas_selecionadas = df1["Road_traffic_density"].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

st.dataframe(df1)

#----------------------------------------------------------------------------------#
#Layout no Streamlit 
#----------------------------------------------------------------------------------#

tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])

with tab1: 
    with st.container():
        #Order Metric
        st.markdown("# Order by Day")
        cols = ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()
        fig=px.bar ( df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Traffic Order Share")
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            fig=px.pie(df_aux, values='ID', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
        
        
        with col2:
            st.header("Traffic Order City")
            df_aux = df1.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            fig=px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown("# Order by Week")
        df1 ['week_of_year']  = df1 ['Order_Date'].dt.strftime( '%U' )
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
        fig=px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("# Order by Week")
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        df_aux = pd.merge(df_aux01, df_aux02, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig=px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("# Country Maps")
    df_aux = (df.loc[:, ['City','Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']]
            .groupby(['City', 'Road_traffic_density'])
            .median().reset_index())

    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux = df_aux.head(50)
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info ['Delivery_location_latitude'],
                    location_info ['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)