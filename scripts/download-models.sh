#!/bin/bash

################################################################################
# Model Download Script - Download all .pth files from OneDrive
# Usage: ./download-models.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Download Model Files from OneDrive"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# OneDrive share link
ONEDRIVE_LINK="https://binusianorg-my.sharepoint.com/personal/kus_andriadi_binus_ac_id/_layouts/15/guestaccess.aspx?share=EnNjotrV4F1Gp4RR3KVyXggB2y7v8tz3T2cxcbCqtzL5yA&e=UHQUPT"

# Target directory
MODEL_DIR="../backend/model"

# Expected model files
EXPECTED_FILES=(
    "REAL-ESRGAN.pth"
    "ConvNext_REAL-ESRGAN.pth"
)

################################################################################
# Check dependencies
################################################################################
print_info "Checking dependencies..."

if ! command -v wget &> /dev/null && ! command -v curl &> /dev/null; then
    print_error "Neither wget nor curl is installed"
    print_info "Install with: sudo apt install wget -y"
    exit 1
fi

if command -v wget &> /dev/null; then
    DOWNLOADER="wget"
    print_success "Using wget"
elif command -v curl &> /dev/null; then
    DOWNLOADER="curl"
    print_success "Using curl"
fi

echo ""

################################################################################
# Create model directory
################################################################################
print_info "Creating model directory..."

mkdir -p "$MODEL_DIR"
print_success "Directory ready: $MODEL_DIR"
echo ""

################################################################################
# Check existing files
################################################################################
print_info "Checking existing files..."

EXISTING_COUNT=0
for file in "${EXPECTED_FILES[@]}"; do
    if [ -f "$MODEL_DIR/$file" ]; then
        SIZE=$(du -h "$MODEL_DIR/$file" | cut -f1)
        print_success "$file exists ($SIZE)"
        EXISTING_COUNT=$((EXISTING_COUNT + 1))
    fi
done

echo ""

if [ $EXISTING_COUNT -eq ${#EXPECTED_FILES[@]} ]; then
    print_success "All model files already exist!"
    echo ""
    ls -lh "$MODEL_DIR"/*.pth
    echo ""
    read -p "Do you want to re-download? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    echo ""
fi

################################################################################
# Download files from OneDrive
################################################################################
print_info "Downloading model files from OneDrive..."
echo ""

# Convert OneDrive share link to direct download
# OneDrive guest access links can be converted to direct download by manipulating the URL
SHARE_TOKEN=$(echo "$ONEDRIVE_LINK" | grep -oP 'share=\K[^&]+')
BASE_URL="https://binusianorg-my.sharepoint.com/personal/kus_andriadi_binus_ac_id/_layouts/15/download.aspx"

print_info "Attempting to download files..."
echo ""

# Try to download each expected file
for file in "${EXPECTED_FILES[@]}"; do
    OUTPUT_FILE="$MODEL_DIR/$file"

    print_info "Downloading: $file"

    # Construct direct download URL
    DOWNLOAD_URL="${BASE_URL}?share=${SHARE_TOKEN}&file=${file}"

    # Try download
    if [ "$DOWNLOADER" = "wget" ]; then
        if wget -O "$OUTPUT_FILE" "$DOWNLOAD_URL" --progress=bar:force:noscroll --no-check-certificate 2>&1; then
            if [ -f "$OUTPUT_FILE" ]; then
                SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
                if [ "$SIZE" -gt 1000000 ]; then
                    SIZE_HR=$(du -h "$OUTPUT_FILE" | cut -f1)
                    print_success "$file downloaded ($SIZE_HR)"
                else
                    print_warning "$file seems too small, trying alternative method..."
                    rm -f "$OUTPUT_FILE"
                fi
            fi
        fi
    else
        if curl -L -o "$OUTPUT_FILE" "$DOWNLOAD_URL" --progress-bar --insecure 2>&1; then
            if [ -f "$OUTPUT_FILE" ]; then
                SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
                if [ "$SIZE" -gt 1000000 ]; then
                    SIZE_HR=$(du -h "$OUTPUT_FILE" | cut -f1)
                    print_success "$file downloaded ($SIZE_HR)"
                else
                    print_warning "$file seems too small, trying alternative method..."
                    rm -f "$OUTPUT_FILE"
                fi
            fi
        fi
    fi

    echo ""
done

################################################################################
# Check if download was successful
################################################################################
print_info "Verifying downloads..."
echo ""

SUCCESS_COUNT=0
FAILED_FILES=()

for file in "${EXPECTED_FILES[@]}"; do
    if [ -f "$MODEL_DIR/$file" ]; then
        SIZE=$(stat -f%z "$MODEL_DIR/$file" 2>/dev/null || stat -c%s "$MODEL_DIR/$file" 2>/dev/null)
        if [ "$SIZE" -gt 1000000 ]; then
            SIZE_HR=$(du -h "$MODEL_DIR/$file" | cut -f1)
            print_success "$file OK ($SIZE_HR)"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            print_error "$file failed (too small or corrupted)"
            FAILED_FILES+=("$file")
        fi
    else
        print_error "$file not downloaded"
        FAILED_FILES+=("$file")
    fi
done

echo ""

################################################################################
# Show results
################################################################################
if [ $SUCCESS_COUNT -eq ${#EXPECTED_FILES[@]} ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_success "ALL MODEL FILES DOWNLOADED SUCCESSFULLY!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_info "Files in $MODEL_DIR:"
    ls -lh "$MODEL_DIR"/*.pth
    echo ""
    print_success "You can now proceed with deployment"
else
    print_warning "Some files failed to download automatically"
    echo ""
    print_info "Failed files: ${FAILED_FILES[*]}"
    echo ""
    print_warning "Please download manually using one of these methods:"
    echo ""
    echo "METHOD 1: Download via browser"
    echo "──────────────────────────────"
    echo "1. Open this link in your browser:"
    echo "   $ONEDRIVE_LINK"
    echo ""
    echo "2. Download the following files:"
    for file in "${FAILED_FILES[@]}"; do
        echo "   → $file"
    done
    echo ""
    echo "3. Upload to VPS:"
    echo "   scp /path/to/*.pth username@vps:$MODEL_DIR/"
    echo ""
    echo "METHOD 2: Use rclone (automated)"
    echo "─────────────────────────────────"
    echo "   scripts/download-models-rclone.sh"
    echo ""
    exit 1
fi
