# 🚀 Solution Rapide - Erreur de Flashage

## ❌ Problème
```
FileNotFoundError: [Errno 2] No such file or directory: 'probe-rs'
```

## ✅ Solution Immédiate

### Option 1: Via l'Extension (Recommandé)
1. Ouvrir VS Code avec l'extension
2. **Palette de commandes** (`Ctrl+Shift+P`)
3. **"Rust Embedded: Configurer l'environnement complet"**
4. Attendre la fin d'installation (5-10 minutes)

### Option 2: Via la ligne de commande
```bash
# Installation probe-rs pour Pico
cargo install probe-rs-tools --locked

# Ou pour ESP32-C3
cargo install espflash

# Vérifier l'installation
probe-rs --version
espflash --version
```

### Option 3: Configuration automatique complète
```bash
cd /home/karagure/extension-hybride
python3 main.py setup
```

## 🔍 Vérification
```bash
# Vérifier que les outils sont installés
which probe-rs      # Pour Pico
which espflash      # Pour ESP32-C3

# Tester un flash après installation
cd votre-projet
python3 /home/karagure/extension-hybride/main.py flash --target pico
```

## ⏰ Temps d'installation
- **probe-rs-tools**: 5-10 minutes (compilation Rust)
- **espflash**: 2-3 minutes

## 🎯 Une fois installé
L'extension VS Code détectera automatiquement les outils et le flashage fonctionnera sans erreur !

---

**Note**: La première installation peut prendre du temps car les outils doivent être compilés depuis les sources Rust.