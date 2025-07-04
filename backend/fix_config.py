import re

with open('app/config.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar e corrigir linha com MIN_
for i, line in enumerate(lines):
    if 'MIN_' in line and line.strip().endswith('MIN_'):
        # Provavelmente uma linha quebrada, corrigir
        if i < len(lines) - 1:
            # Juntar com próxima linha
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith('#'):
                lines[i] = line.rstrip() + next_line + '\n'
                lines[i + 1] = ''
                print(f"✅ Corrigida linha {i + 1}: {line.strip()}")
        else:
            # Remover linha incompleta
            lines[i] = ''
            print(f"✅ Removida linha incompleta {i + 1}")

# Remover linhas vazias extras
lines = [line for line in lines if line.strip() != '']

with open('app/config.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Config.py corrigido")

