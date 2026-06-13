#!/bin/bash
# Download equipment manuals from manufacturer sites

DEST_DIR="/Users/abdulnazeermeeramaideen/Documents/Abdul Nazeer/Alloy-Agent/data/raw/manuals"

echo "Downloading equipment manuals..."

# Atlas Copco Compressed Air Manual
echo "1/4 Downloading Atlas Copco manual..."
curl -L -o "$DEST_DIR/atlas_copco_compressed_air_manual.pdf" \
  "https://www.atlascopco.com/content/dam/atlas-copco/local-countries/netherlands/documents/compressed-air-manual-8th-edition.pdf"

echo "✓ Downloaded Atlas Copco manual"

# Note: Other manufacturers (ManualsLib, Scribd) require browser downloads
# Download these manually:
# 2. ABB MT Series: http://www.manualslib.com/manual/1710834/Abb-Mt-Series.html
# 3. Parker BA Series: https://www.manualslib.com/manual/2930328/Parker-Greer-Ba-Series.html
# 4. Siemens SIMOTICS: http://www.manualslib.com/manual/1913649/Siemens-Simotics-Series.html

echo ""
echo "==========================================="
echo "Manual download summary:"
echo "✓ Atlas Copco: Downloaded"
echo "⚠ ABB, Parker, Siemens: Need browser download"
echo "==========================================="
echo ""
echo "For remaining manuals, open these in browser and click 'Download PDF':"
echo "1. ABB: http://www.manualslib.com/manual/1710834/Abb-Mt-Series.html"
echo "2. Parker: https://www.manualslib.com/manual/2930328/Parker-Greer-Ba-Series.html"
echo "3. Siemens: http://www.manualslib.com/manual/1913649/Siemens-Simotics-Series.html"
