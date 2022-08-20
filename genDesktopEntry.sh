APPDIR="$(pwd)"

echo "[Desktop Entry]
Encoding=UTF-8
Version=1.0
Type=Application
Terminal=false
Path=""$APPDIR""
Exec=bash -c \"cd '$APPDIR' && bash ""$APPDIR""/run.sh\"
Name=MemoryUsageViewer
Icon=""$APPDIR""/icons/app.png
" > "MemoryUsageViewer.desktop"

cp "MemoryUsageViewer.desktop" ~/.local/share/applications/

