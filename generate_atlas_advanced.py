#!/usr/bin/env python3
"""
Advanced Interactive Digital Atlas Generator for Islamic Books Data
Implements spatiotemporal analysis, network visualization, and thematic mapping
"""

import os
import re
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, TimestampedGeoJson
import networkx as nx
import plotly.graph_objects as go
from collections import Counter, defaultdict
from datetime import datetime
import json


# Built-in geocoding dictionary for Chinese cities
CITY_COORDINATES = {
    '北京': (39.9042, 116.4074),
    '北平': (39.9042, 116.4074),
    '上海': (31.2304, 121.4737),
    '天津': (39.3434, 117.3616),
    '南京': (32.0603, 118.7969),
    '成都': (30.5728, 104.0668),
    '錦江': (30.5728, 104.0668),
    '錦城': (30.5728, 104.0668),
    '蓉城': (30.5728, 104.0668),
    '長沙': (28.2282, 112.9388),
    '星沙': (28.2282, 112.9388),
    '奉天': (41.8057, 123.4328),
    '瀋陽': (41.8057, 123.4328),
    '鎮江': (32.2109, 119.4552),
    '潤州': (32.2109, 119.4552),
    '京口': (32.2109, 119.4552),
    '京江': (32.2109, 119.4552),
    '雲南': (25.0406, 102.7125),
    '滇省': (25.0406, 102.7125),
    '導河': (36.2988, 102.9883),
    '廣州': (23.1291, 113.2644),
    '粵東省城': (23.1291, 113.2644),
    '廣邑': (23.1291, 113.2644),
    '香港': (22.3193, 114.1694),
    '燕湖': (39.9042, 116.4074),
}

# Library geocoding dictionary - Enhanced with Japanese institutions
LIBRARY_COORDINATES = {
    # Japanese libraries (primary collections)
    '天理大學': (34.5970, 135.8376),  # Tenri University, Nara
    '天理大學圖書館': (34.5970, 135.8376),
    'Tenri University': (34.5970, 135.8376),
    '大阪大學': (34.8218, 135.5228),  # Osaka University
    'Osaka University': (34.8218, 135.5228),
    '龍谷大學': (34.9807, 135.7556),  # Ryukoku University, Kyoto
    'Ryukoku University': (34.9807, 135.7556),
    '東洋文庫': (35.7339, 139.7544),  # Tōyō Bunko, Tokyo
    'Tōyō Bunko': (35.7339, 139.7544),
    # Western libraries
    'New York Public Library': (40.7532, -73.9822),
    'Harvard-Yenching Library': (42.3770, -71.1167),
    'British Library': (51.5299, -0.1271),
    'Bibliothèque nationale de France': (48.8338, 2.3765),
}

# Chinese era name to Western year conversion
def parse_chinese_era(era_str):
    """
    Parse Chinese era names to Western years.
    Examples: "民國8年" → 1919, "光緒25年" → 1899
    """
    if not era_str or pd.isna(era_str) or era_str.strip() == '？':
        return None
    
    era_str = str(era_str).strip()
    
    # Republic of China (民國)
    match = re.search(r'民國(\d+)年', era_str)
    if match:
        year_num = int(match.group(1))
        return 1911 + year_num  # Republic era starts in 1912
    
    # Qing Dynasty eras
    era_mappings = {
        '光緒': 1875,  # Guangxu (1875-1908)
        '宣統': 1909,  # Xuantong (1909-1911)
        '咸豐': 1851,  # Xianfeng (1851-1861)
        '同治': 1862,  # Tongzhi (1862-1874)
        '道光': 1821,  # Daoguang (1821-1850)
        '嘉慶': 1796,  # Jiaqing (1796-1820)
    }
    
    for era_name, start_year in era_mappings.items():
        match = re.search(f'{era_name}(\\d+)年', era_str)
        if match:
            year_num = int(match.group(1))
            return start_year + year_num - 1
    
    return None


