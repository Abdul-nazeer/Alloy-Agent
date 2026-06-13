"""
Scrape equipment manual content from manufacturer websites
Saves as markdown for easier RAG ingestion
"""

import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

DEST_DIR = Path(__file__).parent.parent / "data" / "raw" / "manuals"
DEST_DIR.mkdir(parents=True, exist_ok=True)

def scrape_manualslib(url, filename):
    """Scrape manual content from ManualsLib"""
    print(f"Scraping: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find manual title
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else "Equipment Manual"
        
        # Find all pages link
        pages_link = soup.find('a', string=lambda t: t and 'Download' in t)
        if pages_link:
            # Try to get the "Read online" or "View" version instead
            view_link = soup.find('a', href=lambda h: h and '/manual/' in h and '/page-1' in h)
            if view_link:
                base_url = url.rsplit('/', 1)[0]
                return scrape_manualslib_pages(base_url, filename, title_text)
        
        # If can't get pages, just get the main content
        content_div = soup.find('div', class_='content') or soup.find('div', id='content')
        if content_div:
            text = content_div.get_text(separator='\n', strip=True)
            
            # Save as markdown
            markdown = f"# {title_text}\n\n"
            markdown += f"Source: {url}\n\n"
            markdown += text
            
            output_file = DEST_DIR / f"{filename}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"✓ Saved: {output_file.name} ({len(text)} chars)")
            return True
        else:
            print(f"⚠️  No content found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def scrape_manualslib_pages(base_url, filename, title):
    """Scrape multiple pages from ManualsLib manual"""
    print(f"  Scraping multi-page manual...")
    
    all_content = []
    page = 1
    max_pages = 50  # Limit to avoid infinite loops
    
    while page <= max_pages:
        try:
            url = f"{base_url}/page-{page}.html"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                break  # No more pages
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find page content
            page_content = soup.find('div', class_='page') or soup.find('div', class_='manual-page')
            if page_content:
                text = page_content.get_text(separator='\n', strip=True)
                all_content.append(f"\n## Page {page}\n\n{text}")
                print(f"    Page {page}: {len(text)} chars")
            else:
                break
            
            page += 1
            time.sleep(0.5)  # Be polite
            
        except Exception as e:
            print(f"    Stopped at page {page}: {e}")
            break
    
    if all_content:
        markdown = f"# {title}\n\n"
        markdown += f"Source: {base_url}\n"
        markdown += '\n'.join(all_content)
        
        output_file = DEST_DIR / f"{filename}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✓ Saved {page-1} pages: {output_file.name}")
        return True
    
    return False

def scrape_web_content(url, filename, title):
    """Generic web scraper for open content"""
    print(f"Scraping: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts, styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # Get main content
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_='content') or
            soup.body
        )
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
            
            markdown = f"# {title}\n\n"
            markdown += f"Source: {url}\n\n"
            markdown += text
            
            output_file = DEST_DIR / f"{filename}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"✓ Saved: {output_file.name} ({len(text)} chars)")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def main():
    """Scrape all target manuals"""
    print("="*60)
    print("SCRAPING EQUIPMENT MANUALS")
    print("="*60)
    
    manuals = [
        {
            'url': 'http://www.manualslib.com/manual/1710834/Abb-Mt-Series.html',
            'filename': 'abb_mt_series_motor_manual',
            'title': 'ABB MT Series Motor Installation & Maintenance Manual',
            'type': 'manualslib'
        },
        {
            'url': 'https://www.manualslib.com/manual/2930328/Parker-Greer-Ba-Series.html',
            'filename': 'parker_hydraulic_ba_series_manual',
            'title': 'Parker Greer BA Series Hydraulic Maintenance Manual',
            'type': 'manualslib'
        },
        {
            'url': 'http://www.manualslib.com/manual/1913649/Siemens-Simotics-Series.html',
            'filename': 'siemens_simotics_hardware_manual',
            'title': 'Siemens SIMOTICS Series Hardware Installation Manual',
            'type': 'manualslib'
        },
        {
            'url': 'https://www.manualslib.com/manual/3137768/Siemens-Simotics-1pq8.html',
            'filename': 'siemens_simotics_1pq8_operating_manual',
            'title': 'Siemens SIMOTICS 1PQ8 Operating Instructions Manual',
            'type': 'manualslib'
        }
    ]
    
    success_count = 0
    
    for manual in manuals:
        print(f"\n[{manuals.index(manual)+1}/{len(manuals)}] {manual['title']}")
        
        if manual['type'] == 'manualslib':
            if scrape_manualslib(manual['url'], manual['filename']):
                success_count += 1
        else:
            if scrape_web_content(manual['url'], manual['filename'], manual['title']):
                success_count += 1
        
        time.sleep(2)  # Be polite between requests
    
    print("\n" + "="*60)
    print(f"SUMMARY: {success_count}/{len(manuals)} manuals scraped")
    print("="*60)
    
    if success_count > 0:
        print(f"\n✓ Saved to: {DEST_DIR}")
        print("\nNext step: Run upload_data.py to ingest into Qdrant")
    else:
        print("\n⚠️  No manuals scraped. You may need to download PDFs manually.")

if __name__ == "__main__":
    main()
