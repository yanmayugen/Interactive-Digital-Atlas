# Interactive Digital Atlas - Islamic Books in Chinese (Advanced)

This project generates comprehensive interactive map visualizations of Islamic books published in Chinese, with advanced spatiotemporal analysis, network visualization, and thematic mapping.

## 🆕 Advanced Features

### 1. **Spatiotemporal Evolution (Time-Lapse Map)**
- Interactive time slider showing how publishing centers shifted from 1863-1943
- Reveals the transition from traditional centers (Yunnan, Nanjing) to modern urban hubs (Beijing, Shanghai)
- File: `temporal_map.html`

### 2. **Publisher-to-Library Network**
- Visualizes the migration of knowledge from publisher cities to preservation libraries
- Shows which regional collections ended up in international archives (Tokyo, New York, etc.)
- File: `network_map.html` (when library geocoding data is available)

### 3. **Regional Specialization (Thematic Mapping)**
- Separate heatmap layers for different book categories:
  - Theology/Religious texts
  - History/Travel accounts
  - Language/Grammar works
  - Periodicals
- Reveals intellectual geography and regional specializations
- File: `thematic_map.html`

### 4. **Publisher Distribution & Longevity**
- Interactive map of publishing houses sized by output
- Color-coded by longevity (blue = new, red = long-established)
- Identifies the "powerhouses" of Islamic printing in China
- File: `publisher_map.html`

### 5. **Network Analysis**
- Co-publishing networks showing publishers working in the same cities
- Geographic networks of city-to-city book flows
- Statistical analysis of network density and connectivity
- File: `network_stats.txt`

## Features

- **Interactive Map**: Built with Folium/Leaflet for smooth navigation
- **Marker Clusters**: Individual book locations with detailed popups
- **Heatmap Layers**: Visualizes publishing density by category
- **Temporal Data**: Books mapped across 80+ years of history
- **Network Graphs**: Publisher and geographic relationship analysis
- **City Standardization**: Handles historical names (北平→北京, 奉天→瀋陽, etc.)
- **Era Parsing**: Converts Chinese era names (民國8年→1919, 光緒25年→1899)

## Requirements

- Python 3.8 or higher
- pandas >= 2.0.0
- folium >= 0.14.0
- networkx >= 3.0.0
- plotly >= 5.0.0

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate All Visualizations (Advanced)

```bash
python generate_atlas_advanced.py
```

This creates:
- `index.html` - Enhanced basic map with all data
- `temporal_map.html` - Time-lapse evolution
- `thematic_map.html` - Regional specialization
- `publisher_map.html` - Publisher analysis
- `network_stats.txt` - Network statistics

### Generate Basic Map Only

```bash
python generate_atlas.py
```

Creates just `index.html` with marker clusters and density heatmap.

## Data Source

The project uses a comprehensive dataset of Islamic books published in Chinese, including:
- 185 books with geocoded locations
- Publication dates from 1863-1943 (Qing Dynasty through Republic era)
- 12 unique publishing cities across China
- 50+ publishers
- Multiple book categories (theology, history, language, periodicals)
- Library preservation information

## Output Visualizations

### Basic Map (`index.html`)
- 185 interactive markers with book details
- Density heatmap showing publishing concentrations
- Toggle-able layers

### Temporal Map (`temporal_map.html`)
- **Use the time slider** to watch publishing centers evolve
- See the shift from traditional to modern urban centers
- Decade-by-decade evolution from 1860s to 1940s

### Thematic Map (`thematic_map.html`)
- **Toggle layers** to see specialization by book type
- Beijing dominated periodicals and newspapers
- Traditional centers focused on theological manuscripts
- Historical and travel literature concentrated in specific regions

### Publisher Map (`publisher_map.html`)
- **Circle size** = number of books published
- **Color** = publisher longevity (blue→orange→red)
- Top publisher: 清眞書報社 with 97 books
- Shows the rise of institutional publishing houses

### Network Analysis (`network_stats.txt`)
- Publisher co-location network: 48 nodes, 194 edges
- Network density: 0.172
- Reveals collaboration patterns and geographic clusters

## Technical Implementation

### Geocoding
- Built-in coordinate dictionary for 27 Chinese city names and variations
- No external API dependencies - fully reproducible offline
- Handles historical place names and alternative spellings

### Temporal Processing
- Parses Chinese era names: 民國 (Republic), 光緒 (Guangxu), 咸豐 (Xianfeng), etc.
- Converts to Western calendar years for temporal analysis
- Covers Qing Dynasty through Republic of China era

### Categorization
- Automated book classification based on title keywords
- Categories: theology, history, language, periodical, general
- Enables thematic mapping and specialization analysis

### Network Analysis
- Uses NetworkX for graph construction and analysis
- Publisher co-location networks (publishers in same city)
- Geographic flow networks (publisher→library)
- Density and connectivity metrics

## Project Structure

```
.
├── requirements.txt                    # Python dependencies
├── generate_atlas.py                   # Basic map generator
├── generate_atlas_advanced.py          # Advanced features generator
├── generate_atlas_basic.py             # Backup of basic version
├── index.html                          # Enhanced basic map
├── temporal_map.html                   # Time-lapse visualization
├── thematic_map.html                   # Regional specialization
├── publisher_map.html                  # Publisher distribution
├── network_stats.txt                   # Network analysis results
├── ‎⁨قائمة الكتب الإسلامية باللغة الصينية (1)⁩.csv  # Source data
└── README.md                           # This file
```

## Data Statistics

- **Total Books**: 185 (with geocoded locations)
- **Date Range**: 1863-1943 (80 years)
- **Cities**: 12 unique locations
- **Publishers**: 50+ institutions
- **Top City**: Beijing with ~120 books (65%)
- **Categories**: Theology (109), General (62), Language (13), History (1)

## Historical Insights

### Publishing Evolution
- **1860s-1890s (Late Qing)**: Traditional centers in Yunnan, Sichuan
- **1900s-1910s**: Shift toward coastal cities (Shanghai, Nanjing)
- **1920s-1940s (Republic era)**: Beijing dominance (清眞書報社)

### Regional Specialization
- **Beijing**: Newspapers, periodicals, modern publishing
- **Yunnan/Sichuan**: Theological manuscripts, traditional texts
- **Shanghai**: Trade and commercial literature

### Publisher Networks
- High co-location density (0.172) indicates concentrated publishing ecosystem
- Major publishing houses sustained operations for 10-20+ years
- Beijing's 清眞書報社 was the dominant institutional publisher

## Future Enhancements

Potential additions:
- Historical geocoding of specific mosque/street addresses
- Author-publisher relationship networks
- Multilingual interface (Chinese/English/Arabic)
- Integration with digital book archives
- Comparative analysis with other religious publishing traditions

## License

This project is created for educational and research purposes.

## Citation

If you use this visualization in research, please cite:
```
Interactive Digital Atlas of Islamic Books in Chinese
GitHub: https://github.com/Isa123YS/gis
Data Source: [Original catalog source]
```
