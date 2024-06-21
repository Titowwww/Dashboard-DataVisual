import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import altair as alt
import pymysql
import sqlalchemy
import plotly.express as px
from datetime import datetime

# create connection ke db
def create_connection():
    conn_info = st.secrets["connections"]["mydb"]
    connection_string = f"{conn_info['dialect']}+{conn_info['driver']}://{conn_info['username']}:{conn_info['password']}@{conn_info['host']}:{conn_info['port']}/{conn_info['database']}"
    engine = sqlalchemy.create_engine(connection_string)
    return engine.connect()

# Fungsi untuk menjalankan query dan mendapatkan data
def fetch_data(query):
    connection = create_connection()
    if connection is None:
        return None
    try:
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        connection.close()

# membaca file csv
file_path = 'imdb_top250_50movies.csv'
data2 = pd.read_csv(file_path)

page = st.sidebar.selectbox('Select Page', ['ADVENTURE WORKS', 'IMDB TOP 50 MOVIES'])

if page == 'ADVENTURE WORKS':
    st.title('Adventure Works Dashboard🚲')

    # COMPARISON
    st.header("Sales by Subcategory💹")
    # SQL queries
    dimproduct_query = 'SELECT ProductSubCategoryKey, ProductKey FROM dimproduct'
    dimproductsubcategory_query = 'SELECT EnglishProductSubCategoryName, ProductSubCategoryKey FROM dimproductsubcategory'
    factinternetsales_query = 'SELECT SalesAmount, ProductKey FROM factinternetsales'

    dimproduct = fetch_data(dimproduct_query)
    dimproductsubcategory = fetch_data(dimproductsubcategory_query)
    factinternetsales = fetch_data(factinternetsales_query)

    if dimproduct is None or dimproductsubcategory is None or factinternetsales is None:
        st.error("Error fetching data from database")
    else:
        # Merge data in the correct order
        df = factinternetsales.merge(dimproduct, on='ProductKey')
        df = df.merge(dimproductsubcategory, on='ProductSubCategoryKey')

        # Calculate sales by subcategory
        sales_by_subcategory = df.groupby("EnglishProductSubCategoryName")["SalesAmount"].sum().reset_index()

        # Streamlit visualization using Altair
        bar_chart = alt.Chart(sales_by_subcategory).mark_bar().encode(
            x=alt.X('EnglishProductSubCategoryName', title='Product SubCategory'),
            y=alt.Y('SalesAmount', title='Sales Amount'),
            color=alt.Color('EnglishProductSubCategoryName', legend=None)  # Menambahkan warna untuk setiap bar
        ).properties(
            width=800
        )
        st.altair_chart(bar_chart, use_container_width=True)
        st.write("""Grafik bar chart di atas menampilkan jumlah penjualan dari setiap subkategori produk di Adventure Works. Sumbu X menunjukkan berbagai subkategori produk, 
                 sedangkan sumbu Y menunjukkan total penjualan (Sales Amount) dalam angka. """)
        st.write("""Pengetahuan ini sangat penting bagi perusahaan dalam mengambil keputusan strategis terkait produksi dan penjualan. Dengan memahami subkategori produk yang memiliki penjualan tinggi, 
                 perusahaan dapat fokus pada peningkatan produksi dan strategi pemasaran. Sebaliknya, untuk subkategori dengan penjualan rendah, perusahaan dapat mengevaluasi kembali strategi mereka atau mempertimbangkan inovasi produk untuk meningkatkan penjualan.""")
        
    # RELATIONSHIP
    st.header("Relationship between Standard Cost and List Price🔗")
    dimproduct_query = 'SELECT StandardCost, ListPrice FROM dimproduct'
    df = fetch_data(dimproduct_query)

    if df is None:
        st.error("Error fetching data from database")
    else:
        scatter_chart = alt.Chart(df).mark_point().encode(
            x=alt.X('StandardCost', title='Standard Cost'),
            y=alt.Y('ListPrice', title='List Price')
        ).properties(
            width=800,
            height=400
        )
        st.altair_chart(scatter_chart, use_container_width=True)
        st.write("""Grafik scatter plot di atas menampilkan hubungan antara dua variabel penting: Standard Cost (biaya produksi) dan List Price (harga jual). Sumbu X merepresentasikan Standard Cost, sedangkan sumbu Y merepresentasikan List Price.
                Dari visualisasi ini, kita dapat mengamati adanya hubungan positif antara Standard Cost dan List Price. Artinya, ketika biaya produksi meningkat, harga jual juga cenderung meningkat. Titik-titik data yang tersebar di grafik menunjukkan bahwa ada korelasi yang cukup kuat antara kedua variabel ini.""")
        st.write("""Grafik ini sangat berguna bagi organisasi untuk memahami dinamika antara biaya produksi dan harga jual. Dengan pemahaman ini, perusahaan dapat lebih baik dalam menentukan strategi penetapan harga yang optimal. Selain itu, memahami hubungan ini juga membantu dalam pengambilan keputusan terkait pengendalian biaya dan strategi pemasaran.""")

    # COMPOSITION
    st.header("Sales of Subcategory by Region📌")

    # Queries to fetch data from tables
    dimsalesterritory_query = 'SELECT SalesTerritoryRegion, SalesTerritoryKey FROM dimsalesterritory'
    dimsalesterritory = fetch_data(dimsalesterritory_query)

    factinternetsales_query = 'SELECT SalesAmount, ProductKey, SalesTerritoryKey FROM factinternetsales'
    factinternetsales = fetch_data(factinternetsales_query)

    dimproduct_query = 'SELECT ProductSubCategoryKey, ProductKey FROM dimproduct'
    dimproduct = fetch_data(dimproduct_query)

    dimproductsubcategory_query = 'SELECT EnglishProductSubCategoryName, ProductSubCategoryKey FROM dimproductsubcategory'
    dimproductsubcategory = fetch_data(dimproductsubcategory_query)

    if dimsalesterritory is None or factinternetsales is None or dimproduct is None or dimproductsubcategory is None:
        st.error("Error fetching data from database")
    else:
        # Merging tables
        df = pd.merge(factinternetsales, dimsalesterritory, on='SalesTerritoryKey')
        df = pd.merge(df, dimproduct, on='ProductKey')
        df = pd.merge(df, dimproductsubcategory, on='ProductSubCategoryKey')

        # Mengambil list unik dari region
        regions = df['SalesTerritoryRegion'].unique()

        # Membuat dropdown di Streamlit
        selected_region = st.selectbox('Select Region', regions)

        # Filtering data berdasarkan region yang dipilih
        filtered_data = df[df['SalesTerritoryRegion'] == selected_region]
        #st.bar_chart(filtered_data.groupby('EnglishProductSubCategoryName')['SalesAmount'].sum())
        grouped_data = filtered_data.groupby(['EnglishProductSubCategoryName', 'SalesTerritoryRegion'])['SalesAmount'].sum().reset_index()

        fig = px.treemap(grouped_data, path=['SalesTerritoryRegion', 'EnglishProductSubCategoryName'], values='SalesAmount',
                     color='SalesAmount', color_continuous_scale='Blues')

        # Menampilkan treemap di Streamlit
        st.plotly_chart(fig)
        st.write("""Grafik Treemap ini menunjukkan pemetaan penjualan tiap produk subcategory dari sebuah region. Region dapat dipilih melalui dropdown yang disediakan.
                 Dengan adanya grafik ini, organisasi dapat membantu dalam mengambil keputusan untuk penjualan product subcategory dari tiap region""")

    # DISTRIBUTION
    st.header("Employees Age Distribution🧑")

    dimemployee_query = 'SELECT EmployeeKey, BirthDate FROM dimemployee'
    dimemployee = fetch_data(dimemployee_query)

    if dimemployee is None:
        st.error("Error fetching data from database")
    else:
        dimemployee['BirthDate'] = pd.to_datetime(dimemployee['BirthDate'], format='%Y%m%d')

        # Menghitung usia karyawan
        current_date = datetime.now()
        dimemployee['Age'] = dimemployee['BirthDate'].apply(lambda x: current_date.year - x.year - ((current_date.month, current_date.day) < (x.month, x.day)))

        # Mengelompokkan usia ke dalam rentang
        bins = [20, 30, 40, 50, 60, 70]
        labels = ['20-29', '30-39', '40-49', '50-59', '60-69']
        dimemployee['AgeGroup'] = pd.cut(dimemployee['Age'], bins=bins, labels=labels, right=False)

         # Menghitung jumlah karyawan di setiap kelompok umur
        age_group_counts = dimemployee['AgeGroup'].value_counts().sort_index().reset_index()
        age_group_counts.columns = ['AgeGroup', 'Count']
        
        # Membuat bar chart 
        fig = px.bar(age_group_counts, x='AgeGroup', y='Count', 
                     title='Distribution of Employee Ages',
                     labels={'AgeGroup': 'Range of Age', 'Count': 'Amounts'},
                     color='AgeGroup', color_discrete_sequence=px.colors.qualitative.Set3)

        # Menampilkan bar chart di Streamlit
        st.plotly_chart(fig, use_container_width=True)
        st.write("""Grafik bar chart di atas menampilkan distribusi usia karyawan di perusahaan. Sumbu X menunjukkan rentang usia karyawan, 
                 sedangkan sumbu Y menunjukkan jumlah karyawan dalam setiap rentang usia tersebut.""")
        st.write("""Pemahaman tentang distribusi usia karyawan ini sangat penting bagi perusahaan dalam berbagai aspek, 
                 seperti perencanaan tenaga kerja, pengembangan karir, dan program pelatihan. Mengetahui bahwa mayoritas karyawan berada dalam kelompok usia tertentu dapat membantu 
                 perusahaan menyesuaikan kebijakan dan program yang sesuai dengan kebutuhan spesifik dari kelompok usia tersebut.""")

