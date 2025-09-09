# Extension Rust Embedded pour VS Code

Une extension VS Code hybride TypeScript/Python pour le développement Rust embarqué, spécialement conçue pour les cartes ESP32-C3 et Raspberry Pi Pico (RP2040).

## Fonctionnalités

- 🚀 **Création de projets** : Templates pré-configurés pour ESP32-C3 et Pico RP2040
- 🛠️ **Compilation automatisée** : Build optimisé pour l'embarqué
- ⚡ **Flashage intégré** : Support de `probe-rs` (Pico) et `espflash` (ESP32-C3)
- 🎯 **Gestion des targets** : Installation automatique des targets Rust
- 🔧 **Configuration d'environnement** : Setup complet en un clic

## Installation

1. Copiez cette extension dans votre dossier d'extensions VS Code
2. Installez les dépendances :
   ```bash
   npm install
   npm run compile
   ```

## Prérequis

- **Rust** : Installé via rustup
- **Python 3.x** : Pour le backend de gestion des projets
- **Cargo** : Gestionnaire de packages Rust

## Utilisation

### Configuration initiale

1. Ouvrez la palette de commandes (`Ctrl+Shift+P`)
2. Exécutez `Rust Embedded: Configurer l'environnement de développement`
3. L'extension installera automatiquement :
   - Target `thumbv6m-none-eabi` (Pico RP2040)
   - Target `riscv32imc-unknown-none-elf` (ESP32-C3)
   - `probe-rs` (outil de flashage Pico)
   - `espflash` (outil de flashage ESP32-C3)

### Créer un nouveau projet

1. `Rust Embedded: Créer un nouveau projet Rust embarqué`
2. Choisissez votre nom de projet
3. Sélectionnez votre carte cible (Pico ou ESP32-C3)
4. Le projet sera créé avec la structure et configuration appropriées

### Compiler et flasher

1. Ouvrez un projet Rust embarqué
2. `Rust Embedded: Compiler le projet` - Compile pour la target sélectionnée
3. `Rust Embedded: Flasher le projet` - Flash le firmware sur votre carte

## Structure des projets générés

### Pour Raspberry Pi Pico (RP2040)
```
mon-projet/
├── Cargo.toml          # Dépendances rp-pico, rp2040-hal
├── .cargo/
│   └── config.toml     # Configuration target thumbv6m-none-eabi
└── src/
    └── main.rs         # Template avec initialisation HAL
```

### Pour ESP32-C3
```
mon-projet/
├── Cargo.toml          # Dépendances esp32c3-hal, esp-backtrace
├── .cargo/
│   └── config.toml     # Configuration target riscv32imc-unknown-none-elf  
└── src/
    └── main.rs         # Template avec initialisation périphériques
```

## Commandes disponibles

- `Rust Embedded: Créer un nouveau projet Rust embarqué`
- `Rust Embedded: Compiler le projet`
- `Rust Embedded: Flasher le projet`
- `Rust Embedded: Installer les targets Rust`
- `Rust Embedded: Installer les outils de flashage`
- `Rust Embedded: Configurer l'environnement de développement`

## Architecture

- **Frontend TypeScript** : Interface utilisateur VS Code, gestion des commandes
- **Backend Python** : Logique métier, création de projets, compilation, flashage
- **Templates intégrés** : Configurations pré-définies pour chaque carte

## Cartes supportées

| Carte | Target Rust | Outil de flashage | Statut |
|-------|-------------|-------------------|---------|
| Raspberry Pi Pico (RP2040) | `thumbv6m-none-eabi` | `probe-rs` | ✅ |
| ESP32-C3 | `riscv32imc-unknown-none-elf` | `espflash` | ✅ |

## Développement

```bash
# Compiler l'extension
npm run compile

# Mode watch
npm run watch

# Test du backend Python
python main.py setup
python main.py create --target pico --project-name test-pico
```