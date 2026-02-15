#!/usr/bin/env python3
"""
Ultra-Advanced Interactive Digital Atlas Generator
Fully utilizes ALL metadata from CSV + Excel + Word documents
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, TimestampedGeoJson
import networkx as nx
from pathlib import Path
import re
import json
from datetime import datetime
from docx import Document

# ============================================================
# GEOCODING DICTIONARY
# ============================================================
CITY_COORDINATES = {
    '北京': (39.9042, 116.4074), '北平': (39.9042, 116.4074),
    '上海': (31.2304, 121.4737),
    '天津': (39.3434, 117.3616),
    '成都': (30.5728, 104.0668), '錦江': (30.5728, 104.0668), '錦城': (30.5728, 104.0668), '蓉城': (30.5728, 104.0668),
    '南京': (32.0603, 118.7969),
    '長沙': (28.2282, 112.9388),
    '鎮江': (32.2109, 119.4552),
    '廣州': (23.1291, 113.2644),
    '瀋陽': (41.8057, 123.4328), '奉天': (41.8057, 123.4328),
    '昆明': (25.0389, 102.7183),
    '香港': (22.3193, 114.1694),
    '青海': (36.6171, 101.7782),
}

# Japanese library coordinates
LIBRARY_COORDINATES = {
    '天理大學': (34.5964, 135.8378),  # Tenri, Nara
    '大阪大學': (34.8207, 135.5228),  # Osaka
    '龍谷大學': (34.9673, 135.7696),  # Kyoto
    '東洋文庫': (35.7365, 139.7459),  # Tokyo
    '紐約公共圖書館': (40.7531, -73.9823),  # NYC
    '哈佛大學': (42.3770, -71.1167),  # Harvard
}

# ============================================================
# DATA LOADING
# ============================================================

def load_all_data():
    """Load and merge all data sources"""
    print("Loading all data sources...")
    
    # Main CSV
    csv_files = list(Path('.').glob('*.csv'))
    df_main = pd.read_csv(csv_files[0]) if csv_files else None
    
    # Excel files
    excel_files = [f for f in Path('.').glob('*.xlsx') if 'focus list' in f.name.lower()]
    df_excel_list = []
    for excel_file in excel_files:
        try:
            df = pd.read_excel(excel_file)
            df['source_file'] = excel_file.name
            df_excel_list.append(df)
            print(f"  Loaded {excel_file.name}: {len(df)} books, {len(df.columns)} columns")
        except Exception as e:
            print(f"  Error loading {excel_file.name}: {e}")
    
    df_excel = pd.concat(df_excel_list, ignore_index=True) if df_excel_list else None
    
    # Word documents (scholarly commentary)
    commentary = load_scholarly_commentary()
    
    return df_main, df_excel, commentary

def load_scholarly_commentary():
    """Extract scholarly commentary from Word documents"""
    commentary = {}
    word_files = list(Path('.').glob('*.docx'))
    
    for word_file in word_files:
        try:
            doc = Document(word_file)
            text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            
            # Parse commentary by book title
            # Split by book entries (titles typically at start of paragraphs)
            entries = re.split(r'\n\n+', text)
            for entry in entries:
                if len(entry) > 50:  # Meaningful content
                    # Try to extract book title (usually Chinese characters at start)
                    title_match = re.match(r'([^\n]+)', entry)
                    if title_match:
                        title = title_match.group(1).strip()
                        commentary[title] = entry
            
            print(f"  Loaded commentary from {word_file.name}: {len(commentary)} book entries")
        except Exception as e:
            print(f"  Error loading {word_file.name}: {e}")
    
    return commentary

# ============================================================
# DATA PROCESSING
# ============================================================

def parse_chinese_year(year_str):
    """Convert Chinese era names to Western years"""
    if pd.isna(year_str) or not isinstance(year_str, str):
        return None
    
    era_map = {
        '光緒': 1875, '宣統': 1909, '民國': 1912,
        '同治': 1862, '嘉慶': 1796, '道光': 1821,
        '咸豐': 1851
    }
    
    for era, base_year in era_map.items():
        if era in year_str:
            match = re.search(r'(\d+)年', year_str)
            if match:
                offset = int(match.group(1))
                return base_year + offset - 1
    
    return None

def categorize_book(title, publisher=''):
    """Categorize books by content type"""
    if pd.isna(title):
        return 'General'
    
    title_str = str(title).lower()
    pub_str = str(publisher).lower()
    
    theology_keywords = ['天方', '教義', '信仰', '清真', '教規', '經學', '教法', '教理', '伊斯蘭']
    language_keywords = ['詞典', '字典', '文法', '語法', '阿文', '阿拉伯', '波斯']
    history_keywords = ['歷史', '史略', '朝覲', '遊記', '傳記']
    periodical_keywords = ['報', '月刊', '週刊', '雜誌', '書報社']
    
    if any(kw in title_str for kw in periodical_keywords) or '書報社' in pub_str:
        return 'Periodical'
    if any(kw in title_str for kw in theology_keywords):
        return 'Theology'
    if any(kw in title_str for kw in language_keywords):
        return 'Language'
    if any(kw in title_str for kw in history_keywords):
        return 'History'
    
    return 'General'

def standardize_city(city_str):
    """Standardize city names"""
    if pd.isna(city_str):
        return None
    
    city_str = str(city_str)
    city_str = re.sub(r'\([^)]*\)', '', city_str)
    city_str = re.sub(r'市|省', '', city_str).strip()
    
    for standard_name in CITY_COORDINATES.keys():
        if standard_name in city_str:
            return standard_name
    
    return city_str if city_str else None

def extract_library_name(library_str):
    """Extract main library name"""
    if pd.isna(library_str):
        return None
    
    library_str = str(library_str)
    
    for lib_name in LIBRARY_COORDINATES.keys():
        if lib_name[:3] in library_str:  # Match first 3 chars
            return lib_name
    
    return library_str.split('圖書館')[0] + '圖書館' if '圖書館' in library_str else library_str

# ============================================================
# PREFACE NETWORK ANALYSIS
# ============================================================

def build_preface_network(df_excel):
    """Build intellectual network from preface authors"""
    G = nx.DiGraph()
    
    for _, row in df_excel.iterrows():
        book_author = row.get('著者/編者\n Author/Editor', '')
        book_title = row.get('題名\n Title', '')
        book_city = standardize_city(row.get('出版城市\n City', ''))
        
        if pd.notna(book_author) and book_author.strip():
            G.add_node(book_author, type='author', city=book_city, title=book_title)
        
        # Add preface authors (up to 4)
        for i in range(1, 5):
            pref_author_col = f'Pref {i} author'
            pref_city_col = f'Pref {i} City'
            pref_date_col = f'Pref {i} date'
            
            if pref_author_col in df_excel.columns:
                pref_author = row.get(pref_author_col, '')
                if pd.notna(pref_author) and pref_author.strip():
                    pref_city = standardize_city(row.get(pref_city_col, ''))
                    pref_date = row.get(pref_date_col, '')
                    
                    G.add_node(pref_author, type='preface_author', city=pref_city)
                    G.add_edge(pref_author, book_author, 
                              relationship='wrote_preface_for',
                              book_title=book_title,
                              date=pref_date)
        
        # Add postface author
        if 'Postface author' in df_excel.columns:
            postf_author = row.get('Postface author', '')
            if pd.notna(postf_author) and postf_author.strip():
                postf_city = standardize_city(row.get('Postface city', ''))
                G.add_node(postf_author, type='postface_author', city=postf_city)
                G.add_edge(postf_author, book_author,
                          relationship='wrote_postface_for',
                          book_title=book_title)
    
    return G

# ============================================================
# VISUALIZATION GENERATION
# ============================================================

def create_preface_network_map(df_excel, output_file='preface_network_map.html'):
    """Create map of preface author intellectual networks"""
    print(f"\nCreating preface network map: {output_file}")
    
    G = build_preface_network(df_excel)
    print(f"  Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    m = folium.Map(location=[35, 110], zoom_start=4, tiles='CartoDB positron')
    
    # Add nodes (authors) to map
    for node, data in G.nodes(data=True):
        city = data.get('city')
        if city and city in CITY_COORDINATES:
            coords = CITY_COORDINATES[city]
            node_type = data.get('type', 'author')
            
            color = {'author': 'blue', 'preface_author': 'green', 'postface_author': 'orange'}[node_type]
            
            folium.CircleMarker(
                location=coords,
                radius=8,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                popup=f"<b>{node}</b><br>Type: {node_type}<br>City: {city}"
            ).add_to(m)
    
    # Add edges (preface relationships)
    for u, v, data in G.edges(data=True):
        u_city = G.nodes[u].get('city')
        v_city = G.nodes[v].get('city')
        
        if u_city and v_city and u_city in CITY_COORDINATES and v_city in CITY_COORDINATES:
            coords_u = CITY_COORDINATES[u_city]
            coords_v = CITY_COORDINATES[v_city]
            
            folium.PolyLine(
                locations=[coords_u, coords_v],
                color='green',
                weight=2,
                opacity=0.5,
                popup=f"{u} → {v}<br>{data.get('relationship', '')}"
            ).add_to(m)
    
    m.save(output_file)
    print(f"  ✓ Saved: {output_file}")

def create_physical_book_analysis_map(df_excel, output_file='physical_books_map.html'):
    """Create map analyzing physical book characteristics"""
    print(f"\nCreating physical book analysis map: {output_file}")
    
    m = folium.Map(location=[35, 110], zoom_start=4, tiles='CartoDB positron')
    
    for _, row in df_excel.iterrows():
        city = standardize_city(row.get('出版城市\n City', ''))
        if not city or city not in CITY_COORDINATES:
            continue
        
        coords = CITY_COORDINATES[city]
        
        # Extract physical metrics
        pages = row.get('# of pages', 0)
        folia = row.get('# of folia', 0)
        juan = row.get('# of juan', 0)
        has_advert = row.get('Advert yes/no', '')
        num_prefaces = row.get('# of Pref', 0)
        
        # Calculate size (radius) - handle string/numeric conversion
        try:
            pages_num = pd.to_numeric(pages, errors='coerce')
            folia_num = pd.to_numeric(folia, errors='coerce')
            juan_num = pd.to_numeric(juan, errors='coerce')
            
            size_metric = (pages_num if pd.notna(pages_num) and pages_num > 0 else 
                          folia_num if pd.notna(folia_num) and folia_num > 0 else 
                          juan_num * 50 if pd.notna(juan_num) and juan_num > 0 else 50)
            radius = min(max(float(size_metric) / 10, 5), 30)
        except:
            radius = 10
        
        # Color by commercial vs scholarly
        is_commercial = str(has_advert).lower() in ['yes', 'y', '是']
        color = 'red' if is_commercial else 'blue'
        
        title = row.get('題名\n Title', 'Unknown')
        author = row.get('著者/編者\n Author/Editor', 'Unknown')
        
        popup_html = f"""
        <b>{title}</b><br>
        Author: {author}<br>
        City: {city}<br>
        <hr>
        Physical Metrics:<br>
        - Pages: {pages if pd.notna(pages) else 'N/A'}<br>
        - Folia: {folia if pd.notna(folia) else 'N/A'}<br>
        - Juan: {juan if pd.notna(juan) else 'N/A'}<br>
        - Prefaces: {num_prefaces if pd.notna(num_prefaces) else '0'}<br>
        - Commercial: {'Yes (has ads)' if is_commercial else 'No'}
        """
        
        folium.CircleMarker(
            location=coords,
            radius=radius,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.5,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    
    m.save(output_file)
    print(f"  ✓ Saved: {output_file}")

def create_collection_influence_map(df_excel, output_file='collection_influence_map.html'):
    """Map showing influence of major anthologies"""
    print(f"\nCreating collection influence map: {output_file}")
    
    m = folium.Map(location=[35, 110], zoom_start=4, tiles='CartoDB positron')
    
    # Count books per city by collection
    city_qd = {}  # Qingzhen Dadian
    city_hdq = {}  # Huizu Diancang Quanshu
    
    for _, row in df_excel.iterrows():
        city = standardize_city(row.get('出版城市\n City', ''))
        if not city or city not in CITY_COORDINATES:
            continue
        
        qd = str(row.get('清眞大典\n Qingzhen Dadian', '無'))
        hdq = str(row.get('回族典藏全書\n Huizu Diancang Quanshu', '無'))
        
        if qd != '無' and '無' not in qd and pd.notna(qd):
            city_qd[city] = city_qd.get(city, 0) + 1
        if hdq != '無' and '無' not in hdq and pd.notna(hdq):
            city_hdq[city] = city_hdq.get(city, 0) + 1
    
    print(f"  Qingzhen Dadian: {sum(city_qd.values())} books in {len(city_qd)} cities")
    print(f"  Huizu Diancang Quanshu: {sum(city_hdq.values())} books in {len(city_hdq)} cities")
    
    # Plot Qingzhen Dadian
    for city, count in city_qd.items():
        coords = CITY_COORDINATES[city]
        folium.CircleMarker(
            location=coords,
            radius=count * 3,
            color='darkblue',
            fill=True,
            fillColor='blue',
            fillOpacity=0.4,
            popup=f"<b>{city}</b><br>清眞大典: {count} books"
        ).add_to(m)
    
    # Plot Huizu Diancang Quanshu
    for city, count in city_hdq.items():
        coords = CITY_COORDINATES[city]
        folium.CircleMarker(
            location=[coords[0] + 0.2, coords[1] + 0.2],  # Offset slightly
            radius=count * 3,
            color='darkred',
            fill=True,
            fillColor='red',
            fillOpacity=0.4,
            popup=f"<b>{city}</b><br>回族典藏全書: {count} books"
        ).add_to(m)
    
    m.save(output_file)
    print(f"  ✓ Saved: {output_file}")

def create_enhanced_main_map(df_main, df_excel, commentary, output_file='index_ultra.html'):
    """Create ultra-enhanced main map with ALL metadata"""
    print(f"\nCreating ultra-enhanced main map: {output_file}")
    
    m = folium.Map(location=[35, 110], zoom_start=4, tiles='OpenStreetMap')
    
    marker_cluster = MarkerCluster().add_to(m)
    heatmap_data = []
    
    # Merge Excel data if available
    excel_lookup = {}
    if df_excel is not None:
        for _, row in df_excel.iterrows():
            title = row.get('題名\n Title', '')
            if pd.notna(title):
                excel_lookup[title] = row
    
    processed = 0
    for _, row in df_main.iterrows():
        city_raw = row.get(row.keys()[9] if len(row.keys()) > 9 else 'City', '')
        city = standardize_city(city_raw)
        
        if not city or city not in CITY_COORDINATES:
            continue
        
        coords = CITY_COORDINATES[city]
        heatmap_data.append(coords)
        
        title = row.get(row.keys()[4] if len(row.keys()) > 4 else 'Title', 'Unknown')
        author = row.get(row.keys()[7] if len(row.keys()) > 7 else 'Author', 'Unknown')
        publisher = row.get(row.keys()[10] if len(row.keys()) > 10 else 'Publisher', 'Unknown')
        year_raw = row.get(row.keys()[5] if len(row.keys()) > 5 else 'Year', '')
        year = parse_chinese_year(year_raw)
        category = categorize_book(title, publisher)
        
        # Get Excel enhanced data
        excel_data = excel_lookup.get(title, {})
        pages = excel_data.get('# of pages', 'N/A') if excel_data else 'N/A'
        folia = excel_data.get('# of folia', 'N/A') if excel_data else 'N/A'
        juan = excel_data.get('# of juan', 'N/A') if excel_data else 'N/A'
        num_pref = excel_data.get('# of Pref', 'N/A') if excel_data else 'N/A'
        has_advert = excel_data.get('Advert yes/no', 'N/A') if excel_data else 'N/A'
        qd = excel_data.get('清眞大典 Qingzhen Dadian', 'N/A') if excel_data else 'N/A'
        hdq = excel_data.get('回族典藏全書 Huizu Diancang Quanshu', 'N/A') if excel_data else 'N/A'
        
        # Get scholarly commentary
        book_commentary = ''
        for comm_title, comm_text in commentary.items():
            if title[:10] in comm_text or comm_title[:10] in str(title):
                book_commentary = comm_text[:500] + '...' if len(comm_text) > 500 else comm_text
                break
        
        popup_html = f"""
        <div style="width:400px">
        <h4>{title}</h4>
        <b>Author:</b> {author}<br>
        <b>Publisher:</b> {publisher}<br>
        <b>City:</b> {city}<br>
        <b>Year:</b> {year if year else 'Unknown'} ({year_raw})<br>
        <b>Category:</b> {category}<br>
        <hr>
        <b>Physical Details:</b><br>
        - Pages: {pages}<br>
        - Folia: {folia}<br>
        - Juan: {juan}<br>
        - Prefaces: {num_pref}<br>
        - Commercial: {has_advert}<br>
        <hr>
        <b>Collections:</b><br>
        - 清眞大典: {qd}<br>
        - 回族典藏全書: {hdq}<br>
        """
        
        if book_commentary:
            popup_html += f"<hr><b>Scholarly Commentary:</b><br><small>{book_commentary}</small>"
        
        popup_html += "</div>"
        
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=450),
            icon=folium.Icon(color='blue', icon='book', prefix='fa')
        ).add_to(marker_cluster)
        
        processed += 1
    
    # Add heatmap
    HeatMap(heatmap_data, name='Density Heatmap').add_to(m)
    folium.LayerControl().add_to(m)
    
    m.save(output_file)
    print(f"  ✓ Saved: {output_file} ({processed} books)")

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("=" * 60)
    print("ULTRA-ADVANCED INTERACTIVE DIGITAL ATLAS GENERATOR")
    print("Fully Utilizing ALL Metadata Sources")
    print("=" * 60)
    
    # Load all data
    df_main, df_excel, commentary = load_all_data()
    
    if df_main is None:
        print("ERROR: No CSV file found!")
        return
    
    print(f"\nData loaded:")
    print(f"  Main CSV: {len(df_main)} books")
    print(f"  Excel files: {len(df_excel) if df_excel is not None else 0} books")
    print(f"  Commentary: {len(commentary)} book entries")
    
    # Generate all visualizations
    if df_excel is not None and len(df_excel) > 0:
        create_preface_network_map(df_excel)
        create_physical_book_analysis_map(df_excel)
        create_collection_influence_map(df_excel)
    else:
        print("\n⚠ Skipping Excel-based visualizations (no data)")
    
    create_enhanced_main_map(df_main, df_excel, commentary)
    
    print("\n" + "=" * 60)
    print("✓ ALL ULTRA-ADVANCED VISUALIZATIONS GENERATED")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - index_ultra.html (Ultra-enhanced main map with ALL metadata)")
    print("  - preface_network_map.html (Intellectual endorsement networks)")
    print("  - physical_books_map.html (Book size/complexity analysis)")
    print("  - collection_influence_map.html (Anthology influence)")
    print("\n")

if __name__ == '__main__':
    main()
