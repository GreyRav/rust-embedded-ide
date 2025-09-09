# 🍓 Guide de Flashage Raspberry Pi Pico (RP2040)

Le Raspberry Pi Pico propose **deux méthodes de flashage** différentes des autres microcontrôleurs.

## 🎯 Méthodes Disponibles

### 1. 💾 **Mode BOOTSEL (Recommandé)**
**Avantages:**
- ✅ Aucun matériel supplémentaire requis
- ✅ Simple à utiliser
- ✅ Fonctionne sur tous les OS
- ✅ Pas de configuration nécessaire

**Inconvénients:**
- ⚠️ Nécessite une manipulation physique du Pico
- ⚠️ Pas de débogage en temps réel

### 2. 🔌 **Mode SWD (avec débogueur)**
**Avantages:**
- ✅ Flashage automatique
- ✅ Débogage en temps réel
- ✅ Pas de manipulation physique

**Inconvénients:**
- ❌ Nécessite un débogueur SWD (Pico Probe, ST-Link, etc.)
- ❌ Configuration plus complexe
- ❌ Matériel supplémentaire requis

## 📋 Processus Mode BOOTSEL (UF2)

### Étapes :
1. **Débrancher** le Pico du port USB
2. **Maintenir** le bouton BOOTSEL enfoncé
3. **Reconnecter** le Pico (tout en maintenant BOOTSEL)
4. **Relâcher** BOOTSEL
5. Le Pico apparaît comme **lecteur USB** (RPI-RP2)
6. L'extension **convertit automatiquement** ELF → UF2
7. **Copie automatique** du fichier UF2 sur le Pico
8. Le Pico **redémarre automatiquement** avec le nouveau firmware

### Outils requis :
```bash
cargo install elf2uf2-rs --locked
```

## 🔌 Processus Mode SWD 

### Connexions :
```
Débogueur SWD → Pico
SWDIO        → GPIO 3 (SWDIO)
SWCLK        → GPIO 2 (SWCLK)  
GND          → GND
3.3V         → 3.3V (optionnel)
```

### Outils requis :
```bash
cargo install probe-rs-tools --locked
```

### Usage :
```bash
probe-rs run --chip RP2040 firmware.elf
```

## 🚀 Utilisation avec l'Extension

### Configuration automatique :
```bash
# Installe les deux outils pour Pico
python3 main.py install-tools --target pico
```

### Flashage intelligent :
L'extension détecte automatiquement la méthode disponible :

1. **Si elf2uf2-rs est installé** → Mode BOOTSEL (UF2)
2. **Si probe-rs est installé** → Mode SWD  
3. **Si les deux** → Priorité au mode BOOTSEL (plus simple)

### Dans VS Code :
1. Ouvrir un projet Pico
2. Cliquer sur **⚡ Flasher**
3. L'extension choisit automatiquement la meilleure méthode
4. Suivre les instructions à l'écran

## 🔧 Dépannage

### "Aucun Pico en mode BOOTSEL détecté"
- Vérifier que le Pico est en mode BOOTSEL (LED clignote)
- Vérifier qu'il apparaît comme lecteur USB
- Sur Linux : `lsblk` ou `ls /media/*/`

### "probe-rs: No probe found"
- Vérifier les connexions SWD
- Vérifier que le débogueur est reconnu : `lsusb`
- Tester : `probe-rs list`

### Conversion ELF → UF2 échoue
- Vérifier que le fichier ELF existe
- Vérifier les permissions du dossier
- Recompiler le projet : `cargo build --target thumbv6m-none-eabi`

## 💡 Conseils

### Pour le développement :
- **Prototypage** : Mode BOOTSEL (simple et rapide)
- **Débogage** : Mode SWD (analyse en temps réel)

### Configuration recommandée :
```bash
# Installation complète pour Pico
cargo install elf2uf2-rs --locked    # Mode BOOTSEL
cargo install probe-rs-tools --locked # Mode SWD (optionnel)
rustup target add thumbv6m-none-eabi  # Target RP2040
```

## 🎯 Comparaison avec autres MCU

| Carte | Méthode | Outil |
|-------|---------|--------|
| **Pico RP2040** | BOOTSEL (UF2) | `elf2uf2-rs` |
| **Pico RP2040** | SWD | `probe-rs` |
| **ESP32-C3** | Serial/USB | `espflash` |
| **Arduino** | Serial | `avrdude` |

Le Pico est unique avec son mode BOOTSEL qui le fait apparaître comme une clé USB ! 🔥