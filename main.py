import argparse
import subprocess
import sys
import json
import os
import shutil
from pathlib import Path

# --- Configuration des Cibles ---
# On définit ici les informations spécifiques à chaque carte
TARGETS = {
    "pico": {
        "rust_target": "thumbv6m-none-eabi",
        "flasher": "probe-rs",
        "chip": "RP2040",
        "template": "pico_template"
    },
    "esp32c3": {
        "rust_target": "riscv32imc-unknown-none-elf",
        "flasher": "espflash",
        "chip": "esp32c3",
        "template": "esp32c3_template"
    },
}

TOOLS = {
    "probe-rs": {
        "install_command": ["cargo", "install", "probe-rs", "--features", "cli"],
        "check_command": ["probe-rs", "--version"]
    },
    "espflash": {
        "install_command": ["cargo", "install", "espflash"],
        "check_command": ["espflash", "--version"]
    }
}

def run_command(command, project_path):
    """Exécute une commande en temps réel et affiche sa sortie."""
    print(f"🚀 Exécution de : {' '.join(command)}")
    # L'argument `cwd` est crucial pour exécuter la commande dans le bon dossier
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        cwd=project_path
    )

    # Affiche la sortie ligne par ligne en temps réel
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip(), flush=True)

    # Vérifie si la commande a réussi
    if process.returncode != 0:
        print(f"❌ Erreur lors de l'exécution de la commande (code: {process.returncode})", file=sys.stderr)
        sys.exit(process.returncode)
    
    print("✅ Commande terminée avec succès.")
    return True


def find_elf_file(project_path, rust_target):
    """Trouve le fichier .elf compilé dans le dossier target."""
    # Le nom du projet est le nom du dossier parent
    project_name = Path(project_path).name
    # Le chemin du fichier .elf est prédictible
    elf_path = Path(project_path) / "target" / rust_target / "release" / project_name
    
    if not elf_path.exists():
         # Essayons le mode debug si le mode release n'existe pas
         elf_path = Path(project_path) / "target" / rust_target / "debug" / project_name
         if not elf_path.exists():
            print(f"❌ Impossible de trouver le fichier .elf. Avez-vous compilé le projet ?", file=sys.stderr)
            return None
            
    return str(elf_path)