def categorize_book(title):
    """
    Categorize books by type based on title keywords.
    Returns: theology, history, language, periodical, or general
    """
    if not title or pd.isna(title):
        return 'general'
    
    title = str(title).lower()
    
    # Theology/Religious keywords
    if any(keyword in title for keyword in ['天方', '清真', '經', '教', '理', '道', '法', '聖']):
        return 'theology'
    
    # History/Travel keywords
    if any(keyword in title for keyword in ['史', '記', '遊', '覲', '途', '誌']):
        return 'history'
    
    # Language/Grammar keywords
    if any(keyword in title for keyword in ['字', '語', '文', '典', '解']):
        return 'language'
    
    # Periodicals
    if any(keyword in title for keyword in ['報', '刊', '月刊', '週刊']):
        return 'periodical'
    
    return 'general'


def clean_city_name(city_str):
    """Clean and standardize city names."""
    if not city_str or pd.isna(city_str) or city_str.strip() == '？':
        return None
    
    city_str = city_str.strip()
    
    if ' ' in city_str:
        city_str = city_str.split()[0]
    
    if '（' in city_str:
        city_str = city_str.split('（')[0].strip()
    
    standardization_map = {
        '北平': '北京', '錦江': '成都', '錦城': '成都', '蓉城': '成都',
        '星沙': '長沙', '潤州': '鎮江', '京口': '鎮江', '京江': '鎮江',
        '滇省': '雲南', '粵東省城': '廣州', '廣邑': '廣州',
        '奉天': '瀋陽', '燕湖': '北京',
    }
    
    return standardization_map.get(city_str, city_str)


def geocode_city(city_name):
    """Get coordinates for a city."""
    return CITY_COORDINATES.get(city_name) if city_name else None


def geocode_library(library_name):
    """Get coordinates for a library - enhanced for Japanese institutions."""
    if not library_name or pd.isna(library_name):
        return None
    
    library_name = str(library_name).strip()
    
    # Try exact match
    if library_name in LIBRARY_COORDINATES:
        return LIBRARY_COORDINATES[library_name]
    
    # Japanese library fuzzy matching - check for key institutions
    japanese_institutions = {
        '天理': (34.5970, 135.8376),  # Tenri University
        '大阪': (34.8218, 135.5228),  # Osaka University
        '龍谷': (34.9807, 135.7556),  # Ryukoku University
        '東洋文庫': (35.7339, 139.7544),  # Tōyō Bunko
    }
    
    for keyword, coords in japanese_institutions.items():
        if keyword in library_name:
            return coords
    
    # Try fuzzy match with Western libraries
    for lib_key, coords in LIBRARY_COORDINATES.items():
        if lib_key.lower() in library_name.lower() or library_name.lower() in lib_key.lower():
            return coords
    
    return None


def find_csv_file():
    """Find the CSV file in the current directory."""
    csv_files = sorted([f for f in os.listdir('.') if f.endswith('.csv')])
    
    if csv_files:
        print(f"Found CSV file: {csv_files[0]}")
        return csv_files[0]
    elif os.path.exists('data.csv'):
        return 'data.csv'
    else:
        raise FileNotFoundError("No CSV file found")


