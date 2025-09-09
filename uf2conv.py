#!/usr/bin/env python3
"""
UF2 converter utility - convertit un binaire en format UF2
Basé sur le script officiel Microsoft UF2
"""
import sys
import struct
import os

UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157
UF2_MAGIC_END = 0x0AB16F30

RP2040_FAMILY_ID = 0xe48bff56

def convert_to_uf2(data, start_addr=0x10000000, family_id=RP2040_FAMILY_ID):
    """Convertit des données binaires en format UF2."""
    chunks = [data[i:i+256] for i in range(0, len(data), 256)]
    uf2_blocks = []
    
    for block_no, chunk in enumerate(chunks):
        # Pad le chunk à 256 bytes si nécessaire
        if len(chunk) < 256:
            chunk += b'\x00' * (256 - len(chunk))
        
        # Créer le header UF2
        header = struct.pack("<8I",
            UF2_MAGIC_START0,          # magic start 0
            UF2_MAGIC_START1,          # magic start 1  
            0x2000,                    # flags (family ID présent)
            start_addr + block_no * 256, # adresse target
            256,                       # payload size
            block_no,                  # block number
            len(chunks),               # nombre total de blocks
            family_id                  # family ID (RP2040)
        )
        
        # Créer le footer
        footer = struct.pack("<I", UF2_MAGIC_END)
        
        # Padding pour arriver à 512 bytes
        padding = b'\x00' * (512 - len(header) - len(chunk) - len(footer))
        
        block = header + chunk + padding + footer
        uf2_blocks.append(block)
    
    return b''.join(uf2_blocks)

def main():
    if len(sys.argv) != 3:
        print("Usage: uf2conv.py <input.bin> <output.uf2>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"❌ Fichier d'entrée non trouvé: {input_file}")
        sys.exit(1)
    
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Convertir en UF2
        uf2_data = convert_to_uf2(data)
        
        with open(output_file, 'wb') as f:
            f.write(uf2_data)
        
        print(f"✅ Conversion réussie: {input_file} → {output_file}")
        print(f"📊 {len(data)} bytes → {len(uf2_data)} bytes UF2")
        
    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()