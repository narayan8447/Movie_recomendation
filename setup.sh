# Create a directory for Streamlit configuration if it doesn't exist
mkdir -p ~/.streamlit/

# Create the Streamlit configuration file (config.toml)
# This file sets the server options and the visual theme of the app.
echo "\
[server]
headless = true
port = $PORT
enableCORS = false

[theme]
primaryColor='#e63946'
backgroundColor='#1a1a1a'
secondaryBackgroundColor='#2b2b2b'
textColor='#ffffff'
font='sans serif'
" > ~/.streamlit/config.toml