def check_tool_installed(tool_name):
    """Vérifie si un outil est installé."""
    try:
        result = subprocess.run(TOOLS[tool_name]["check_command"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_rust_target(target):
    """Installe une target Rust."""
    print(f"🎯 Installation de la target Rust: {target}")
    command = ["rustup", "target", "add", target]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Target {target} installée avec succès")
    else:
        print(f"❌ Erreur lors de l'installation de la target {target}")
        print(result.stderr)
        return False
    return True

def install_tool(tool_name):
    """Installe un outil de flashage."""
    print(f"🔧 Installation de l'outil: {tool_name}")
    
    if check_tool_installed(tool_name):
        print(f"✅ {tool_name} est déjà installé")
        return True
    
    command = TOOLS[tool_name]["install_command"]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {tool_name} installé avec succès")
        return True
    else:
        print(f"❌ Erreur lors de l'installation de {tool_name}")
        print(result.stderr)
        return False

def create_project(project_name, target_name, project_path):
    """Crée un nouveau projet Rust embarqué."""
    print(f"📁 Création du projet {project_name} pour {target_name}")
    
    full_path = Path(project_path) / project_name
    
    if full_path.exists():
        print(f"❌ Le dossier {project_name} existe déjà")
        return False
    
    # Crée le projet Rust de base
    subprocess.run(["cargo", "init", str(full_path), "--name", project_name], 
                   cwd=project_path)
    
    target_config = TARGETS[target_name]
    
    # Crée le fichier Cargo.toml spécifique à l'embarqué
    cargo_toml_content = f"""[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
cortex-m = "0.7"
cortex-m-rt = "0.7"
panic-halt = "0.2"
"""
    
    if target_name == "pico":
        cargo_toml_content += """rp-pico = "0.8"
embedded-hal = "0.2.5"

[dependencies.rp2040-hal]
version = "0.9"
features = ["rt", "critical-section-impl"]
"""
    elif target_name == "esp32c3":
        cargo_toml_content += """esp32c3-hal = "0.15"
esp-backtrace = { version = "0.8", features = ["esp32c3", "exception-handler", "panic-handler", "println"] }
esp-println = { version = "0.6", features = ["esp32c3"] }
"""
    
    with open(full_path / "Cargo.toml", "w") as f:
        f.write(cargo_toml_content)
    
    # Crée le fichier .cargo/config.toml
    cargo_config_dir = full_path / ".cargo"
    cargo_config_dir.mkdir(exist_ok=True)
    
    config_content = f"""[build]
target = "{target_config['rust_target']}"

[target.{target_config['rust_target']}]
runner = "probe-rs run --chip {target_config['chip']}"
"""
    
    with open(cargo_config_dir / "config.toml", "w") as f:
        f.write(config_content)
    
    # Crée un main.rs de base
    src_dir = full_path / "src"
    main_rs_content = get_main_template(target_name)
    
    with open(src_dir / "main.rs", "w") as f:
        f.write(main_rs_content)
    
    print(f"✅ Projet {project_name} créé avec succès dans {full_path}")
    return True

def get_main_template(target_name):
    """Retourne le template main.rs pour la target donnée."""
    if target_name == "pico":
        return """#![no_std]
#![no_main]

use panic_halt as _;
use rp_pico::entry;
use rp_pico::hal::{clocks::{init_clocks_and_plls, Clock}, pac, sio::Sio, watchdog::Watchdog};

#[entry]
fn main() -> ! {
    let mut pac = pac::Peripherals::take().unwrap();
    let core = pac::CorePeripherals::take().unwrap();
    
    let mut watchdog = Watchdog::new(pac.WATCHDOG);
    let clocks = init_clocks_and_plls(
        rp_pico::XOSC_CRYSTAL_FREQ,
        pac.XOSC,
        pac.CLOCKS,
        pac.PLL_SYS,
        pac.PLL_USB,
        &mut pac.RESETS,
        &mut watchdog,
    )
    .ok()
    .unwrap();

    loop {
        // Votre code ici
    }
}
"""
    elif target_name == "esp32c3":
        return """#![no_std]
#![no_main]

use esp32c3_hal::{clock::ClockControl, peripherals::Peripherals, prelude::*, Rtc};
use esp_backtrace as _;

#[entry]
fn main() -> ! {
    let peripherals = Peripherals::take();
    let mut system = peripherals.DPORT.split();
    let clocks = ClockControl::boot_defaults(system.clock_control).freeze();
    
    let mut rtc = Rtc::new(peripherals.RTC_CNTL);
    rtc.rwdt.disable();

    loop {
        // Votre code ici
    }
}
"""
    return ""

def main():
    """Fonction principale pour parser les arguments et lancer les actions."""
    parser = argparse.ArgumentParser(description="Outil de build et flash pour Rust Embarqué.")
    parser.add_argument("action", choices=["build", "flash", "create", "install-target", "install-tools", "setup"], 
                       help="L'action à effectuer.")
    parser.add_argument("--target", choices=TARGETS.keys(), help="La carte cible.")
    parser.add_argument("--project-path", default=".", help="Le chemin vers le projet Rust.")
    parser.add_argument("--project-name", help="Le nom du nouveau projet (pour l'action create).")
    
    args = parser.parse_args()
    project_path = args.project_path
    
    # --- Action: create ---
    if args.action == "create":
        if not args.project_name:
            print("❌ Le nom du projet est requis pour créer un nouveau projet")
            sys.exit(1)
        if not args.target:
            print("❌ La target est requise pour créer un nouveau projet")
            sys.exit(1)
        create_project(args.project_name, args.target, project_path)
        
    # --- Action: install-target ---
    elif args.action == "install-target":
        if args.target:
            target_config = TARGETS[args.target]
            install_rust_target(target_config["rust_target"])
        else:
            # Installer toutes les targets
            for config in TARGETS.values():
                install_rust_target(config["rust_target"])
                
    # --- Action: install-tools ---
    elif args.action == "install-tools":
        if args.target:
            target_config = TARGETS[args.target]
            install_tool(target_config["flasher"])
        else:
            # Installer tous les outils
            for tool_name in TOOLS.keys():
                install_tool(tool_name)
                
    # --- Action: setup ---
    elif args.action == "setup":
        print("🔧 Configuration de l'environnement de développement...")
        
        # Installer toutes les targets
        for config in TARGETS.values():
            install_rust_target(config["rust_target"])
            
        # Installer tous les outils
        for tool_name in TOOLS.keys():
            install_tool(tool_name)
            
        print("✅ Environnement configuré avec succès!")
        
    # Actions nécessitant une target
    elif args.target:
        target_config = TARGETS[args.target]
        
        # --- Action: build ---
        if args.action == "build":
            print(f"🛠️  Compilation pour {args.target}...")
            build_command = [
                "cargo", "build", 
                "--release",
                "--target", target_config["rust_target"]
            ]
            run_command(build_command, project_path)
            
        # --- Action: flash ---
        elif args.action == "flash":
            print(f"⚡ Téléversement sur {args.target}...")
            
            # 1. Trouver le fichier binaire (.elf)
            elf_file = find_elf_file(project_path, target_config["rust_target"])
            if not elf_file:
                sys.exit(1)
            
            print(f" Fichier binaire trouvé : {elf_file}")

            # 2. Construire la commande de flash
            flash_command = []
            if target_config["flasher"] == "probe-rs":
                flash_command = ["probe-rs", "run", "--chip", target_config["chip"], elf_file]
                
            elif target_config["flasher"] == "espflash":
                flash_command = ["espflash", "flash", "-M", "dio", elf_file]

            # 3. Exécuter la commande
            run_command(flash_command, project_path)
    else:
        print("❌ Target requise pour cette action")
        sys.exit(1)


if __name__ == "__main__":
    main()