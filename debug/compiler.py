import re

def parse_mor(content):
    presets = {}
    dialogues = []
    options = {}
    current_section = None
    current_preset = None
    current_dialogue = None
    current_option = None

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测当前部分
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            continue

        if current_section == 'default':
            if line.startswith('@'):
                current_preset = line[1:]
                presets[current_preset] = []
            else:
                if '=' in line:
                    key, val = line.split('=', 1)
                    presets[current_preset].append((key.strip(), val.strip()))
                else:
                    presets[current_preset].append((None, line.strip()))

        elif current_section == 'dialogue':
            if line.startswith('@'):
                parts = line[1:].split(',', 1)
                dlg_name = parts[0]
                preset_name = parts[1].strip() if len(parts) > 1 else None
                current_dialogue = {
                    'name': dlg_name,
                    'preset': preset_name,
                    'params': []
                }
                dialogues.append(current_dialogue)
            else:
                if '=' in line:
                    key, val = line.split('=', 1)
                    current_dialogue['params'].append((key.strip(), val.strip()))
                else:
                    current_dialogue['params'].append((None, line.strip()))

        elif current_section == 'option':
            if line.startswith('@'):
                current_option = line[1:]
                options[current_option] = []
            else:
                if '=' in line:
                    key, val = line.split('=', 1)
                    options[current_option].append((key.strip(), val.strip()))
                else:
                    options[current_option].append((line.strip(), ''))

    return presets, dialogues, options

def process_dialogue(dialogue, presets):
    # 合并 preset 参数
    preset_params = []
    if dialogue['preset'] and dialogue['preset'] in presets:
        preset_params = presets[dialogue['preset']]

    all_params = preset_params + dialogue['params']
    processed_lines = []

    for param in all_params:
        if param[0] is None:
            # 将 sac 替换为 stop 和 clear
            if param[1] == 'sac':
                processed_lines.append('stop')
                processed_lines.append('clear')
            else:
                processed_lines.append(param[1])
            continue

        key, value = param
        # 处理颜色转换
        if key == 'hexcolour':
            hex_val = value.lstrip('#')
            dec_val = int(hex_val, 16)
            processed_lines.append(f'colour={dec_val}')
        elif key == 'rgbcolour':
            r, g, b = map(int, re.findall(r'\d+', value))
            dec_val = (r << 16) | (g << 8) | b
            processed_lines.append(f'colour={dec_val}')
        elif key == 'text':
            # 将 \n 替换为 <ls#>
            value = value.replace('\\n', '\n')
            processed_lines.append(f'{key}={value}')
        else:
            processed_lines.append(f'{key}={value}')

    return processed_lines

def generate_chat(dialogues, presets):
    blocks = []
    for dlg in dialogues:
        lines = process_dialogue(dlg, presets)
        blocks.append('<nl#>'.join(lines))
    return '<nc#>'.join(blocks)

def generate_indexes(dialogues, options):
    name_to_idx = {dlg['name']: idx for idx, dlg in enumerate(dialogues)}
    indexes = []
    for opt_name, items in options.items():
        indexes.append(f'@{opt_name}')
        for key, val in items:
            if key in name_to_idx:
                indexes.append(f'{name_to_idx[key]}={val}')
            else:
                indexes.append(f'{key}={val}')
    return '\n'.join(indexes)

def main():
    with open('/home/zy/桌面/GAL_demo/debug/mor.txt', 'r', encoding='utf-8') as f:
        mor_content = f.read()

    presets, dialogues, options = parse_mor(mor_content)

    # 生成 chat.txt
    chat_content = generate_chat(dialogues, presets)
    #在最后设置一个<nl#>可以防止bug
    chat_content = chat_content +"<nl#>"
    with open('/home/zy/桌面/GAL_demo/debug/chat.txt', 'w', encoding='utf-8') as f:
        f.write(chat_content)

    # 生成 indexes.txt
    indexes_content = generate_indexes(dialogues, options)
    with open('/home/zy/桌面/GAL_demo/debug/indexes.txt', 'w', encoding='utf-8') as f:
        f.write(indexes_content)

if __name__ == '__main__':
    main()