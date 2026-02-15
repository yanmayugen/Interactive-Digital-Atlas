# Interactive Digital Atlas of Islamic Books in Chinese

**English Version | 英文版本**

## Overview

This project is a comprehensive GIS-based interactive digital atlas visualizing Islamic books published in Chinese during the 19th and 20th centuries. It combines spatiotemporal analysis, network visualization, and digital humanities research methodologies to reveal historical patterns in Islamic scholarly publishing in China.

## Quick Start

1. **View the Unified Dashboard**: Open `dashboard.html` in your web browser
2. **Navigate between visualizations**: Click on any map card to explore specific aspects
3. **All maps work offline**: No internet connection required after downloading

## 9 Interactive Visualizations

### 1. Enhanced Basic Map (`index.html`)
- **What**: Comprehensive overview with all 185 geocoded books
- **Features**: Interactive marker clusters, density heatmap, detailed metadata
- **Use case**: General exploration and overview of publishing locations

### 2. Temporal Evolution Map (`temporal_map.html`)
- **What**: Time-lapse visualization from 1863-1943 with interactive slider
- **Features**: 144 books with parsed temporal data, era-based transitions
- **Use case**: Understanding how publishing centers shifted over 80 years

### 3. Regional Specialization Map (`thematic_map.html`)
- **What**: Thematic heatmaps by book category
- **Features**: 4 category layers (Theology: 109, Language: 13, History: 1, General: 62)
- **Use case**: Analyzing regional intellectual specialization

### 4. Publisher Distribution Map (`publisher_map.html`)
- **What**: 50 publishers mapped and analyzed
- **Features**: Circle size = book count, color = longevity
- **Use case**: Identifying institutional powerhouses of Islamic printing

### 5. China→Japan Migration Network (`network_map.html`)
- **What**: "The Book Road" showing knowledge migration
- **Features**: 12 Chinese cities → 10 Japanese libraries, flow lines
- **Use case**: Visualizing how 95% of books ended up in Japanese collections

### 6. Ultra-Enhanced Map (`index_ultra.html`)
- **What**: Expert-curated data with 58 metadata fields
- **Features**: Preface networks, physical metrics, scholarly commentary
- **Use case**: In-depth analysis with all available metadata

### 7. Preface Author Networks (`preface_network_map.html`)
- **What**: Intellectual endorsement networks
- **Features**: 5 preface authors, 4 endorsement relationships
- **Use case**: Understanding scholarly prestige networks

### 8. Physical Book Analysis (`physical_books_map.html`)
- **What**: Book size and complexity analysis
- **Features**: Pages, folia, chapters, commercial indicators
- **Use case**: Publishing economics and book production patterns

### 9. Collection Influence Map (`collection_influence_map.html`)
- **What**: Impact of major anthologies
- **Features**: 清眞大典 (139 books), 回族典藏全書 (182 books)
- **Use case**: Tracking anthology influence across regions

## Key Historical Insights

### 🇯🇵 Japanese Preservation
95% of all books (234 out of 246) are preserved in Japanese academic institutions, with 天理大學 (Tenri University) holding the largest collection (195 books).

### 📍 Beijing Dominance
Beijing published 120 books (65% of total), led by 清眞書報社 (Qingzhen Shubao She), demonstrating the capital's central role in Islamic scholarly publishing.

### ⏰ Temporal Shift
Clear transition from traditional centers (Yunnan, Sichuan) to modern urban hubs (Beijing, Shanghai) during the Republic era, reflecting broader modernization trends in China.

### 🎓 Regional Specialization
- Beijing: Periodicals and newspapers
- Yunnan/Sichuan: Deep theological manuscripts

### 🔗 Publisher Concentration
Network analysis reveals high co-location density (0.172), indicating a concentrated publishing ecosystem with strong geographic clustering.

## Data Sources

### Main CSV (247 books, 23 columns)
- Title, Author, Publisher, Year, City, Library location
- Chinese era names, Hijri calendar dates
- Collection membership data

### Expert Excel Files (78 books, 58 columns)
- **Hai Peng collection**: 39 books with detailed metadata
- **Rian Thum collection**: 39 books with scholarly annotations
- Preface/postface networks (up to 4 prefaces per book)
- Physical metrics (pages, folia, juan/chapters)
- Commercial indicators (advertisement presence)
- Variant character tracking
- Multiple library holdings