def read_and_process_csv(csv_file):
    """
    Read and process CSV with enhanced data extraction.
    """
    print(f"\n{'='*60}")
    print(f"Reading CSV: {csv_file}")
    print(f"{'='*60}")
    
    df = pd.read_csv(csv_file, skiprows=[0])
    print(f"Total records: {len(df)}")
    
    # Extract columns - be more specific in search to avoid false matches
    title_col = next((col for col in df.columns if 'Title' in str(col) or '題名' in str(col)), df.columns[2])
    author_col = next((col for col in df.columns if 'Author' in str(col) or '著者' in str(col)), df.columns[4])
    city_col = next((col for col in df.columns if 'City' in str(col) or '出版城市' in str(col)), df.columns[9])
    publisher_col = next((col for col in df.columns if 'Publisher' in str(col) or '出版人' in str(col) or '機構' in str(col)), df.columns[10])
    era_col = next((col for col in df.columns if 'Chinese era' in str(col) or ('出版時間' in str(col) and 'Chinese' in str(col))), df.columns[5])
    year_col = next((col for col in df.columns if ('Year' in str(col) and 'Hijri' not in str(col)) or '西曆' in str(col)), df.columns[6])
    library_col = next((col for col in df.columns if 'Library' in str(col) and 'York' not in str(col) or '館藏' in str(col)), df.columns[11])
    
    columns_to_rename = {
        title_col: 'Title',
        author_col: 'Author',
        city_col: 'City',
        publisher_col: 'Publisher',
        era_col: 'Era',
        year_col: 'Year_Western',
        library_col: 'Library',
    }
    
    df_processed = df.rename(columns=columns_to_rename).copy()
    
    # Select only the renamed columns
    df_processed = df_processed[['Title', 'Author', 'City', 'Publisher', 'Era', 'Year_Western', 'Library']].copy()
    
    # Clean and enhance data
    df_processed['City_Clean'] = df_processed['City'].apply(clean_city_name)
    df_processed['Coordinates'] = df_processed['City_Clean'].apply(geocode_city)
    df_processed['Latitude'] = df_processed['Coordinates'].apply(lambda x: x[0] if x else None)
    df_processed['Longitude'] = df_processed['Coordinates'].apply(lambda x: x[1] if x else None)
    
    # Parse years
    df_processed['Year_Parsed'] = df_processed['Era'].apply(parse_chinese_era)
    df_processed['Year_Final'] = df_processed.apply(
        lambda row: row['Year_Parsed'] if row['Year_Parsed'] else 
                   (int(row['Year_Western']) if pd.notna(row['Year_Western']) and str(row['Year_Western']).replace('.', '').isdigit() else None),
        axis=1
    )
    
    # Categorize books
    df_processed['Category'] = df_processed['Title'].apply(categorize_book)
    
    # Geocode libraries
    df_processed['Library_Coords'] = df_processed['Library'].apply(geocode_library)
    df_processed['Library_Lat'] = df_processed['Library_Coords'].apply(lambda x: x[0] if x else None)
    df_processed['Library_Lon'] = df_processed['Library_Coords'].apply(lambda x: x[1] if x else None)
    
    # Filter valid records
    df_valid = df_processed[df_processed['Coordinates'].notna()].copy()
    
    print(f"Records with valid cities: {len(df_valid)}")
    print(f"Records with parsed years: {df_valid['Year_Final'].notna().sum()}")
    print(f"Records with library locations: {df_valid['Library_Coords'].notna().sum()}")
    
    return df_valid


def create_temporal_map(df, output_file='temporal_map.html'):
    """
    Create a time-lapse map showing spatiotemporal evolution.
    Feature #1: Spatiotemporal Evolution
    """
    print(f"\n{'='*60}")
    print("Creating Temporal Map (Time-Lapse)")
    print(f"{'='*60}")
    
    df_temporal = df[df['Year_Final'].notna()].copy()
    
    if len(df_temporal) == 0:
        print("⚠️  No records with valid years - skipping temporal map")
        return None
    
    # Calculate center
    center_lat = df_temporal['Latitude'].mean()
    center_lon = df_temporal['Longitude'].mean()
    
    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Prepare temporal data
    features = []
    for idx, row in df_temporal.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['Longitude'], row['Latitude']]
            },
            'properties': {
                'time': f"{int(row['Year_Final'])}-01-01",
                'popup': f"<b>{row['Title']}</b><br>{row['City_Clean']}<br>{int(row['Year_Final'])}",
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': '#ff0000',
                    'fillOpacity': 0.6,
                    'stroke': 'true',
                    'radius': 8
                }
            }
        }
        features.append(feature)
    
    # Add TimestampedGeoJson
    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='P1Y',
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=2,
        loop_button=True,
        date_options='YYYY',
        time_slider_drag_update=True
    ).add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 600px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 10px; opacity: 0.9;">
        <h3 style="margin: 0;">Temporal Evolution of Islamic Publishing</h3>
        <p style="margin: 5px 0;">Use the time slider to watch publishing centers shift over time</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(output_file)
    print(f"✓ Saved: {output_file}")
    print(f"  Year range: {int(df_temporal['Year_Final'].min())} - {int(df_temporal['Year_Final'].max())}")
    
    return m


