#!/usr/bin/env python3
"""
Interactive Digital Atlas Generator for Islamic Books Data
Reads CSV data and creates an interactive map visualization with Folium
"""

import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap


# Built-in geocoding dictionary for Chinese cities
CITY_COORDINATES = {
    # Major cities
    '北京': (39.9042, 116.4074),
    '北平': (39.9042, 116.4074),  # Historical name for Beijing
    '上海': (31.2304, 121.4737),
    '天津': (39.3434, 117.3616),
    '南京': (32.0603, 118.7969),
    '成都': (30.5728, 104.0668),
    '錦江': (30.5728, 104.0668),  # District in Chengdu
    '錦城': (30.5728, 104.0668),  # Historical name for Chengdu
    '蓉城': (30.5728, 104.0668),  # Another name for Chengdu
    '長沙': (28.2282, 112.9388),
    '星沙': (28.2282, 112.9388),  # Area in Changsha
    '奉天': (41.8057, 123.4328),  # Historical name for Shenyang
    '瀋陽': (41.8057, 123.4328),
    '鎮江': (32.2109, 119.4552),
    '潤州': (32.2109, 119.4552),  # Historical name for Zhenjiang
    '京口': (32.2109, 119.4552),  # Another name for Zhenjiang
    '京江': (32.2109, 119.4552),  # Another name for Zhenjiang
    '雲南': (25.0406, 102.7125),  # Kunming, capital of Yunnan
    '滇省': (25.0406, 102.7125),  # Yunnan province
    '導河': (36.2988, 102.9883),  # Qinghai area
    '廣州': (23.1291, 113.2644),
    '粵東省城': (23.1291, 113.2644),  # Guangdong provincial capital
    '廣邑': (23.1291, 113.2644),  # Guangzhou area
    '香港': (22.3193, 114.1694),
    '燕湖': (39.9042, 116.4074),  # Near Beijing area
}


def find_csv_file():
    """
    Find the CSV file in the current directory.
    Tries to find any CSV file first, then falls back to data.csv
    """
    csv_files = sorted([f for f in os.listdir('.') if f.endswith('.csv')])
    
    if csv_files:
        # Use the first CSV file found (sorted for deterministic behavior)
        csv_file = csv_files[0]
        print(f"Found CSV file: {csv_file}")
        return csv_file
    elif os.path.exists('data.csv'):
        print("Using default: data.csv")
        return 'data.csv'
    else:
        raise FileNotFoundError("No CSV file found in the current directory")


def clean_city_name(city_str):
    """
    Clean and standardize city names.
    Handles multiple cities in one field and extracts the primary one.
    """
    if not city_str or pd.isna(city_str) or city_str.strip() == '？':
        return None
    
    city_str = city_str.strip()
    
    # Handle multiple cities separated by space
    if ' ' in city_str:
        # Take the first city
        city_str = city_str.split()[0]
    
    # Handle cities with annotations in parentheses
    if '（' in city_str:
        # Extract the main city name before parentheses
        city_str = city_str.split('（')[0].strip()
    
    # Standardize known variations
    standardization_map = {
        '北平': '北京',
        '錦江': '成都',
        '錦城': '成都',
        '蓉城': '成都',
        '星沙': '長沙',
        '潤州': '鎮江',
        '京口': '鎮江',
        '京江': '鎮江',
        '滇省': '雲南',
        '粵東省城': '廣州',
        '廣邑': '廣州',
        '奉天': '瀋陽',
        '燕湖': '北京',
    }
    
    if city_str in standardization_map:
        city_str = standardization_map[city_str]
    
    return city_str


def geocode_city(city_name):
    """
    Get coordinates for a city using the built-in dictionary.
    """
    if not city_name:
        return None
    
    return CITY_COORDINATES.get(city_name)


