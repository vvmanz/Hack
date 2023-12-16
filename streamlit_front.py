import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Функция для запроса к API для получения рейсов
def fetch_flights(departure_city, destination_city, departure_date, return_date):
    departure_date_str = departure_date.strftime('%Y-%m-%d')
    return_date_str = return_date.strftime('%Y-%m-%d')
    response = requests.get(f'http://localhost:5000/api/flights?departure_city={departure_city}&destination_city={destination_city}&departure_date={departure_date_str}&return_date={return_date_str}')
    return response

# Функция для отображения рейсов и кнопок прогнозирования
def show_flights(flights_data, response_data):
    if response_data.get('alternative_results') == 1:
        st.info("К сожалению, на выбранные даты нет доступных рейсов. Вот все доступные авиарейсы с датой вылета, указанной вами:")
    elif response_data.get('alternative_results') == 2:
        st.warning("К сожалению, доступных билетов на вашу дату вылета не найдено. Здесь представлен список билетов, которые, возможно, вам подойдут:")
    elif response_data.get('alternative_results') == 0:
        st.success("Найдены следующие рейсы:")

    for flight in flights_data:
        flight_info = f"{flight[1]} -> {flight[2]}, {flight[3]} - {flight[4]},Авиакомпания: {flight[5]}, Цена: {flight[6]} руб."
        st.write(flight_info)
        if st.button("Прогноз цены на билет", key=f"button_{flight[0]}"):
            fetch_and_plot_price_forecast(flight[1], flight[2])

# Функция для запроса прогноза цен и построения графика
def fetch_and_plot_price_forecast(departure_city, destination_city):
    price_response = requests.get(f'http://localhost:5000/api/price_forecast?departure_city={departure_city}&destination_city={destination_city}')
    if price_response.status_code == 200:
        price_data = price_response.json()
        plot_price_forecast(price_data)
    else:
        st.error("Ошибка при получении данных о ценах")

# Функция построения графика цен
def plot_price_forecast(price_data):
    df = pd.DataFrame(price_data, columns=["Дата", "Цена"])
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
    df = df.sort_values(by='Дата')

    plt.figure(figsize=(10, 5), facecolor='none')
    ax = plt.subplot(111)
    ax.set_facecolor('none')

    csfont = {'fontname': 'Comic Sans'}

    ax.plot(df['Дата'], df['Цена'], marker='o', color='limegreen')
    ax.set_title("Изменение цен на билеты", color='white',**csfont)
    ax.set_xlabel("Дата", color='white',**csfont)
    ax.set_ylabel("Цена (руб)", color='white',**csfont)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt)


def main():
    st.markdown("""
        <style>
        .header {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
            text-align: center;
        }
        .subheader {
            color: #ffffff;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="header">Название Компании или Проекта</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Добро пожаловать в наш сервис прогнозирования стоимости авиабилетов</div>', unsafe_allow_html=True)

    with st.form("input_form"):
        departure_city = st.selectbox("Город вылета", ["Токио", "Сингапур", "Пекин", "Гонг Конг", "Манила", "Тайпей", "Гатвик", "Лос-Анджелес"])
        destination_city = st.selectbox("Город назначения", ["Токио", "Сингапур", "Пекин", "Гонг Конг", "Манила", "Тайпей", "Гатвик", "Лос-Анджелес"])
        departure_date = st.date_input("Дата вылета", datetime.today())
        return_date = st.date_input("Дата прилета", datetime.today())
        submit_button = st.form_submit_button("Найти рейсы")

    if submit_button:
        response = fetch_flights(departure_city, destination_city, departure_date, return_date)
        if response.status_code == 200:
            response_data = response.json()
            st.session_state['flights_data'] = response_data['flights']
            st.session_state['response_data'] = response_data
        else:
            st.error("Ошибка при получении данных")

    if 'flights_data' in st.session_state:
        show_flights(st.session_state['flights_data'], st.session_state['response_data'])

if __name__ == "__main__":
    main()