def create_network_map(df, output_file='network_map.html'):
    """
    Create publisher-to-library network visualization showing China→Japan book migration.
    Feature #2: Publisher-to-Library Network - "The Book Road"
    """
    print(f"\n{'='*60}")
    print("Creating Publisher-to-Library Network (China→Japan)")
    print(f"{'='*60}")
    
    df_network = df[(df['Coordinates'].notna()) & (df['Library_Coords'].notna())].copy()
    
    if len(df_network) == 0:
        print("⚠️  No records with both publisher and library locations - skipping network map")
        return None
    
    # Analyze Japanese vs other collections
    japanese_books = df_network[df_network['Library'].str.contains('天理|大阪|龍谷|東洋', na=False)]
    print(f"  Books in Japanese libraries: {len(japanese_books)}")
    print(f"  Books in other libraries: {len(df_network) - len(japanese_books)}")
    
    center_lat = 35.0  # Centered between China and Japan
    center_lon = 115.0
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=4)
    
    # Add origin markers (Chinese publishing cities)
    for city in df_network['City_Clean'].unique():
        city_data = df_network[df_network['City_Clean'] == city]
        lat, lon = city_data.iloc[0]['Latitude'], city_data.iloc[0]['Longitude']
        count = len(city_data)
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=8 + count * 0.3,
            popup=f"<b>{city} (Publishing City)</b><br>{count} books published<br>Now preserved in Japanese collections",
            tooltip=f"{city}: {count} books",
            color='#0066cc',
            fill=True,
            fillColor='#0066cc',
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Group flow lines by library to reduce clutter
    library_flows = {}
    for library in df_network['Library'].unique():
        lib_data = df_network[df_network['Library'] == library]
        if lib_data.iloc[0]['Library_Coords']:
            lat, lon = lib_data.iloc[0]['Library_Lat'], lib_data.iloc[0]['Library_Lon']
            library_flows[library] = {
                'coords': (lat, lon),
                'count': len(lib_data),
                'cities': lib_data['City_Clean'].tolist()
            }
    
    # Draw flow lines from each city to each library
    flow_count = {}
    for idx, row in df_network.iterrows():
        flow_key = f"{row['City_Clean']}→{row['Library'][:10]}"
        flow_count[flow_key] = flow_count.get(flow_key, 0) + 1
    
    # Draw aggregated flow lines
    drawn_flows = set()
    for idx, row in df_network.iterrows():
        flow_key = (row['City_Clean'], row['Library'])
        if flow_key not in drawn_flows:
            drawn_flows.add(flow_key)
            count = sum(1 for i, r in df_network.iterrows() if r['City_Clean'] == row['City_Clean'] and r['Library'] == row['Library'])
            
            # Color based on destination (red for Japan, orange for others)
            is_japan = any(keyword in str(row['Library']) for keyword in ['天理', '大阪', '龍谷', '東洋'])
            line_color = '#cc0000' if is_japan else '#ff9900'
            line_opacity = min(0.2 + count * 0.05, 0.8)
            line_weight = max(1, min(count * 0.3, 4))
            
            folium.PolyLine(
                locations=[
                    [row['Latitude'], row['Longitude']],
                    [row['Library_Lat'], row['Library_Lon']]
                ],
                color=line_color,
                weight=line_weight,
                opacity=line_opacity,
                popup=f"{row['City_Clean']} → {row['Library'][:30]}<br>{count} books"
            ).add_to(m)
    
    # Add library markers (destinations)
    for library, data in library_flows.items():
        lat, lon = data['coords']
        count = data['count']
        
        # Determine if Japanese library
        is_japan = any(keyword in library for keyword in ['天理', '大阪', '龍谷', '東洋'])
        icon_color = 'red' if is_japan else 'green'
        lib_type = "🇯🇵 Japanese" if is_japan else "🌍 International"
        
        # Clean library name for display
        lib_display = library[:40] + ('...' if len(library) > 40 else '')
        
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{lib_display}</b><br>{lib_type} Library<br><b>{count} books</b> preserved<br>From: {', '.join(set(data['cities'][:5]))}{'...' if len(set(data['cities'])) > 5 else ''}",
            tooltip=f"{lib_display}: {count} books",
            icon=folium.Icon(color=icon_color, icon='book', prefix='fa')
        ).add_to(m)
    
    # Enhanced title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 650px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:15px; padding: 10px; opacity: 0.95;">
        <h3 style="margin: 0;">The "Book Road": China → Japan Migration</h3>
        <p style="margin: 5px 0; font-size: 13px;">
        🔵 Blue circles: Chinese publishing cities | 
        🔴 Red markers: Japanese libraries | 
        🟢 Green: Other libraries<br>
        Red lines: Books flowing to Japan | Orange: Other destinations
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(output_file)
    print(f"✓ Saved: {output_file}")
    print(f"  Chinese publisher cities: {df_network['City_Clean'].nunique()}")
    print(f"  Total libraries: {len(library_flows)}")
    print(f"  Japanese libraries: {sum(1 for lib in library_flows if any(k in lib for k in ['天理', '大阪', '龍谷', '東洋']))}")
    print(f"  Total book flows visualized: {len(df_network)}")
    
    return m


