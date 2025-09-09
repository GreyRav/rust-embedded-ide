#!/bin/bash

echo "🚀 Test de l'extension [#] Rust Embedded"
echo "========================================"

# Compilation de l'extension
echo "📦 Compilation de l'extension..."
npm run compile

if [ $? -eq 0 ]; then
    echo "✅ Compilation réussie!"
else
    echo "❌ Erreur de compilation"
    exit 1
fi

# Test de détection Python
echo ""
echo "🐍 Test de détection Python..."
if command -v python3 &> /dev/null; then
    echo "✅ python3 détecté: $(python3 --version)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "✅ python détecté: $(python --version)"
    PYTHON_CMD="python"
else
    echo "❌ Aucune commande Python trouvée"
    exit 1
fi

# Test du backend Python
echo ""
echo "🐍 Test du backend Python avec $PYTHON_CMD..."
$PYTHON_CMD main.py --help

if [ $? -eq 0 ]; then
    echo "✅ Backend Python fonctionnel!"
else
    echo "❌ Problème avec le backend Python"
    exit 1
fi

# Vérification des fichiers essentiels
echo ""
echo "📋 Vérification des fichiers..."

files=(
    "package.json"
    "images/icon.png" 
    "src/extension.ts"
    "src/welcomePanel.ts"
    "src/actionsProvider.ts"
    "src/rustEmbeddedProvider.ts"
    "main.py"
)

all_good=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant"
        all_good=false
    fi
done

if [ "$all_good" = true ]; then
    # Vérification des outils de flashage
    echo ""
    echo "🔧 Vérification des outils de flashage..."
    if command -v probe-rs &> /dev/null; then
        echo "✅ probe-rs installé: $(probe-rs --version | head -1)"
    else
        echo "⚠️  probe-rs non installé (requis pour Pico)"
    fi

    if command -v espflash &> /dev/null; then
        echo "✅ espflash installé: $(espflash --version | head -1)"
    else
        echo "⚠️  espflash non installé (requis pour ESP32-C3)"
    fi

    echo ""
    echo "🎉 Extension prête à être testée!"
    echo ""
    echo "Pour tester dans VS Code:"
    echo "1. Appuyez sur F5 dans VS Code"  
    echo "2. L'extension se lancera dans une nouvelle fenêtre"
    echo "3. Le panneau de bienvenue apparaîtra automatiquement"
    echo ""
    echo "⚠️  IMPORTANT - Première utilisation:"
    echo "   Utilisez '⚙️ Configurer l'Environnement' avant de flasher"
    echo ""
    echo "Fonctionnalités à tester:"
    echo "- 🏠 Panneau de bienvenue avec cartes dev boards"
    echo "- 📁 Création de projet (Pico/ESP32-C3)"
    echo "- ⚙️ Configuration automatique de l'environnement"  
    echo "- 🛠️ Compilation des projets"
    echo "- ⚡ Flashage sur les cartes"
    echo "- 🎯 Barre latérale Rust Embedded"
else
    echo "❌ Des fichiers sont manquants, vérifiez l'installation"
    exit 1
fi