### Word Documents (~12,000 characters)
- **18 books** with detailed scholarly commentary
- Themes and religious significance
- Content summaries and textual analysis
- Historical context and social impact
- Pricing and commercial details

### Tenri University PDF Catalog (5 pages)
- Reference document for catalog system
- Image-based PDF (used as documentation reference)

## Network Analysis Results

- **Publisher co-location network**: 48 nodes, 194 edges
- **Network density**: 0.172 (concentrated ecosystem)
- **Geographic networks**: 22 nodes, 37 edges
- **Preface networks**: 5 authors, 4 endorsement relationships

## Technical Details

### Technologies Used
- **Folium**: Interactive web maps with Python
- **NetworkX**: Network graph analysis
- **Pandas**: Data processing and analysis
- **OpenStreetMap**: Base map tiles
- **Python-docx & openpyxl**: Document parsing

### Data Processing Features
- City name standardization (北平→北京, etc.)
- Chinese era name parsing (民國8年→1919)
- Automatic category detection
- Built-in geocoding (27 city name variations)
- Network graph construction and analysis

## Usage Instructions

### Generate All Visualizations

```bash
# Install dependencies
pip install -r requirements.txt

# Generate basic map
python generate_atlas.py

# Generate advanced visualizations (5 maps)
python generate_atlas_advanced.py

# Generate ultra-advanced visualizations (complete dataset)
python generate_atlas_ultra.py

# Generate unified dashboard
python generate_final_dashboard.py
```

### View Maps

1. **Local viewing**: Double-click any HTML file to open in your web browser
2. **GitHub Pages**: Enable in repository settings for web hosting
3. **Dashboard**: Open `dashboard.html` for unified access to all maps

## Project Structure

```
├── dashboard.html                     # Unified interface (English)
├── index.html                         # Enhanced basic map
├── temporal_map.html                  # Time-lapse visualization
├── thematic_map.html                  # Regional specialization
├── publisher_map.html                 # Publisher distribution
├── network_map.html                   # China→Japan migration
├── index_ultra.html                   # Ultra-enhanced with 58 fields
├── preface_network_map.html           # Intellectual networks
├── physical_books_map.html            # Physical book analysis
├── collection_influence_map.html      # Anthology influence
├── generate_atlas.py                  # Basic generator
├── generate_atlas_advanced.py         # Advanced generator
├── generate_atlas_ultra.py            # Ultra-advanced generator
├── generate_final_dashboard.py        # Dashboard generator
├── requirements.txt                   # Python dependencies
├── ENGLISH_README.md                  # This file (English)
├── README_ADVANCED.md                 # Technical documentation
└── VISUALIZATION_GUIDE.md             # Complete visualization guide
```

## Data Statistics

- **Total books**: 247
- **Geocoded books**: 185 (75%)
- **Books with temporal data**: 144 (58%)
- **Publishing cities**: 12 (across China)
- **Japanese libraries**: 10 (holding 95% of books)
- **Time period**: 1863-1943 (80 years)
- **Publishers analyzed**: 50
- **Expert-curated books**: 78 (with 58 metadata fields)
- **Books with scholarly commentary**: 18

## Research Applications

### Digital Humanities
- Spatiotemporal analysis of intellectual production
- Network analysis of scholarly relationships
- Textual transmission and preservation studies

### Historical Geography
- Visualization of publishing center evolution
- Migration patterns of knowledge and texts
- Regional specialization in Islamic scholarship

### Book History
- Publishing economics and commercial patterns
- Institutional analysis of printing houses
- Physical book characteristics and production

### East Asian Islamic Studies
- China-Japan intellectual exchanges
- Preservation history of Islamic texts
- Regional variations in Islamic scholarship

## Citation

If you use this atlas in your research, please cite:

```
Interactive Digital Atlas of Islamic Books in Chinese (19th-20th Century)
Data sources: Tenri University, Osaka University, Tōyō Bunko
Visualization: Folium, NetworkX, Python
[Year]
```

## Contact & Support

For questions, bug reports, or feature requests, please open an issue in the GitHub repository.

## License

[Specify your license here]

---

**Note**: All visualizations are designed for English-speaking researchers and include bilingual Chinese/English labels where appropriate. The maps work offline and require only a web browser to view.