def create_thematic_map(df, output_file='thematic_map.html'):
    """
    Create regional specialization heatmaps by book category.
    Feature #3: Regional Specialization Heatmap
    """
    print(f"\n{'='*60}")
    print("Creating Thematic/Regional Specialization Maps")
    print(f"{'='*60}")
    
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Create separate heatmaps for each category
    categories = df['Category'].unique()
    colors = {
        'theology': {'color': 'red', 'name': 'Theology/Religious'},
        'history': {'color': 'blue', 'name': 'History/Travel'},
        'language': {'color': 'green', 'name': 'Language/Grammar'},
        'periodical': {'color': 'purple', 'name': 'Periodicals'},
        'general': {'color': 'gray', 'name': 'General'}
    }
    
    for category in categories:
        df_cat = df[df['Category'] == category]
        if len(df_cat) > 0:
            heat_data = [[row['Latitude'], row['Longitude']] for _, row in df_cat.iterrows()]
            
            HeatMap(
                heat_data,
                name=colors.get(category, {}).get('name', category),
                min_opacity=0.2,
                max_opacity=0.7,
                radius=20,
                blur=25,
                gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1.0: 'red'}
            ).add_to(m)
            
            print(f"  {category}: {len(df_cat)} books")
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 600px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 10px; opacity: 0.9;">
        <h3 style="margin: 0;">Regional Specialization by Book Type</h3>
        <p style="margin: 5px 0;">Toggle layers to see which regions specialized in different types of literature</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(output_file)
    print(f"✓ Saved: {output_file}")
    
    return m


