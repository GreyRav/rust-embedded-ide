import argparse
import subprocess
import sys
import json
import os
import shutil
from pathlib import Path

# --- Configuration des Cibles ---
# On definit ici les informations specifiques a chaque carte
TARGETS = {
    "pico": {
        "rust_target": "thumbv6m-none-eabi",
        "flasher": "elf2uf2-rs",  # Convertit ELF vers UF2 pour mode BOOTSEL
        "flasher_alt": "probe-rs", # Alternative avec debogueur SWD
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
    "elf2uf2-rs": {
        "install_command": ["cargo", "install", "elf2uf2-rs", "--locked"],
        "check_command": ["elf2uf2-rs", "--help"]
    },
    "probe-rs": {
        "install_command": ["cargo", "install", "probe-rs-tools", "--locked"],
        "check_command": ["probe-rs", "--version"]
    },
    "espflash": {
        "install_command": ["cargo", "install", "espflash"],
        "check_command": ["espflash", "--version"]
    }
}

def run_command(command, project_path):
    """Execute une commande en temps reel et affiche sa sortie."""
    print(f"🚀 Execution de : {' '.join(command)}")
    
    try:
        # L'argument `cwd` est crucial pour executer la commande dans le bon dossier
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            cwd=project_path
        )

        # Affiche la sortie ligne par ligne en temps reel
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip(), flush=True)

        # Verifie si la commande a reussi
        if process.returncode != 0:
            print(f"❌ Erreur lors de l'execution de la commande (code: {process.returncode})", file=sys.stderr)
            sys.exit(process.returncode)
        
        print("✅ Commande terminee avec succes.")
        return True
        
    except FileNotFoundError as e:
        tool_name = command[0]
        print(f"❌ Erreur: L'outil '{tool_name}' n'est pas installe.", file=sys.stderr)
        print(f"", file=sys.stderr)
        
        if tool_name == "probe-rs":
            print(f"💡 Pour installer probe-rs (outil de flashage Pico):", file=sys.stderr)
            print(f"   cargo install probe-rs-tools --locked", file=sys.stderr)
            print(f"   ou utilisez: python3 {sys.argv[0]} install-tools --target pico", file=sys.stderr)
        elif tool_name == "espflash":
            print(f"💡 Pour installer espflash (outil de flashage ESP32-C3):", file=sys.stderr)
            print(f"   cargo install espflash", file=sys.stderr)
            print(f"   ou utilisez: python3 {sys.argv[0]} install-tools --target esp32c3", file=sys.stderr)
        elif tool_name == "cargo":
            print(f"💡 Pour installer Rust et Cargo:", file=sys.stderr)
            print(f"   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh", file=sys.stderr)
        elif tool_name == "rustup":
            print(f"💡 Pour installer rustup:", file=sys.stderr)
            print(f"   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh", file=sys.stderr)
        else:
            print(f"💡 Installez {tool_name} et assurez-vous qu'il soit dans votre PATH.", file=sys.stderr)
            
        print(f"", file=sys.stderr)
        print(f"🔧 Pour configurer automatiquement tout l'environnement:", file=sys.stderr)
        print(f"   python3 {sys.argv[0]} setup", file=sys.stderr)
        sys.exit(1)


def find_elf_file(project_path, rust_target):
    """Trouve le fichier .elf compile dans le dossier target."""
    # Lire le nom du projet depuis Cargo.toml
    cargo_toml_path = Path(project_path) / "Cargo.toml"
    project_name = None
    
    if cargo_toml_path.exists():
        try:
            with open(cargo_toml_path, 'r') as f:
                for line in f:
                    if line.startswith('name = '):
                        project_name = line.split('=')[1].strip().strip('"\'')
                        break
        except Exception:
            pass
    
    # Fallback au nom du dossier si on ne trouve pas dans Cargo.toml
    if not project_name:
        project_name = Path(project_path).name
    
    # Essayer le mode release en premier
    elf_path = Path(project_path) / "target" / rust_target / "release" / project_name
    
    if elf_path.exists() and elf_path.is_file():
        return str(elf_path)
    
    # Essayons le mode debug si le mode release n'existe pas
    elf_path = Path(project_path) / "target" / rust_target / "debug" / project_name
    
    if elf_path.exists() and elf_path.is_file():
        return str(elf_path)
    
    print(f"❌ Impossible de trouver le fichier .elf. Avez-vous compile le projet ?", file=sys.stderr)
    print(f"🔍 Recherche:", file=sys.stderr)
    print(f"   - {Path(project_path) / 'target' / rust_target / 'release' / project_name}", file=sys.stderr)
    print(f"   - {Path(project_path) / 'target' / rust_target / 'debug' / project_name}", file=sys.stderr)
    return None


