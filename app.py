from flask import Flask, render_template, request
import folium
from folium.plugins import MarkerCluster
import json

app = Flask(__name__)

with open("sido_with_kor_field_and_region.json", "r", encoding="utf-8") as f:
    sido_geojson = json.load(f)

with open("지역별_음식유형_요약.json", "r", encoding="utf-8") as f:
    food_json = json.load(f)

# 카테고리 목록
CATEGORIES = list(next(iter(food_json.values())).keys())

# region 매핑 테이블
REGION_MAP = {
    "서울": "서울",
    "부산": "부산",
    "대구": "대구",
    "인천": "인천",
    "광주": "광주",
    "대전": "대전",
    "울산": "울산",
    "경기": "경기",
    "강원": "강원",
    "제주": "제주",
    "충청북도": "충청",
    "충청남도": "충청",
    "전라북도": "전라",
    "전라남도": "전라",
    "경상북도": "경상",
    "경상남도": "경상",
    "세종": "충청",
}


# 색상 계산 함수 (최소~최대값 기준으로 초록~빨강 그라데이션)
def get_color(value, vmin, vmax):
    # 0: 초록, 1: 빨강
    ratio = (value - vmin) / (vmax - vmin) if vmax > vmin else 0
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    b = 0
    return f"#{r:02x}{g:02x}{b:02x}"


@app.route("/", methods=["GET", "POST"])
def index():
    selected_cat = request.form.get("category")
    if not selected_cat:
        selected_cat = None

    # 각 지역별 평균값 추출
    region_values = {}
    if selected_cat:
        for region, foods in food_json.items():
            if selected_cat in foods:
                region_values[region] = foods[selected_cat]["평균"]

    # 색상 범위
    values = list(region_values.values()) if region_values else []
    vmin, vmax = (min(values), max(values)) if values else (0, 1)

    # folium 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=6, tiles="CartoDB positron")

    def style_fn(feature):
        region = feature["properties"].get("REGION")
        if not selected_cat:
            # 카테고리 미선택 시 하늘색
            return {
                "fillColor": "#87ceeb",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.6,
            }
        json_region = REGION_MAP.get(region, region)
        value = region_values.get(json_region)
        if region == "세종" and value is None and "충청" in region_values:
            value = region_values["충청"]
        color = get_color(value, vmin, vmax) if value is not None else "#cccccc"
        return {
            "fillColor": color,
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.6,
        }

    # Tooltip 필드/alias 동적 설정
    if not selected_cat:
        tooltip_fields = ["REGION"]
        tooltip_aliases = ["지역"]
    else:
        tooltip_fields = ["REGION"]
        tooltip_aliases = ["지역"]
        stats = ["평균", "중위수", "Q1", "Q3", "IQR", "개수"]
        for feature in sido_geojson["features"]:
            region = feature["properties"].get("REGION")
            json_region = REGION_MAP.get(region, region)
            food_info = food_json.get(json_region, {}).get(selected_cat, {})
            for stat in stats:
                feature["properties"][f"선택_{stat}"] = food_info.get(stat, "N/A")
        for stat in stats:
            tooltip_fields.append(f"선택_{stat}")
            tooltip_aliases.append(stat)

    folium.GeoJson(
        sido_geojson,
        name="geojson",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases),
    ).add_to(m)
    map_html = m._repr_html_()
    return render_template(
        "index.html",
        map_html=map_html,
        categories=CATEGORIES,
        selected_cat=selected_cat if selected_cat else "",
        vmin=int(vmin) if selected_cat else None,
        vmax=int(vmax) if selected_cat else None,
    )


if __name__ == "__main__":
    app.run(debug=True)
