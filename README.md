# Interactive Digital Atlas - Islamic Books in Chinese

This project generates an interactive map visualization of Islamic books published in Chinese, showing their publishing locations across China.

## Features

- **Interactive Map**: Built with Folium/Leaflet for smooth navigation and zooming
- **Marker Clusters**: Individual book locations with detailed popups showing:
  - Book Title
  - Author/Editor
  - Publisher
  - City
- **Heatmap Layer**: Visualizes the density of publishing activities across regions
- **Layer Control**: Toggle between marker clusters and heatmap views
- **City Standardization**: Automatically maps historical city names to modern equivalents:
  - 北平 (Beiping) → 北京 (Beijing)
  - 錦江/錦城/蓉城 → 成都 (Chengdu)
  - 奉天 → 瀋陽 (Shenyang)
  - And more...

## Requirements

- Python 3.8 or higher
- pandas >= 2.0.0
- folium >= 0.14.0

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Simply run the generator script:

```bash
python generate_atlas.py
```

The script will:
1. Automatically detect the CSV file in the current directory
2. Process and clean the data
3. Geocode city locations using a built-in dictionary
4. Generate an interactive map
5. Save the result as `index.html`

Open `index.html` in any modern web browser to view the Interactive Digital Atlas.

## Data Source

The project uses the CSV file containing information about Islamic books published in Chinese, including:
- Book titles and authors
- Publishing dates and locations
- Publishers and library holdings

## Output

The generated `index.html` file includes:
- **185 books** visualized across **12 unique cities**
- Interactive markers with detailed information
- Heatmap showing publishing density
- Responsive design that works on desktop and mobile

## Technical Details

### Geocoding

The script uses a built-in dictionary of Chinese city coordinates for stable and reliable geocoding. This approach ensures:
- No external API dependencies
- Fast processing
- Consistent results

### City Name Standardization

The script handles various historical and alternative city names:
- Historical names (北平 for Beijing, 奉天 for Shenyang)
- Alternative names (錦江, 錦城, 蓉城 all refer to Chengdu)
- Cities with multiple entries in the same field
- Cities with annotations in parentheses

## Project Structure

```
.
├── requirements.txt              # Python dependencies
├── generate_atlas.py            # Main script to generate the atlas
├── index.html                   # Generated interactive map (output)
├── ‎⁨قائمة الكتب الإسلامية باللغة الصينية (1)⁩.csv  # Source data
└── README.md                    # This file
```

## License

This project is created for educational and research purposes.

## Screenshot

![Interactive Digital Atlas Preview](https://github.com/user-attachments/assets/b1f71356-c3cb-4094-9724-3c2bbb07c6f2)

*Note: The screenshot shows the atlas header. When opened in a browser with internet access, the full interactive map with markers and heatmap will be displayed.*
