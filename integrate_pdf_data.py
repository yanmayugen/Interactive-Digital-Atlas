#!/usr/bin/env python3
"""
PDF Data Integration Module
Integrates OCR-extracted PDF catalog data with existing book records
"""

import json
import pandas as pd
import re
from difflib import SequenceMatcher

def load_pdf_data():
    """Load OCR-extracted PDF data"""
    try:
        with open('pdf_extracted_data.json', 'r', encoding='utf-8') as f:
            pdf_data = json.load(f)
        return pdf_data
    except FileNotFoundError:
        print("Warning: PDF extracted data not found")
        return None

def parse_catalog_entries(pdf_text):
    """
    Parse bibliographic entries from OCR text
    Returns list of parsed catalog entries
    """
    entries = []
    
    # Split text into potential entries (lines with years/call numbers)
    lines = pdf_text.split('\n')
    
    current_entry = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for year patterns (691, 69T = Showa era, etc.)
        year_match = re.search(r'["\']?6[09][1-9T]', line)
        if year_match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                'raw_line': line,
                'year_code': year_match.group(),
                'text': line
            }
        elif current_entry:
            # Append to current entry
            current_entry['text'] += ' ' + line
    
    if current_entry:
        entries.append(current_entry)
    
    return entries

def match_pdf_to_csv(pdf_entries, csv_data):
    """
    Match PDF catalog entries to CSV records
    Returns enhanced CSV dataframe
    """
    matches = []
    
    for idx, row in csv_data.iterrows():
        best_match = None
        best_score = 0
        
        title = str(row.get('书名', '')).strip()
        if not title:
            continue
            
        # Try to match against PDF entries
        for entry in pdf_entries:
            entry_text = entry.get('text', '')
            # Calculate similarity
            score = SequenceMatcher(None, title, entry_text).ratio()
            
            if score > best_score:
                best_score = score
                best_match = entry
        
        # If good match found, add PDF confirmation
        if best_match and best_score > 0.3:  # 30% similarity threshold
            matches.append({
                'csv_index': idx,
                'pdf_entry': best_match,
                'confidence': best_score
            })
    
    return matches

def enhance_records_with_pdf(csv_data, pdf_matches):
    """
    Add PDF validation flags and metadata to CSV records
    """
    csv_data['pdf_confirmed'] = False
    csv_data['pdf_confidence'] = 0.0
    csv_data['pdf_catalog_entry'] = ''
    
    for match in pdf_matches:
        idx = match['csv_index']
        csv_data.at[idx, 'pdf_confirmed'] = True
        csv_data.at[idx, 'pdf_confidence'] = match['confidence']
        csv_data.at[idx, 'pdf_catalog_entry'] = match['pdf_entry'].get('raw_line', '')[:200]
    
    return csv_data

def integrate_pdf_data_main():
    """
    Main integration function
    Loads PDF data and enhances CSV records
    """
    print("="*60)
    print("PDF Data Integration")
    print("="*60)
    
    # Load PDF data
    pdf_data = load_pdf_data()
    if not pdf_data:
        print("No PDF data available for integration")
        return None
    
    print(f"PDF Data: {pdf_data['total_characters']} characters from {pdf_data['pages']} pages")
    
    # Parse catalog entries
    full_text = pdf_data.get('full_text', '')
    catalog_entries = parse_catalog_entries(full_text)
    print(f"Parsed: {len(catalog_entries)} potential catalog entries")
    
    # Load CSV data
    import glob
    csv_files = sorted(glob.glob('*.csv'))
    if not csv_files:
        print("No CSV files found")
        return None
    
    csv_file = csv_files[0]
    print(f"Loading: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
    except:
        df = pd.read_csv(csv_file, encoding='gbk')
    
    print(f"CSV Records: {len(df)}")
    
    # Match PDF entries to CSV records
    matches = match_pdf_to_csv(catalog_entries, df)
    print(f"Matches Found: {len(matches)}")
    
    # Enhance records
    enhanced_df = enhance_records_with_pdf(df, matches)
    
    # Save enhanced data
    enhanced_file = 'enhanced_data_with_pdf.csv'
    enhanced_df.to_csv(enhanced_file, index=False, encoding='utf-8-sig')
    print(f"✓ Saved enhanced data: {enhanced_file}")
    
    # Statistics
    confirmed = enhanced_df['pdf_confirmed'].sum()
    total = len(enhanced_df)
    print(f"\nIntegration Statistics:")
    print(f"  - Total books: {total}")
    print(f"  - PDF confirmed: {confirmed} ({confirmed/total*100:.1f}%)")
    print(f"  - Average confidence: {enhanced_df[enhanced_df['pdf_confirmed']]['pdf_confidence'].mean():.2f}")
    
    print("="*60)
    
    return enhanced_df

if __name__ == '__main__':
    integrate_pdf_data_main()
