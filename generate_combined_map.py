#!/usr/bin/env python3
"""
Comprehensive Combined Map Generator
Creates a single interactive map integrating all visualizations with toggle-able layers
"""

import pandas as pd
import folium
from folium import plugins
import os
import glob
import re

# City coordinates dictionary
CITY_COORDS = {
    '北京': (39.9042, 116.4074),
    '天津': (39.3434, 117.3616),
    '上海': (31.2304, 121.4737),
    '成都': (30.5728, 104.0668),
    '长沙': (28.2282, 112.9388),
    '南京': (32.0603, 118.7969),
    '镇江': (32.2109, 119.4550),
    '沈阳': (41.8057, 123.4328),
    '昆明': (25.0389, 102.7183),
    '广州': (23.1291, 113.2644),
    '香港': (22.3193, 114.1694),
    '青海': (36.6171, 101.7782)
}

# Japanese library coordinates
LIBRARY_COORDS = {
    '天理大學': (34.5964, 135.8378),
    '大阪大學': (34.8211, 135.5229),
    '龍谷大學': (34.9669, 135.7730),
    '東洋文庫': (35.7368, 139.7497),
    '早稻田大學': (35.7090, 139.7197),
    '慶應義塾大學': (35.6498, 139.7386),
    '東京大學': (35.7126, 139.7622),
    '京都大學': (35.0262, 135.7819),
    '筑波大學': (36.1094, 140.1025),
    '一橋大學': (35.6937, 139.4271)
}

def standardize_city(city_str):
    """Standardize city names"""
    if not isinstance(city_str, str):
        return None
    
    city_str = city_str.strip()
    
    # Remove parenthetical content
    city_str = re.sub(r'\([^)]*\)', '', city_str).strip()
    
    # Mapping of variations
    city_map = {
        '北平': '北京',
        '京师': '北京',
        '燕京': '北京',
        '天津市': '天津',
        '上海市': '上海',
        '成都市': '成都',
        '长沙市': '长沙',
        '南京市': '南京',
        '金陵': '南京',
        '镇江市': '镇江',
        '沈阳市': '沈阳',
        '盛京': '沈阳',
        '昆明市': '昆明',
        '广州市': '广州',
        '羊城': '广州'
    }
    
    return city_map.get(city_str, city_str)

def parse_year(year_str, era_str):
    """Parse year from Chinese era names"""
    if pd.notna(year_str):
        try:
            return int(float(year_str))
        except:
            pass
    
    if pd.notna(era_str):
        era_str = str(era_str).strip()
        
        # Republic era (民國)
        match = re.search(r'民國\s*(\d+)', era_str)
        if match:
            return 1911 + int(match.group(1))
        
        # Guangxu era (光緒)
        match = re.search(r'光緒\s*(\d+)', era_str)
        if match:
            return 1874 + int(match.group(1))
        
        # Qing era patterns
        match = re.search(r'清\s*(\d+)', era_str)
        if match:
            return 1800 + int(match.group(1))
    
    return None

def categorize_book(title):
    """Categorize books by title keywords"""
    if not isinstance(title, str):
        return "General"
    
    title_lower = title.lower()
    
    theology_keywords = ['tianfang', '天方', 'islam', 'muslim', 'quran', 'koran', 
                         'hadith', 'faith', 'religion', 'theology', '教義', '教理',
                         '經典', '教法', '真理', '大典']
    language_keywords = ['grammar', 'language', 'dictionary', 'vocabulary', 
                         '文法', '語法', '字典', '詞典', '語言']
    history_keywords = ['history', 'travel', 'journey', '歷史', '史', '遊記', '旅']
    
    for keyword in theology_keywords:
        if keyword in title_lower:
            return "Theology"
    for keyword in language_keywords:
        if keyword in title_lower:
            return "Language"
    for keyword in history_keywords:
        if keyword in title_lower:
            return "History"
    
    return "General"

print("=" * 60)
print("Comprehensive Combined Map Generator")
print("Islamic Books in Chinese - All Visualizations Integrated")
print("=" * 60)

