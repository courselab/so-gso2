labels_list = {
    ".": b"\xa2"
}

opcode_map = {
    "movbah": b"\xb4",
    "movbal": b"\x8a",
    "movw": b"\xbe\x00",
    "cmp" : b"\x3c",
    "je"  : b"\x74",
    "int" : b"\xcd",
    "add" : b"\x83",
    "jmp" : b"\xeb",
    "hlt" : b"\xf4",
}

def get_label(line):
    # Retorna uma string com label.
    index_1 = line.find(":")
    if index_1 > 0:
        label = line[:index_1]
        return label
    return ""

def get_code(line):
    # Retorna uma string com código.
    index_2 = line.find(" ")  
    if index_2 > 0:
        opcode = line[:index_2]
        return opcode

    return line


def get_value_by_code(code, line):
    # Retorna uma string com o valor definido na instrução, dado um código.
    temp_line = line[len(code):]
    if len(temp_line) > 0:
        index_dollar = temp_line.find("$")
        index_comma = temp_line.find(",")
        if index_comma > 0:
            value = temp_line[index_dollar+1:index_comma]
            return clean_string(value)
        return clean_string(temp_line[index_dollar+1:])
    return ""

def get_value_by_directive(code, line):
    # Retorna uma lista de strings com o valor definido na instrução, dado um diretiva.
    temp_line = line[len(code):]
    if code == ".string":
        start_index = temp_line.find('"') + 1
        end_index = temp_line.rfind('"')
        string = temp_line[start_index:end_index]
        return [string]
    else:
        if len(temp_line) > 0:
            split_list = temp_line.split(",")
            for i in range(len(split_list)):
                split_list[i] = clean_string(split_list[i])
            return split_list
    return ""

def get_reg_by_code(code, value, line):
    # Retorna uma string com endereço de destino, dado um código. 
    temp_line = line[len(code) + len(value) :]
    percentage_index = temp_line.find("%")
    if percentage_index > 0:
        reg = temp_line[percentage_index+1:]
        return clean_string(reg)
    return ""

def clean_string(string):
    # Retorna uma string sem espaços e tabulação
    empty_index = string.find(" ")
    while empty_index != -1:
        string = string.replace(" ", "")
        empty_index = string.find(" ")
    
    t_index = string.find("\t")
    while t_index != -1:
        string = string.replace("\t", "")
        t_index = string.find("\t")

    return string

def remove_comments(line):
    # Retorna uma string sem comentários
    comment_index = line.find("#")
    if comment_index < 0:
        return line
    elif comment_index > 0:
        return line[:comment_index]
    else:
        return ""

def string_to_byte(value):
    # Converte string para byte
    if len(value) > 0:
        byte = bytearray(1)
        hex_value = int(value, 16)
        byte[0] = hex_value
        return byte

def word_to_list(string):
    # Retorna uma lista de bytes para um valor da diretiva .word
    byte_list = []
    hex_string = ""
    if string.startswith("0x"):
        hex_string = string[2:]
    for i in range(len(hex_string)):
        if i % 2 != 0:
            byte_list.append(hex_string[:i+1])
            hex_string = hex_string[2:]
    return byte_list

def get_fill_args(value):
    # Retorna os argumentos size e valor para diretiva .fill
    start_index = value[0].find('(') + 1
    end_index = value[0].rfind(')')
    numbers = value[0][start_index:end_index]
    expr = value[0][start_index-1:end_index+1]
    nums = numbers.split("-")
    if len(nums) > 1:
        nums[0] = labels_list[nums[0]]
        nums[1] = labels_list[nums[1]]
        res = nums[0][0] - nums[1][0]
    value[0] = value[0].replace(expr, str(res))
    nums = value[0].split("-")
    if len(nums) > 1:
        res = int(nums[0]) - int(nums[1])
    
    val = int(value[1])
    
    return res, val

