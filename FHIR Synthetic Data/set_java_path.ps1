# -------------------------------------------------------------------
# Set Java and Node paths explicitly
# -------------------------------------------------------------------
$JavaPath = "C:\Users\yvy7zh\Work\Applications\jdk-17.0.18+8\bin"
$NodePath = "C:\Users\yvy7zh\Work\Applications\node-v24.13.1-win-x64"

$env:PATH = "$JavaPath;$NodePath;$env:PATH"

Write-Host "Java path set to: $JavaPath"
Write-Host "Node path set to: $NodePath"