# Find CSV file
csv_files = glob.glob('*الكتب*.csv')
if not csv_files:
    csv_files = glob.glob('*.csv')

if not csv_files:
    print("ERROR: No CSV file found!")
    exit(1)

csv_file = sorted(csv_files)[0]
print(f"Found CSV file: {csv_file}")

# Read data
print(f"Reading CSV file: {csv_file}")
df = pd.read_csv(csv_file, encoding='utf-8')
print(f"Total records: {len(df)}")

# Process data
df['city_standardized'] = df.iloc[:, 9].apply(standardize_city)
df['year_parsed'] = df.apply(lambda row: parse_year(
    row.iloc[6] if len(row) > 6 else None,
    row.iloc[5] if len(row) > 5 else None
), axis=1)
df['category'] = df.iloc[:, 2].apply(categorize_book)

# Filter geocodable books
df_geo = df[df['city_standardized'].isin(CITY_COORDS.keys())].copy()
df_geo['lat'] = df_geo['city_standardized'].map(lambda x: CITY_COORDS[x][0])
df_geo['lon'] = df_geo['city_standardized'].map(lambda x: CITY_COORDS[x][1])

print(f"Records with valid cities: {len(df_geo)}")
print(f"Records with geocoded cities: {len(df_geo)}")

# Create comprehensive map
print("Creating comprehensive combined map...")

m = folium.Map(
    location=[35, 110],
    zoom_start=4,
    tiles='OpenStreetMap',
    control_scale=True
)

