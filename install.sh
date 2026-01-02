#!/bin/bash

# TeleSentry V2 Installation Script
# This script installs all required dependencies and sets up the environment

set -e  # Exit on any error

echo "=========================================="
echo "TeleSentry V2 Installation Script"
echo "=========================================="
echo ""

# define some colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database configuration (change this if you are going to put this in production)
DB_NAME="search_telegram"
DB_USER="grilo"
DB_PASSWORD="grilo"
SQL_FILE="mysq.sql"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update package list
print_status "Updating package list..."
apt-get update -y

# Install Python3
print_status "Installing Python3..."
apt-get install -y python3

# Install pip3
print_status "Installing pip3..."
apt-get install -y python3-pip

# Install Python requirements
print_status "Installing Python requirements..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    print_status "Python requirements installed successfully"
else
    print_warning "requirements.txt not found, skipping Python package installation"
fi

# Install Apache2
print_status "Installing Apache2..."
apt-get install -y apache2

# Start and enable Apache2
systemctl start apache2
systemctl enable apache2
print_status "Apache2 installed and started"

# Install MariaDB
print_status "Installing MariaDB..."
# Set root password for MariaDB (non-interactive)
debconf-set-selections <<< "mariadb-server mariadb-server/root_password password ${DB_PASSWORD}"
debconf-set-selections <<< "mariadb-server mariadb-server/root_password_again password ${DB_PASSWORD}"

apt-get install -y mariadb-server mariadb-client

# Start and enable MariaDB
systemctl start mariadb
systemctl enable mariadb
print_status "MariaDB installed and started"

# Wait a moment for MariaDB to fully start
sleep 3

# Create database and user
print_status "Creating database and user..."
mysql -u root -p${DB_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

print_status "Database and user created successfully"

# Restore SQL file
print_status "Restoring SQL file..."
if [ -f "${SQL_FILE}" ]; then
    mysql -u root -p${DB_PASSWORD} ${DB_NAME} < ${SQL_FILE}
    print_status "SQL file restored successfully"
else
    print_error "${SQL_FILE} not found! Please ensure the SQL file exists."
    exit 1
fi

# Grant privileges (ensure they are set)
print_status "Granting MySQL privileges..."
mysql -u root -p${DB_PASSWORD} <<EOF
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
print_status "MySQL privileges granted"

# Install PHP MySQL extension
print_status "Installing php-mysql..."
apt-get install -y php-mysql

# Install PHP and Apache PHP module
print_status "Installing PHP and libapache2-mod-php..."
apt-get install -y php libapache2-mod-php

# Restart Apache to load PHP module
systemctl restart apache2
print_status "Apache2 restarted with PHP support"

# Copy web files to Apache2 document root
print_status "Copying web files to Apache2 document root..."
WEB_SOURCE="web/telegram_webserver"
APACHE_WEB_ROOT="/var/www/html"

if [ -d "${WEB_SOURCE}" ]; then
    # Create destination directory if it doesn't exist
    mkdir -p "${APACHE_WEB_ROOT}"
    
    # Copy web files (preserving structure)
    cp -r "${WEB_SOURCE}" "${APACHE_WEB_ROOT}/"
    
    # Set appropriate permissions
    chown -R www-data:www-data "${APACHE_WEB_ROOT}/telegram_webserver"
    chmod -R 755 "${APACHE_WEB_ROOT}/telegram_webserver"
    
    print_status "Web files copied to ${APACHE_WEB_ROOT}/telegram_webserver"
else
    print_warning "Web directory ${WEB_SOURCE} not found, skipping web file deployment"
fi

echo ""
echo "=========================================="
print_status "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Python3: Installed"
echo "  - pip3: Installed"
echo "  - Python requirements: Installed"
echo "  - Apache2: Installed and running"
echo "  - Web files: Deployed to /var/www/html/telegram_webserver"
echo "  - MariaDB: Installed and running"
echo "  - Database '${DB_NAME}': Created"
echo "  - Database user '${DB_USER}': Created"
echo "  - SQL file: Restored"
echo "  - PHP: Installed"
echo "  - php-mysql: Installed"
echo "  - libapache2-mod-php: Installed"
echo ""
print_status "Setup complete! You can now use TeleSentry V2 :)."