def read_and_process_csv(csv_file):
    """
    Read the CSV file and process the data.
    Returns a DataFrame with cleaned data and coordinates.
    """
    print(f"Reading CSV file: {csv_file}")
    
    # Read the CSV file
    df = pd.read_csv(csv_file, skiprows=[0])  # Skip the first empty row
    
    print(f"Total records: {len(df)}")
    
    # Extract relevant columns
    # Try to find columns by matching keywords in column names
    title_col = next((col for col in df.columns if 'Title' in str(col) or '題名' in str(col)), df.columns[2] if len(df.columns) > 2 else None)
    author_col = next((col for col in df.columns if 'Author' in str(col) or '著者' in str(col)), df.columns[4] if len(df.columns) > 4 else None)
    city_col = next((col for col in df.columns if 'City' in str(col) or '城市' in str(col)), df.columns[9] if len(df.columns) > 9 else None)
    publisher_col = next((col for col in df.columns if 'Publisher' in str(col) or '出版' in str(col)), df.columns[10] if len(df.columns) > 10 else None)
    
    columns_to_keep = {
        title_col: 'Title',
        author_col: 'Author',
        city_col: 'City',
        publisher_col: 'Publisher',
    }
    
    df_processed = df.rename(columns=columns_to_keep)[['Title', 'Author', 'City', 'Publisher']].copy()
    
    # Clean city names
    df_processed['City_Clean'] = df_processed['City'].apply(clean_city_name)
    
    # Filter out records without valid cities
    df_processed = df_processed[df_processed['City_Clean'].notna()].copy()
    
    print(f"Records with valid cities: {len(df_processed)}")
    
    # Geocode cities
    df_processed['Coordinates'] = df_processed['City_Clean'].apply(geocode_city)
    
    # Filter out records without coordinates
    df_processed = df_processed[df_processed['Coordinates'].notna()].copy()
    
    print(f"Records with geocoded cities: {len(df_processed)}")
    
    # Split coordinates into latitude and longitude
    df_processed['Latitude'] = df_processed['Coordinates'].apply(lambda x: x[0] if x else None)
    df_processed['Longitude'] = df_processed['Coordinates'].apply(lambda x: x[1] if x else None)
    
    return df_processed


def create_map(df):
    """
    Create an interactive Folium map with marker clusters and heatmap.
    """
    print("Creating interactive map...")
    
    # Calculate center of map (average of all coordinates)
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add marker cluster layer
    marker_cluster = MarkerCluster(name='Books').add_to(m)
    
    # Add markers for each book
    for idx, row in df.iterrows():
        popup_html = f"""
        <div style="width: 300px;">
            <h4>{row['Title']}</h4>
            <p><b>Author:</b> {row['Author']}</p>
            <p><b>Publisher:</b> {row['Publisher']}</p>
            <p><b>City:</b> {row['City_Clean']}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['Title'][:50] + ('...' if len(row['Title']) > 50 else ''),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)
    
    # Create heatmap data
    heat_data = [[row['Latitude'], row['Longitude']] for idx, row in df.iterrows()]
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        name='Publishing Density',
        min_opacity=0.3,
        max_opacity=0.8,
        radius=25,
        blur=35,
        gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1.0: 'red'}
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 500px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 10px; opacity: 0.9;">
        <h3 style="margin: 0;">Interactive Digital Atlas</h3>
        <p style="margin: 5px 0;">Islamic Books in Chinese - Publishing Locations</p>
        <small>Toggle layers in the top-right corner</small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    return m


def main():
    """
    Main function to generate the Interactive Digital Atlas.
    """
    print("=" * 60)
    print("Interactive Digital Atlas Generator")
    print("Islamic Books in Chinese - Publishing Locations")
    print("=" * 60)
    
    try:
        # Find CSV file
        csv_file = find_csv_file()
        
        # Read and process data
        df = read_and_process_csv(csv_file)
        
        if len(df) == 0:
            print("Error: No valid data found with geocoded cities.")
            return
        
        # Create map
        m = create_map(df)
        
        # Save map
        output_file = 'index.html'
        m.save(output_file)
        
        print("=" * 60)
        print(f"✓ Successfully generated: {output_file}")
        print(f"✓ Total books visualized: {len(df)}")
        print(f"✓ Unique cities: {df['City_Clean'].nunique()}")
        print("=" * 60)
        print(f"\nOpen {output_file} in your web browser to view the atlas.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