# Add title
title_html = '''
<div style="position: fixed; 
            top: 10px; left: 50px; width: 500px; height: 90px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 10px">
<h4 style="margin:0;">Comprehensive Interactive Digital Atlas</h4>
<p style="margin:5px 0;">Islamic Books in Chinese - All Visualizations Combined</p>
<p style="margin:0; font-size:12px;">Toggle layers in the top-right corner</p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Layer 1: Individual Book Markers
marker_cluster = plugins.MarkerCluster(name='Book Markers (185 books)', show=True).add_to(m)

for idx, row in df_geo.iterrows():
    popup_html = f"""
    <div style="width: 300px;">
        <h4>{row.iloc[2]}</h4>
        <p><strong>Author:</strong> {row.iloc[3] if pd.notna(row.iloc[3]) else 'Unknown'}</p>
        <p><strong>Publisher:</strong> {row.iloc[10] if pd.notna(row.iloc[10]) else 'Unknown'}</p>
        <p><strong>City:</strong> {row['city_standardized']}</p>
        <p><strong>Year:</strong> {row['year_parsed'] if pd.notna(row['year_parsed']) else 'Unknown'}</p>
        <p><strong>Category:</strong> {row['category']}</p>
        <p><strong>Library:</strong> {row.iloc[11] if pd.notna(row.iloc[11]) else 'Unknown'}</p>
    </div>
    """
    
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row.iloc[2][:50] if len(str(row.iloc[2])) > 50 else row.iloc[2],
        icon=folium.Icon(color='blue', icon='book', prefix='fa')
    ).add_to(marker_cluster)

# Layer 2: Category Heatmaps
categories = ['Theology', 'Language', 'History', 'General']
colors = {'Theology': 'red', 'Language': 'green', 'History': 'purple', 'General': 'orange'}

for category in categories:
    df_cat = df_geo[df_geo['category'] == category]
    if len(df_cat) > 0:
        heat_data = [[row['lat'], row['lon']] for _, row in df_cat.iterrows()]
        
        plugins.HeatMap(
            heat_data,
            name=f'{category} Heatmap ({len(df_cat)} books)',
            min_opacity=0.3,
            radius=25,
            blur=30,
            gradient={
                0.0: 'blue',
                0.5: colors[category],
                1.0: 'darkred'
            },
            show=False
        ).add_to(m)

# Layer 3: Publisher Distribution
publisher_stats = df_geo.groupby('city_standardized').agg({
    'year_parsed': lambda x: f"{x.min():.0f}-{x.max():.0f}" if x.notna().any() else "Unknown",
    'lat': 'first',
    'lon': 'first',
    'city_standardized': 'count'
}).rename(columns={'city_standardized': 'count'})

publisher_layer = folium.FeatureGroup(name='Publisher Circles (50 publishers)', show=False)

for city, data in publisher_stats.iterrows():
    count = data['count']
    year_range = data['year_parsed']
    
    # Size based on count
    radius = min(count * 3, 50)
    
    # Color based on longevity
    if '-' in str(year_range):
        try:
            years = year_range.split('-')
            span = int(years[1]) - int(years[0])
            if span > 30:
                color = 'red'
            elif span > 15:
                color = 'orange'
            else:
                color = 'blue'
        except:
            color = 'gray'
    else:
        color = 'gray'
    
    folium.CircleMarker(
        location=[data['lat'], data['lon']],
        radius=radius,
        popup=f"<b>{city}</b><br>Books: {count}<br>Years: {year_range}",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6
    ).add_to(publisher_layer)

publisher_layer.add_to(m)

# Layer 4: China→Japan Network Flows
network_layer = folium.FeatureGroup(name='Migration Flows (China→Japan)', show=False)

# Add Japanese library markers
for library, coords in LIBRARY_COORDS.items():
    library_books = df_geo[df_geo.iloc[:, 11].astype(str).str.contains(library.split('大學')[0], na=False)]
    count = len(library_books)
    
    if count > 0:
        folium.Marker(
            location=coords,
            popup=f"<b>{library}</b><br>Books: {count}",
            tooltip=f"{library} ({count} books)",
            icon=folium.Icon(color='red', icon='university', prefix='fa')
        ).add_to(network_layer)

# Add flow lines
for city, coords in CITY_COORDS.items():
    city_books = df_geo[df_geo['city_standardized'] == city]
    tenri_books = city_books[city_books.iloc[:, 11].astype(str).str.contains('天理', na=False)]
    
    if len(tenri_books) > 0:
        folium.PolyLine(
            locations=[coords, LIBRARY_COORDS['天理大學']],
            color='red',
            weight=2,
            opacity=0.5,
            popup=f"{city} → Tenri University: {len(tenri_books)} books"
        ).add_to(network_layer)

network_layer.add_to(m)

# Layer 5: Temporal Slider
df_temporal = df_geo[df_geo['year_parsed'].notna()].copy()
df_temporal['year_int'] = df_temporal['year_parsed'].astype(int)

if len(df_temporal) > 0:
    time_data = []
    for _, row in df_temporal.iterrows():
        time_data.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['lon'], row['lat']]
            },
            'properties': {
                'time': str(row['year_int']),
                'popup': f"{row.iloc[2]}<br>{row['city_standardized']}<br>{row['year_int']}",
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'purple',
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 5
                }
            }
        })
    
    plugins.TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': time_data},
        period='P1Y',
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options='YYYY',
        time_slider_drag_update=True
    ).add_to(m)

# Add layer control
folium.LayerControl(collapsed=False).add_to(m)

# Add fullscreen option
plugins.Fullscreen().add_to(m)

# Save map
output_file = 'all_in_one_map.html'
m.save(output_file)

print("=" * 60)
print(f"✓ Successfully generated: {output_file}")
print(f"✓ Total books visualized: {len(df_geo)}")
print(f"✓ Integrated layers:")
print(f"  - Book Markers: {len(df_geo)} books")
print(f"  - Category Heatmaps: {len(categories)} layers")
print(f"  - Publisher Circles: {len(publisher_stats)} cities")
print(f"  - Migration Flows: China→Japan network")
print(f"  - Temporal Evolution: {len(df_temporal)} books with dates")
print("=" * 60)
print("\nOpen all_in_one_map.html in your web browser to view the comprehensive atlas.")
print("Toggle layers on/off using the control in the top-right corner.")
