#!/bin/bash
# Generate self-signed SSL certificate for HTTPS

CERT_DIR="ssl"
CERT_FILE="$CERT_DIR/cert.pem"
KEY_FILE="$CERT_DIR/key.pem"

# Create ssl directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL certificates already exist at $CERT_FILE and $KEY_FILE"
    exit 0
fi

# Generate self-signed certificate
echo "Generating self-signed SSL certificate..."
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "SSL certificates generated successfully!"
echo "Certificate: $CERT_FILE"
echo "Key: $KEY_FILE"
echo ""
echo "Note: This is a self-signed certificate. Browsers will show a security warning."
echo "For production, use certificates from a trusted Certificate Authority (CA)."