elif page == 'IMDB TOP 50 MOVIES':
    st.title("IMDB TOP 50 MOVIES🎥")

    # Mengubah tipe data string menjadi float di kolom budget
    data2['Budget'] = pd.to_numeric(data2['Budget'].str.replace('$', '').str.replace(',', ''), errors='coerce')

    # Mengubah tipe data string menjadi float di kolom Gross US & Canada
    data2['Gross US & Canada'] = pd.to_numeric(data2['Gross US & Canada'].str.replace('$', '').str.replace(',', ''), errors='coerce')

    # Mengubah tipe data string menjadi float di kolom Gross worldwide
    data2['Gross worldwide'] = pd.to_numeric(data2['Gross worldwide'].str.replace('$', '').str.replace(',', ''), errors='coerce')

    #COMPARISON
    st.header("Gross Worldwide by Year💸")
    # Mengubah kolom 'Opening_Week_Date' ke datetime
    data2['Opening_Week_Date'] = pd.to_datetime(data2['Opening_Week_Date'])
    # Membuat dropdown
    year_ranges = ['1970-1980', '1981-2000', '2001-2010', '2011-2020', '2021-2024']
    selected_year_range = st.selectbox('Select Movie Year Range', year_ranges)

    # Filtering data berdasarakan tahun
    if selected_year_range == '1970-1980':
        df_plot = data2[(data2['Opening_Week_Date'].dt.year >= 1970) & (data2['Opening_Week_Date'].dt.year <= 2000)]
    elif selected_year_range == '1981-2000':
        df_plot = data2[(data2['Opening_Week_Date'].dt.year >= 2001) & (data2['Opening_Week_Date'].dt.year <= 2010)]
    elif selected_year_range == '2001-2010':
        df_plot = data2[(data2['Opening_Week_Date'].dt.year >= 2001) & (data2['Opening_Week_Date'].dt.year <= 2010)]
    elif selected_year_range == '2011-2020':
        df_plot = data2[(data2['Opening_Week_Date'].dt.year >= 2011) & (data2['Opening_Week_Date'].dt.year <= 2020)]
    else:
        df_plot = data2[(data2['Opening_Week_Date'].dt.year >= 2021) & (data2['Opening_Week_Date'].dt.year <= 2024)]

    # Mengurutkan data dari yang tertinggi-terendah
    df_plot = df_plot.sort_values(by='Gross worldwide', ascending=False)

    # Membuat barchart
    fig = px.bar(df_plot, x='Title', y='Gross worldwide', color='Title', color_discrete_sequence=px.colors.sequential.Plotly3, title='Gross Worldwide by Year')
    st.plotly_chart(fig, use_container_width=True)
    st.write("""Grafik Barchart ini menampilkan Gross Worldwide dari 50 film teratas. Sumbu X menunjukkan Judul Film dan sumbu Y menunjukkan Gross Worldwide.
             Grafik ini dapat di filter berdasarkan tahun rilis film. Secara keseluruhan, visualisasi secara efektif menyajikan pendapatan kotor di seluruh dunia dari 50 film IMDb teratas,
              menawarkan gambaran singkat tentang film-film yang paling sukses secara komersial.""")

    # DISTRIBUTION
    st.header("Distribution of Aspect Ratio🎞️")
    # Menghitung jumlah setiap aspek rasio
    aspect_ratio_counts = data2['Aspect ratio'].value_counts().reset_index()
    aspect_ratio_counts.columns = ['Aspect ratio', 'Frequency']
    # Membuat bar chart menggunakan Altair dengan warna untuk setiap bar
    bar_chart = alt.Chart(aspect_ratio_counts).mark_bar().encode(
        x=alt.X('Aspect ratio', title='Aspect Ratio'),
        y=alt.Y('Frequency', title='Frequency'),
        color=alt.Color('Aspect ratio', legend=None)  # Menambahkan warna untuk setiap bar berdasarkan aspek rasio
    ).properties(
        width=800
    )
    # Menampilkan bar chart di Streamlit
    st.altair_chart(bar_chart, use_container_width=True)
    st.write("""Grafik Barchart ini menampilkan distribusi penggunaan Aspek Ratio dalam film. 
             Memahami distribusi aspek rasio dalam film dapat membantu pembuat film atau produsen film memilih aspek rasio yang tepat untuk menyampaikan cerita mereka secara efektif.""")

    #RELATIONSHIP
    st.header("Relationship between Budget and Gross Worldwide🪙")
    fig = px.scatter(data2, x='Budget', y='Gross worldwide')
    st.plotly_chart(fig, use_container_width=True)
    st.write("""Grafik Scatter Plot ini menampilkan relasi atau hubungan antara Budget dan Runtime. Visualisasi ini menunjukkan bahwa budget produksi film bukanlah penentu tunggal kesuksesan finansial. 
             Faktor-faktor lain juga berperan penting dalam menentukan pendapatan kotor film.""")

    # COMPOSITION
    st.header("Composition of Color🎨")
    # Menghitung jumlah setiap warna
    color_counts = data2['Color'].value_counts().reset_index()
    color_counts.columns = ['Color', 'Frequency']
    # Membuat pie chart menggunakan Plotly
    fig = px.pie(color_counts, names='Color', values='Frequency')
    # Menampilkan pie chart di Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.write("""Grafik Pie Chart ini menampilkan komposisi dari penggunaan warna pada sebuah film. Dari grafik ini,
              menunjukkan dominasi film berwarna dalam industri perfilman. Namun, film hitam putih masih memiliki perannya tersendiri. Pemilihan warna merupakan keputusan kreatif yang dapat memengaruhi gaya dan pesan yang ingin disampaikan oleh film.""")
