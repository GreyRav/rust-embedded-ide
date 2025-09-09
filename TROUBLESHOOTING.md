# 🔧 Guide de Dépannage - Extension [#] Rust Embedded

## Problèmes Python

### ❌ "Python n'est pas installé ou non disponible dans PATH"

**Cause** : L'extension ne trouve ni `python` ni `python3` dans votre système.

**Solutions par plateforme :**

#### 🐧 Linux (Ubuntu/Debian)
```bash
# Installer Python 3
sudo apt update
sudo apt install python3 python3-pip

# Vérifier l'installation
python3 --version
```

#### 🍎 macOS
```bash
# Via Homebrew (recommandé)
brew install python

# Ou télécharger depuis python.org
# https://www.python.org/downloads/macos/
```

#### 🪟 Windows
1. Télécharger Python depuis [python.org](https://www.python.org/downloads/windows/)
2. **Important** : Cocher "Add Python to PATH" lors de l'installation
3. Redémarrer VS Code après installation

### ❌ Extension utilise "python" mais vous avez "python3"

**Cause** : Sur certains systèmes (Linux/macOS récents), seul `python3` est disponible.

**Solution automatique** : L'extension détecte automatiquement la commande disponible.

**Vérification manuelle** :
```bash
# Test des commandes disponibles
python3 --version   # Linux/macOS moderne
python --version    # Windows/systèmes avec alias
```

### ❌ "Command failed" lors de l'exécution

**Causes possibles :**
1. Python installé mais pas dans PATH
2. Permissions insuffisantes
3. Version Python incompatible (< 3.6)

**Solutions :**

#### Vérifier PATH
```bash
# Linux/macOS
echo $PATH | grep -o '[^:]*python[^:]*'

# Windows (PowerShell)
$env:PATH -split ';' | Select-String python
```

#### Tester manuellement
```bash
# Aller dans le dossier de l'extension
cd /path/to/extension

# Tester le script Python
python3 main.py --help
# ou
python main.py --help
```

## Problèmes Rust

### ❌ "rustup: command not found"

**Solution** : Installer Rust
```bash
# Installation Rust via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Redémarrer le terminal
source ~/.cargo/env

# Vérifier
rustup --version
cargo --version
```

### ❌ "Target ... not found"

**Solution** : L'extension installera automatiquement les targets, mais vous pouvez le faire manuellement :
```bash
# Pour Raspberry Pi Pico
rustup target add thumbv6m-none-eabi

# Pour ESP32-C3
rustup target add riscv32imc-unknown-none-elf
```

## Problèmes VS Code

### ❌ Extension ne se lance pas

1. **Vérifier les logs** : `Ctrl+Shift+P` → "Developer: Open Extension Host"
2. **Recharger** : `Ctrl+Shift+P` → "Developer: Reload Window"  
3. **Réinstaller** : Supprimer et réinstaller l'extension

### ❌ Panneau de bienvenue n'apparaît pas

**Causes possibles :**
- Un projet Rust est déjà ouvert (Cargo.toml détecté)
- Extension désactivée

**Solutions :**
1. Fermer le projet actuel
2. `Ctrl+Shift+P` → "Rust Embedded: Panneau de Bienvenue"
3. Vérifier que l'extension est activée dans les paramètres

### ❌ Terminal ne s'ouvre pas

**Solution** : Vérifier les paramètres de terminal VS Code
```json
// settings.json
{
    "terminal.integrated.shell.linux": "/bin/bash",
    "terminal.integrated.shell.windows": "cmd.exe"
}
```

## Tests de Diagnostic

### 🧪 Test Complet
```bash
# Lancer le script de test
./test-extension.sh
```

### 🐍 Test Python Seul
```bash
# Test de détection Python
node test-python-detection.js
```

### 🔍 Debug Mode VS Code
1. Ouvrir le dossier de l'extension dans VS Code
2. `F5` pour lancer en mode debug
3. Ouvrir les Developer Tools (`Ctrl+Shift+I`)
4. Vérifier la console pour les erreurs

## Logs et Débogage

### Activer les logs détaillés
```json
// settings.json
{
    "rust-embedded.debug": true,
    "rust-embedded.verboseLogging": true
}
```

### Localisation des logs
- **Linux/macOS** : `~/.vscode/extensions/rust-embedded-*/logs/`
- **Windows** : `%USERPROFILE%\.vscode\extensions\rust-embedded-*\logs\`

## Problèmes Fréquents

### 🔄 "Permission denied" sur Linux/macOS
```bash
# Donner les permissions d'exécution
chmod +x main.py
chmod +x test-extension.sh
```

### 🔒 Antivirus bloque l'exécution (Windows)
1. Ajouter le dossier d'extension aux exclusions
2. Temporairement désactiver la protection temps réel pour l'installation

### 🌐 Problème de proxy d'entreprise
```bash
# Configuration proxy pour pip/cargo
export https_proxy=http://proxy.company.com:8080
export http_proxy=http://proxy.company.com:8080
```

## Support

Si le problème persiste :

1. **Vérifier** : `./test-extension.sh` passe tous les tests
2. **Collecter** : Logs VS Code + sortie terminal
3. **Créer issue** : Avec informations système (OS, Python version, Rust version)

### Informations à inclure
```bash
# Système
uname -a                 # Linux/macOS
systeminfo               # Windows

# Versions
python3 --version
cargo --version
code --version

# Test extension
./test-extension.sh
```