def check_tool_installed(tool_name):
    """Verifie si un outil est installe."""
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
        print(f"✅ Target {target} installee avec succes")
    else:
        print(f"❌ Erreur lors de l'installation de la target {target}")
        print(result.stderr)
        return False
    return True

def install_tool(tool_name):
    """Installe un outil de flashage."""
    print(f"🔧 Installation de l'outil: {tool_name}")
    
    if check_tool_installed(tool_name):
        print(f"✅ {tool_name} est deja installe")
        return True
    
    command = TOOLS[tool_name]["install_command"]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {tool_name} installe avec succes")
        return True
    else:
        print(f"❌ Erreur lors de l'installation de {tool_name}")
        print(result.stderr)
        return False

def create_project(project_name, target_name, project_path):
    """Cree un nouveau projet Rust embarque."""
    print(f"📁 Creation du projet {project_name} pour {target_name}")
    
    full_path = Path(project_path) / project_name
    
    if full_path.exists():
        print(f"❌ Le dossier {project_name} existe deja")
        return False
    
    # Cree le projet Rust de base
    subprocess.run(["cargo", "init", str(full_path), "--name", project_name], 
                   cwd=project_path)
    
    target_config = TARGETS[target_name]
    
    # Cree le fichier Cargo.toml specifique a l'embarque
    cargo_toml_content = f"""[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "{project_name}"
test = false
bench = false

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

# Outils pour la generation UF2
[dependencies.rp2040-boot2]
version = "0.3"
"""
    elif target_name == "esp32c3":
        cargo_toml_content += """esp32c3-hal = "0.15"
esp-backtrace = { version = "0.8", features = ["esp32c3", "exception-handler", "panic-handler", "println"] }
esp-println = { version = "0.6", features = ["esp32c3"] }
"""
    
    with open(full_path / "Cargo.toml", "w") as f:
        f.write(cargo_toml_content)
    
    # Cree le fichier .cargo/config.toml
    cargo_config_dir = full_path / ".cargo"
    cargo_config_dir.mkdir(exist_ok=True)
    
    if target_name == "pico":
        config_content = f"""[build]
target = "{target_config['rust_target']}"

[target.{target_config['rust_target']}]
runner = "elf2uf2-rs -d"
rustflags = [
    "-C", "link-arg=--nmagic",
    "-C", "link-arg=-Tlink.x",
]
"""
    else:
        config_content = f"""[build]
target = "{target_config['rust_target']}"

[target.{target_config['rust_target']}]
runner = "probe-rs run --chip {target_config['chip']}"
"""
    
    with open(cargo_config_dir / "config.toml", "w") as f:
        f.write(config_content)
    
    # Cree un main.rs de base
    src_dir = full_path / "src"
    main_rs_content = get_main_template(target_name)
    
    with open(src_dir / "main.rs", "w") as f:
        f.write(main_rs_content)
    
    # Creer le fichier memory.x pour Pico
    if target_name == "pico":
        memory_x_content = """/* Memory layout of the RP2040 microcontroller */
MEMORY {
    BOOT2 : ORIGIN = 0x10000000, LENGTH = 0x100
    FLASH : ORIGIN = 0x10000100, LENGTH = 2048K - 0x100
    RAM   : ORIGIN = 0x20000000, LENGTH = 256K
}

EXTERN(BOOT2_FIRMWARE)

SECTIONS {
    /* ### Boot loader */
    .boot2 ORIGIN(BOOT2) :
    {
        KEEP(*(.boot2));
    } > BOOT2
} INSERT BEFORE .text;
"""
        with open(full_path / "memory.x", "w") as f:
            f.write(memory_x_content)
    
    print(f"✅ Projet {project_name} cree avec succes dans {full_path}")
    return True