def get_value_from_mov(value):
    # Retorna byte para valor de código mov.
    start_index = value.find('(') + 1
    end_index = value.rfind(')')
    if start_index >= 0 and end_index >=0:
        string = value[start_index:end_index]
        string = string.replace("%", "")
        #print(string)
        temp_string = value[:start_index-1]
        #print(temp_string)
        val = b"\x84" + labels_list[temp_string] + b"\x7c"
        return val
    return string_to_byte(value)

def assemble(input_file="hw.S", output_file="hw.bin"):

    machine_code = b""
    flat_binary = ""
    
    # Vamos ler cada linha do arquivo ".asm" e processar somente labels
    with open(input_file, "r") as file:
        for line in file:
            line = line.strip()
            new_line = remove_comments(line)
            if len(new_line) == 0:
                # Linha só de comentários, nada para processar 
                continue
            else:
                # Vamos tratar os labels existentes.
                label = get_label(new_line)
                if len(label) > 0:
                    #continue
                    #value = get_value_by_code(code, new_line)
                    if label == "_start":
                        labels_list[label] = b"\x7c"
                        continue
                    elif label == "loop":
                        labels_list[label] = b"\xf1"
                        continue
                    elif label == "halt":
                        continue
                    elif label == "msg":
                        labels_list[label] = b"\x17"
                        continue

        # Vamos ler cada linha do arquivo ".asm" e processar as instruções
        file.seek(0)
        for line in file:
            line = line.strip()
            new_line = remove_comments(line)

            if len(new_line) == 0:
                # Linha só de comentários, nada para processar 
                continue
            else:
                # Aqui só temos diretivas do programa e instruções, vamos processá-las
                code = get_code(new_line)                
                if code.startswith("."):
                    # Vamos tratar as diretivas code16, global, string, fill e word
                    if code == ".code16":
                        # TODO: Tratar
                        continue
                    elif code == ".global":
                        # TODO: Tratar
                        continue
                    elif code == ".string":
                        # Devemos adicionar a string definida ao string de bytes
                        value = get_value_by_directive(code, new_line)
                        string = bytearray(value[0], 'utf-8') + b'\x00\x00\x00\x00'
                        data_bytes = machine_code + string
                    elif code == ".fill":
                        # Devemos adicionar o padding de zeros a string de bytes
                        value = get_value_by_directive(code, new_line)
                        size, val = get_fill_args(value)
                        padding = bytearray(val)*size
                        data_bytes += padding
                    elif code == ".word":
                        # Devemos adicionar o value da diretiva a string de bytes
                        value = get_value_by_directive(code, new_line)[0]
                        byte_list = word_to_list(value)
                        for string in byte_list[::-1]:
                            byte = string_to_byte(string)  
                            data_bytes += byte
                        flat_binary = data_bytes 
                else:
                    # Vamos tratar os opcodes definidos no opcode_map
                    value = get_value_by_code(code, new_line)
                    reg = get_reg_by_code(code, value, new_line)
                    #print(code + " " + value + " " + reg)
                    
                    if code == "movb":
                        code = "movb" + reg 
                        machine_code += opcode_map[code]
                        machine_code += get_value_from_mov(value)
                    elif code == "movw":
                        machine_code += opcode_map[code]
                        machine_code += string_to_byte(value)
                    elif code == "cmp":
                        machine_code += opcode_map[code]
                        machine_code += string_to_byte(value)
                    elif code == "je":
                        machine_code += opcode_map[code]
                        if value == "halt":
                            value = b"\x07"
                            machine_code += value
                    elif code == "int":
                        machine_code += opcode_map[code]
                        machine_code += string_to_byte(value)
                    elif code == "add":
                        machine_code += opcode_map[code]
                        inj = b"\xc6"
                        machine_code += inj
                        machine_code += string_to_byte(value)               
                    elif code == "hlt":
                        machine_code += opcode_map[code]
                    elif code == "jmp":
                        machine_code += opcode_map[code]
                        if value == "loop":
                            value = labels_list[value]
                            machine_code += value
                        if value == "halt":
                            value = b"\xfd"
                            machine_code += value
                    else:
                        # TODO: Código não identificado, precisa parsear
                        pass  

    with open(output_file, "wb") as f:
        f.write(flat_binary)

if __name__ == "__main__":
    assemble()
