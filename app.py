from flask import Flask, render_template
import folium
from folium.plugins import MarkerCluster
import json

app = Flask(__name__)

with open('korea_boundary.geojson', 'r', encoding='utf-8') as f:
    korea_geojson = json.load(f)

@app.route('/')
def index():
    # Folium 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    # 예시 데이터 추가
    data = [
        {'location': [37.5665, 126.9780], 'tooltip': 'Seoul', 'price': 35000},
        {'location': [35.1796, 129.0756], 'tooltip': 'Busan', 'price': 30000},
        # 추가 데이터...
    ]

    for item in data:
        folium.Marker(
            location=item['location'],
            popup=f"Price: {item['price']}",
            tooltip=item['tooltip']
        ).add_to(marker_cluster)

    # 한국 경계선 추가
    folium.GeoJson(
        korea_geojson,
        name='geojson',
        style_function=lambda x: {'fillColor': '#00000000', 'color': 'black', 'weight': 1}
    ).add_to(m)

    # HTML로 변환
    map_html = m._repr_html_()

    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True) 