def get_main_template(target_name):
    """Retourne le template main.rs pour la target donnee."""
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
        // Your code here
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
        // Your code here
    }
}
"""
    return ""

def flash_pico_uf2_direct(project_path):
    """Flashage du Pico via cargo run avec elf2uf2-rs."""
    print("📋 Flashage Pico en mode BOOTSEL (UF2) - Methode directe")
    print("ℹ️  Ce mode necessite que le Pico soit connecte en mode BOOTSEL :")
    print("   1. Debrancher le Pico")
    print("   2. Maintenir le bouton BOOTSEL enfonce")
    print("   3. Reconnecter le Pico (tout en maintenant BOOTSEL)")
    print("   4. Relâcher BOOTSEL - le Pico apparaît comme lecteur USB")
    print()
    
    # Utiliser cargo run qui declenchera elf2uf2-rs comme runner
    print("🚀 Compilation et flashage via cargo run...")
    cargo_command = ["cargo", "run", "--release"]
    
    result = subprocess.run(cargo_command, cwd=project_path)
    
    if result.returncode == 0:
        print("✅ Flashage Pico termine avec succes!")
        return True
    else:
        print("❌ Erreur lors du flashage direct", file=sys.stderr)
        return False

def flash_pico_uf2_binutils(project_path, elf_file):
    """Flashage du Pico via cargo-binutils (generation .bin → UF2)."""
    print("🔧 Tentative de generation UF2 via cargo-binutils...")
    
    # Generer le fichier .bin depuis l'ELF
    bin_file = elf_file.replace('.elf', '.bin') if elf_file.endswith('.elf') else elf_file + '.bin'
    objcopy_command = ["cargo", "objcopy", "--release", "--", "-O", "binary", bin_file]
    
    result = subprocess.run(objcopy_command, cwd=project_path, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erreur generation binaire:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return False
    
    print(f"✅ Fichier binaire cree: {bin_file}")
    
    # Convertir .bin vers UF2
    uf2_file = bin_file.replace('.bin', '.uf2')
    
    # Essayer d'abord elf2uf2-rs
    convert_command = ["elf2uf2-rs", bin_file, uf2_file]
    result = subprocess.run(convert_command, cwd=project_path, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️ elf2uf2-rs a echoue, utilisation du convertisseur personnalise...")
        # Utiliser notre convertisseur UF2 personnalise
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uf2conv_path = os.path.join(script_dir, "uf2conv.py")
        
        if os.path.exists(uf2conv_path):
            custom_command = ["python3", uf2conv_path, bin_file, uf2_file]
            result = subprocess.run(custom_command, cwd=project_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Erreur conversion .bin vers UF2 (convertisseur personnalise):", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                return False
        else:
            print(f"❌ Convertisseur personnalise non trouve: {uf2conv_path}", file=sys.stderr)
            return False
    
    print(f"✅ Fichier UF2 cree: {uf2_file}")
    
    # Copier automatiquement vers le Pico si detecte
    pico_mount_path = detect_pico_uf2_disk()
    if pico_mount_path:
        import shutil
        dest_path = os.path.join(pico_mount_path, os.path.basename(uf2_file))
        try:
            shutil.copy2(uf2_file, dest_path)
            print(f"✅ Fichier UF2 copie vers le Pico: {dest_path}")
            print("🎉 Flashage termine! Le Pico va redemarrer automatiquement.")
        except Exception as e:
            print(f"⚠️ Erreur lors de la copie vers le Pico: {e}")
            print(f"📋 Copiez manuellement le fichier: {uf2_file}")
            print(f"📋 Vers le lecteur Pico: {pico_mount_path}")
    else:
        print(f"⚠️ Pico non detecte en mode BOOTSEL")
        print(f"📋 Copiez manuellement le fichier: {uf2_file}")
        print(f"📋 Vers le lecteur Pico une fois connecte en mode BOOTSEL")
    
    return True

def create_simple_uf2_guide(project_path):
    """Cree un guide simple pour flasher manuellement le Pico."""
    print("📖 Guide de flashage manuel Pico:")
    print()
    print("1. 🔄 Recompilez le projet avec la configuration correcte:")
    print(f"   cd {project_path}")
    print("   cargo build --release")
    print()
    print("2. 📁 Creez un nouveau projet Pico avec l'extension pour la bonne config:")
    print("   python3 main.py create --target pico --project-name nouveau-pico")
    print()
    print("3. 📋 Mode BOOTSEL:")
    print("   - Debranchez le Pico")
    print("   - Maintenez BOOTSEL enfonce")
    print("   - Rebranchez le Pico")
    print("   - Relâchez BOOTSEL")
    print("   - Le Pico apparaît comme lecteur USB")
    print()
    print("4. 🎯 Utilisez probe-rs en mode SWD (si debogueur disponible):")
    print(f"   cd {project_path}")
    print("   cargo run --release")
    print()
    return True

def flash_pico_uf2(project_path, elf_file):
    """Flashage du Pico en mode BOOTSEL (UF2) - Fallback manuel."""
    print("📋 Flashage Pico en mode BOOTSEL (UF2)")
    print("ℹ️  Ce mode necessite que le Pico soit connecte en mode BOOTSEL :")
    print("   1. Debrancher le Pico")
    print("   2. Maintenir le bouton BOOTSEL enfonce")
    print("   3. Reconnecter le Pico (tout en maintenant BOOTSEL)")
    print("   4. Relâcher BOOTSEL - le Pico apparaît comme lecteur USB")
    print()
    
    # Essayer d'abord la methode directe
    if flash_pico_uf2_direct(project_path):
        return True
    
    # Essayer la methode binutils avec fallback
    print("🔧 Methode directe echouee, tentative via cargo-binutils...")
    if flash_pico_uf2_binutils(project_path, elf_file):
        return True
    
    # Si toutes les methodes automatiques echouent, donner des instructions
    print("💡 Les methodes automatiques ont echoue.")
    print()
    return create_simple_uf2_guide(project_path)

def detect_pico_uf2_disk():
    """Detecte si le Pico est connecte en mode BOOTSEL (lecteur UF2)."""
    import glob
    
    # Chemins typiques pour un Pico en mode BOOTSEL
    pico_paths = [
        "/media/*/RPI-RP2",      # Linux
        "/Volumes/RPI-RP2",      # macOS
    ]
    
    for pattern in pico_paths:
        matches = glob.glob(pattern)
        if matches:
            path = matches[0]
            print(f"Found pico uf2 disk {path}")
            return path
    
    return None

def detect_pico_flash_mode():
    """Detecte la methode de flashage disponible pour le Pico."""
    # Priorite au mode BOOTSEL (plus simple, pas de materiel supplementaire)
    if check_tool_installed("elf2uf2-rs"):
        return "bootsel"
    
    # Fallback vers mode SWD si debogueur disponible
    if check_tool_installed("probe-rs"):
        return "swd"
    
    return None

def main():
    """Fonction principale pour parser les arguments et lancer les actions."""
    parser = argparse.ArgumentParser(description="Outil de build et flash pour Rust Embarque.")
    parser.add_argument("action", choices=["build", "flash", "create", "install-target", "install-tools", "setup"], 
                       help="L'action a effectuer.")
    parser.add_argument("--target", choices=TARGETS.keys(), help="La carte cible.")
    parser.add_argument("--project-path", default=".", help="Le chemin vers le projet Rust.")
    parser.add_argument("--project-name", help="Le nom du nouveau projet (pour l'action create).")
    
    args = parser.parse_args()
    project_path = args.project_path
    
    # --- Action: create ---
    if args.action == "create":
        if not args.project_name:
            print("❌ Le nom du projet est requis pour creer un nouveau projet")
            sys.exit(1)
        if not args.target:
            print("❌ La target est requise pour creer un nouveau projet")
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
            
            # Installation speciale pour Pico (les deux outils)
            if args.target == "pico":
                print("📋 Installation des outils pour Pico RP2040...")
                
                # Installer llvm-tools-preview pour cargo objcopy
                print("📋 Installation de llvm-tools-preview...")
                llvm_command = ["rustup", "component", "add", "llvm-tools-preview"]
                result = subprocess.run(llvm_command, capture_output=True, text=True)
                if result.returncode != 0:
                    print("⚠️ Impossible d'installer llvm-tools-preview")
                else:
                    print("✅ llvm-tools-preview installe")
                
                install_tool("elf2uf2-rs")  # Mode BOOTSEL (recommande)
                install_tool("probe-rs")    # Mode SWD (debogueur)
            else:
                # Installation normale pour les autres targets
                install_tool(target_config["flasher"])
        else:
            # Installer tous les outils
            for tool_name in TOOLS.keys():
                install_tool(tool_name)
                
    # --- Action: setup ---
    elif args.action == "setup":
        print("🔧 Configuration de l'environnement de developpement...")
        
        # Installer toutes les targets
        for config in TARGETS.values():
            install_rust_target(config["rust_target"])
            
        # Installer tous les outils
        for tool_name in TOOLS.keys():
            install_tool(tool_name)
            
        print("✅ Environnement configure avec succes!")
        
    # Actions necessitant une target
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
            print(f"⚡ Televersement sur {args.target}...")
            
            # 1. Trouver le fichier binaire (.elf)
            elf_file = find_elf_file(project_path, target_config["rust_target"])
            if not elf_file:
                sys.exit(1)
            
            print(f"📁 Fichier binaire trouve : {elf_file}")

            # 2. Traitement special pour Pico (RP2040)
            if args.target == "pico":
                flash_mode = detect_pico_flash_mode()
                
                if flash_mode == "bootsel":
                    # Mode BOOTSEL (recommande, plus simple)
                    print("🎯 Utilisation du mode BOOTSEL (UF2)")
                    if flash_pico_uf2(project_path, elf_file):
                        print("✅ Flashage Pico termine avec succes!")
                    else:
                        sys.exit(1)
                        
                elif flash_mode == "swd":
                    # Mode SWD avec probe-rs (necessite debogueur)
                    print("🎯 Utilisation du mode SWD avec probe-rs")
                    print("⚠️  Ce mode necessite un debogueur SWD connecte au Pico")
                    flash_command = ["probe-rs", "run", "--chip", target_config["chip"], elf_file]
                    run_command(flash_command, project_path)
                    
                else:
                    # Aucun outil de flashage disponible
                    print(f"❌ Aucun outil de flashage pour Pico n'est installe.", file=sys.stderr)
                    print(f"", file=sys.stderr)
                    print(f"💡 Solutions pour Pico RP2040:", file=sys.stderr)
                    print(f"   1. Mode BOOTSEL (recommande): cargo install elf2uf2-rs --locked", file=sys.stderr)
                    print(f"   2. Mode SWD (avec debogueur): cargo install probe-rs-tools --locked", file=sys.stderr)
                    print(f"   3. Installation automatique: python3 {sys.argv[0]} install-tools --target pico", file=sys.stderr)
                    print(f"   4. Configuration complete: python3 {sys.argv[0]} setup", file=sys.stderr)
                    sys.exit(1)
                    
            # 3. Traitement pour ESP32-C3
            elif args.target == "esp32c3":
                flasher = target_config["flasher"]
                if not check_tool_installed(flasher):
                    print(f"❌ L'outil de flashage '{flasher}' n'est pas installe.", file=sys.stderr)
                    print(f"", file=sys.stderr)
                    print(f"💡 Solutions:", file=sys.stderr)
                    print(f"   1. Installation manuelle: cargo install {flasher}", file=sys.stderr)
                    print(f"   2. Installation automatique: python3 {sys.argv[0]} install-tools --target {args.target}", file=sys.stderr)
                    print(f"   3. Configuration complete: python3 {sys.argv[0]} setup", file=sys.stderr)
                    sys.exit(1)
                
                flash_command = ["espflash", "flash", "-M", "dio", elf_file]
                run_command(flash_command, project_path)
    else:
        print("❌ Target requise pour cette action")
        sys.exit(1)


if __name__ == "__main__":
    main()