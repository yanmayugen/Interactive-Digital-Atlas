#!/usr/bin/env python3
"""
PDF OCR Data Extraction
Extracts bibliographic data from Tenri University catalog PDF using OCR
"""

import re
import json
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

def ocr_pdf(pdf_path):
    """
    Convert PDF to images and extract text using OCR
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of extracted text strings, one per page
    """
    print(f"Converting PDF to images: {pdf_path}")
    
    # Convert PDF to images
    try:
        images = convert_from_path(pdf_path, dpi=300)
        print(f"✓ Converted {len(images)} pages to images")
    except Exception as e:
        print(f"✗ Error converting PDF: {e}")
        return []
    
    # Extract text from each page using OCR
    extracted_pages = []
    for i, image in enumerate(images, 1):
        print(f"Processing page {i}/{len(images)}...")
        try:
            # Perform OCR with Japanese language support
            text = pytesseract.image_to_string(image, lang='jpn+eng+chi_sim')
            extracted_pages.append(text)
            print(f"✓ Extracted {len(text)} characters from page {i}")
        except Exception as e:
            print(f"✗ Error on page {i}: {e}")
            # Try with default language if Japanese fails
            try:
                text = pytesseract.image_to_string(image)
                extracted_pages.append(text)
                print(f"✓ Extracted {len(text)} characters from page {i} (default language)")
            except:
                extracted_pages.append("")
    
    return extracted_pages

def clean_ocr_text(text):
    """
    Clean OCR text by removing common OCR errors and normalizing whitespace
    
    Args:
        text: Raw OCR text
        
    Returns:
        Cleaned text
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove common OCR artifacts
    text = text.replace('|', 'I')
    text = text.replace('0', 'O')  # When in non-numeric context
    
    return text

def extract_bibliographic_entries(pages_text):
    """
    Extract bibliographic entries from OCR text
    
    Args:
        pages_text: List of text strings from each page
        
    Returns:
        List of dictionaries containing extracted book metadata
    """
    entries = []
    combined_text = "\n\n=== PAGE BREAK ===\n\n".join(pages_text)
    
    # Clean the text
    cleaned_text = clean_ocr_text(combined_text)
    
    # Try to identify bibliographic patterns
    # This is a basic extraction - adjust based on actual PDF structure
    lines = cleaned_text.split('\n')
    
    current_entry = {}
    for line in lines:
        line = line.strip()
        if not line or line == "=== PAGE BREAK ===":
            if current_entry:
                entries.append(current_entry)
                current_entry = {}
            continue
        
        # Look for common bibliographic markers
        if re.search(r'\d{4}', line):  # Year pattern
            current_entry['year_line'] = line
        
        # Look for Japanese/Chinese characters (potential titles)
        if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', line):
            if 'title_line' not in current_entry:
                current_entry['title_line'] = line
            elif 'additional_info' not in current_entry:
                current_entry['additional_info'] = line
    
    if current_entry:
        entries.append(current_entry)
    
    return entries, cleaned_text

def main():
    """Main extraction function"""
    print("=" * 60)
    print("PDF OCR Data Extraction")
    print("Tenri University Catalog - Bibliographic Data")
    print("=" * 60)
    
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("✗ No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]
    print(f"\nFound PDF: {pdf_path}")
    
    # Extract text using OCR
    pages_text = ocr_pdf(pdf_path)
    
    if not pages_text:
        print("\n✗ No text extracted from PDF")
        return
    
    print(f"\n✓ Successfully extracted text from {len(pages_text)} pages")
    print(f"Total characters extracted: {sum(len(p) for p in pages_text)}")
    
    # Extract bibliographic entries
    print("\nExtracting bibliographic entries...")
    entries, full_text = extract_bibliographic_entries(pages_text)
    
    print(f"✓ Extracted {len(entries)} potential entries")
    
    # Save extracted data
    output = {
        'source': pdf_path,
        'pages': len(pages_text),
        'total_characters': sum(len(p) for p in pages_text),
        'entries': entries,
        'full_text': full_text,
        'pages_text': pages_text
    }
    
    # Save to JSON
    output_file = 'pdf_extracted_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved extracted data to: {output_file}")
    
    # Save full text to separate file
    text_file = 'pdf_extracted_text.txt'
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"✓ Saved full text to: {text_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Extraction Summary")
    print("=" * 60)
    print(f"PDF file: {pdf_path}")
    print(f"Pages processed: {len(pages_text)}")
    print(f"Total characters: {sum(len(p) for p in pages_text):,}")
    print(f"Potential entries: {len(entries)}")
    print(f"Output files: {output_file}, {text_file}")
    print("=" * 60)
    
    # Print first few entries as sample
    if entries:
        print("\nSample Entries (first 3):")
        for i, entry in enumerate(entries[:3], 1):
            print(f"\nEntry {i}:")
            for key, value in entry.items():
                print(f"  {key}: {value[:100]}..." if len(value) > 100 else f"  {key}: {value}")

if __name__ == "__main__":
    main()
