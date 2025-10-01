#!/bin/bash
# Create a macOS app bundle for easy launching

APP_NAME="Notetaker AI"
APP_DIR="$HOME/Desktop/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
PROJECT_DIR="$(pwd)"

echo "📦 Creating macOS app: $APP_NAME.app"
echo ""

# Create app structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create the launcher script
cat > "$MACOS_DIR/launcher.sh" << 'EOFSCRIPT'
#!/bin/bash
cd "PROJECT_PATH"
bash start.sh
EOFSCRIPT

# Replace PROJECT_PATH with actual path
sed -i '' "s|PROJECT_PATH|$PROJECT_DIR|g" "$MACOS_DIR/launcher.sh"
chmod +x "$MACOS_DIR/launcher.sh"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.notetaker.ai</string>
    <key>CFBundleName</key>
    <string>Notetaker AI</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
</dict>
</plist>
EOF

echo "✅ App created at: $APP_DIR"
echo ""
echo "🎯 To use:"
echo "   1. Double-click 'Notetaker AI.app' on your Desktop"
echo "   2. Or drag it to your Dock for easy access"
echo ""
echo "💡 The app will:"
echo "   • Start Ollama (if needed)"
echo "   • Start the backend server"
echo "   • Open your browser to the app"