def create_publisher_map(df, output_file='publisher_map.html'):
    """
    Create publisher distribution map sized by output and colored by longevity.
    Feature #4: Publisher Distribution & Longevity
    """
    print(f"\n{'='*60}")
    print("Creating Publisher Distribution Map")
    print(f"{'='*60}")
    
    # Aggregate by publisher
    publisher_stats = []
    for publisher in df['Publisher'].unique():
        if pd.notna(publisher):
            pub_data = df[df['Publisher'] == publisher]
            if pub_data['Coordinates'].notna().any():
                coords = pub_data[pub_data['Coordinates'].notna()].iloc[0]
                years = pub_data['Year_Final'].dropna()
                
                publisher_stats.append({
                    'publisher': publisher,
                    'lat': coords['Latitude'],
                    'lon': coords['Longitude'],
                    'city': coords['City_Clean'],
                    'count': len(pub_data),
                    'year_min': int(years.min()) if len(years) > 0 else None,
                    'year_max': int(years.max()) if len(years) > 0 else None,
                    'longevity': int(years.max() - years.min()) if len(years) > 1 else 0
                })
    
    df_publishers = pd.DataFrame(publisher_stats)
    
    if len(df_publishers) == 0:
        print("⚠️  No publisher data available")
        return None
    
    center_lat = df_publishers['lat'].mean()
    center_lon = df_publishers['lon'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Add publisher markers
    for _, pub in df_publishers.iterrows():
        # Circle size based on book count
        radius = 5 + pub['count'] * 2
        
        # Color based on longevity (red = longer history)
        if pub['longevity'] > 10:
            color = 'red'
        elif pub['longevity'] > 5:
            color = 'orange'
        else:
            color = 'blue'
        
        year_range = f"{pub['year_min']}-{pub['year_max']}" if pub['year_min'] and pub['year_max'] else "Unknown"
        
        folium.CircleMarker(
            location=[pub['lat'], pub['lon']],
            radius=radius,
            popup=f"<b>{pub['publisher']}</b><br>City: {pub['city']}<br>Books: {pub['count']}<br>Active: {year_range}<br>Longevity: {pub['longevity']} years",
            tooltip=pub['publisher'],
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 600px; height: 110px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 10px; opacity: 0.9;">
        <h3 style="margin: 0;">Publisher Distribution & Longevity</h3>
        <p style="margin: 5px 0;">Circle size = number of books | Color: Blue (new) → Orange → Red (long-established)</p>
        <small>Click circles for publisher details</small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(output_file)
    print(f"✓ Saved: {output_file}")
    print(f"  Total publishers: {len(df_publishers)}")
    print(f"  Top publisher: {df_publishers.nlargest(1, 'count').iloc[0]['publisher']} ({df_publishers.nlargest(1, 'count').iloc[0]['count']} books)")
    
    return m


def create_network_analysis(df, output_prefix='network'):
    """
    Create network analysis visualizations.
    Feature #5: Network Analysis (co-publishing, author-publisher, etc.)
    """
    print(f"\n{'='*60}")
    print("Creating Network Analysis")
    print(f"{'='*60}")
    
    # 1. City-to-City Network (books flowing between publishing and preservation)
    G_cities = nx.Graph()
    
    df_flow = df[(df['Coordinates'].notna()) & (df['Library_Coords'].notna())]
    for _, row in df_flow.iterrows():
        if row['City_Clean'] and row['Library']:
            G_cities.add_edge(row['City_Clean'], row['Library'], weight=1)
    
    if len(G_cities.edges()) > 0:
        print(f"  City network: {len(G_cities.nodes())} nodes, {len(G_cities.edges())} edges")
    
    # 2. Publisher Network (publishers in same city)
    G_publishers = nx.Graph()
    
    for city in df['City_Clean'].unique():
        if pd.notna(city):
            publishers = df[df['City_Clean'] == city]['Publisher'].dropna().unique()
            if len(publishers) > 1:
                for i, pub1 in enumerate(publishers):
                    for pub2 in publishers[i+1:]:
                        G_publishers.add_edge(pub1, pub2, city=city)
    
    if len(G_publishers.edges()) > 0:
        print(f"  Publisher co-location network: {len(G_publishers.nodes())} nodes, {len(G_publishers.edges())} edges")
    
    # Save network statistics
    with open(f'{output_prefix}_stats.txt', 'w', encoding='utf-8') as f:
        f.write("NETWORK ANALYSIS RESULTS\n")
        f.write("="*60 + "\n\n")
        
        f.write("1. City-to-Library Network\n")
        f.write(f"   Nodes: {len(G_cities.nodes())}\n")
        f.write(f"   Edges: {len(G_cities.edges())}\n")
        if len(G_cities.nodes()) > 0:
            f.write(f"   Density: {nx.density(G_cities):.4f}\n")
        
        f.write("\n2. Publisher Co-location Network\n")
        f.write(f"   Nodes: {len(G_publishers.nodes())}\n")
        f.write(f"   Edges: {len(G_publishers.edges())}\n")
        if len(G_publishers.nodes()) > 0:
            f.write(f"   Density: {nx.density(G_publishers):.4f}\n")
    
    print(f"✓ Saved network statistics: {output_prefix}_stats.txt")
    
    return G_cities, G_publishers


def create_enhanced_basic_map(df, output_file='index.html'):
    """
    Create the enhanced basic map (like original but with improvements).
    """
    print(f"\n{'='*60}")
    print("Creating Enhanced Basic Map")
    print(f"{'='*60}")
    
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles='OpenStreetMap')
    
    # Add marker cluster
    marker_cluster = MarkerCluster(name='Books').add_to(m)
    
    # Add markers
    for idx, row in df.iterrows():
        popup_html = f"""
        <div style="width: 350px;">
            <h4>{row['Title']}</h4>
            <p><b>Author:</b> {row['Author']}</p>
            <p><b>Publisher:</b> {row['Publisher']}</p>
            <p><b>City:</b> {row['City_Clean']}</p>
            <p><b>Year:</b> {int(row['Year_Final']) if pd.notna(row['Year_Final']) else 'Unknown'}</p>
            <p><b>Category:</b> {row['Category']}</p>
            {f"<p><b>Library:</b> {row['Library']}</p>" if pd.notna(row['Library']) else ""}
        </div>
        """
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=row['Title'][:50] + ('...' if len(row['Title']) > 50 else ''),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)
    
    # Add heatmap
    heat_data = [[row['Latitude'], row['Longitude']] for idx, row in df.iterrows()]
    HeatMap(
        heat_data,
        name='Publishing Density',
        min_opacity=0.3,
        max_opacity=0.8,
        radius=25,
        blur=35,
        gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1.0: 'red'}
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    # Enhanced title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 600px; height: 110px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 10px; opacity: 0.9;">
        <h3 style="margin: 0;">Interactive Digital Atlas (Enhanced)</h3>
        <p style="margin: 5px 0;">Islamic Books in Chinese - Publishing Locations</p>
        <small>Toggle layers | Click markers for details | Includes temporal & category data</small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(output_file)
    print(f"✓ Saved: {output_file}")
    
    return m


def main():
    """
    Main function to generate all advanced atlas visualizations.
    """
    print("\n" + "="*60)
    print("ADVANCED INTERACTIVE DIGITAL ATLAS GENERATOR")
    print("Islamic Books in Chinese - Comprehensive Analysis")
    print("="*60)
    
    try:
        # Find and read CSV
        csv_file = find_csv_file()
        df = read_and_process_csv(csv_file)
        
        if len(df) == 0:
            print("Error: No valid data found")
            return 1
        
        print(f"\n{'='*60}")
        print("DATA SUMMARY")
        print(f"{'='*60}")
        print(f"Total records processed: {len(df)}")
        print(f"Unique cities: {df['City_Clean'].nunique()}")
        print(f"Date range: {int(df['Year_Final'].min()) if df['Year_Final'].notna().any() else 'N/A'} - {int(df['Year_Final'].max()) if df['Year_Final'].notna().any() else 'N/A'}")
        print(f"Categories: {', '.join(df['Category'].value_counts().index.tolist())}")
        
        # Generate all visualizations
        print(f"\n{'='*60}")
        print("GENERATING VISUALIZATIONS")
        print(f"{'='*60}")
        
        create_enhanced_basic_map(df, 'index.html')
        create_temporal_map(df, 'temporal_map.html')
        create_network_map(df, 'network_map.html')
        create_thematic_map(df, 'thematic_map.html')
        create_publisher_map(df, 'publisher_map.html')
        create_network_analysis(df, 'network')
        
        print(f"\n{'='*60}")
        print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        print(f"{'='*60}")
        print("\nGenerated files:")
        print("  • index.html - Enhanced basic map with all data")
        print("  • temporal_map.html - Time-lapse showing publishing evolution")
        print("  • network_map.html - Publisher-to-library knowledge flows")
        print("  • thematic_map.html - Regional specialization by book type")
        print("  • publisher_map.html - Publisher distribution & longevity")
        print("  • network_stats.txt - Network analysis results")
        print("\nOpen any HTML file in your browser to explore the visualizations!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
