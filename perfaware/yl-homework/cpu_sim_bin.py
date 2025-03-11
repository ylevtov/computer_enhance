import sys

effectiveAddresses = ["BX + SI", "BX + DI", "BP + SI", "BP + DI", "SI", "DI", "BP", "BX"]
registers = ["AL", "CL", "DL", "BL", "AH", "CH", "DH", "BH", "AX", "CX", "DX", "BX", "SP", "BP", "SI", "DI"]

def getRegisterMod(**kwargs):
    mod = kwargs["mod"]
    reg = kwargs["reg"]
    w = kwargs["w"]
    rm = kwargs["rm"]
    match mod:
        case '00':
            return getEffectiveAddress(rm)
        case '01':
            disp_lo = kwargs["disp_lo"]
            return getEffectiveAddress(rm, disp_lo, "", w)
        case '10':
            disp_lo = kwargs["disp_lo"]
            disp_hi = kwargs["disp_hi"]
            return getEffectiveAddress(rm, disp_lo, disp_hi, w)
        case '11':
            return getRegister(reg, w)

def getEffectiveAddress(rm, disp_lo="", disp_hi="", w=""):
    disp_int = 0
    displacement = ""
    if (disp_hi):
        disp_int = int(disp_hi+disp_lo, 2)
        if (w == "1"):
            disp_int -= int("1111111111111111", 2) + 1
    elif (disp_lo):
        disp_int = int(disp_lo, 2)
        if (w == "1"):
            disp_int -= (int("1111111111111111", 2) + 1) % 65536
    if (disp_int > 0):
        displacement = f" + {disp_int}"
    elif (disp_int < 0):
        displacement = f" - {abs(disp_int)}"

    return f'[{effectiveAddresses[int(rm, 2)]}{displacement}]'

def getRegister(reg, w):
    return registers[int(f'{w}{reg}', 2)]

def checkInstruction(instruction):
    # print(f'checking instruction {instruction}')
    if (instruction[0:4] == "1011"):
        w = instruction[4]
        reg = instruction[5:8]
        match w:
            case '0':
                data = getNextChunk(8)
            case '1':
                dataLSB = getNextChunk(8)
                dataMSB = getNextChunk(8)
                data = dataMSB+dataLSB
        # print(f'decodeInst4 w {w}, reg {reg}, data {data}')
        decodeInstruction4(w, reg, data)
    elif (instruction[0:6] == "100010"):
        d = instruction[6]
        w = instruction[7]
        second_byte = getNextChunk(8)
        # print(f'{instruction} {second_byte}')
        decodeRegMemToFromRegMem(d, w, second_byte)
        # print(f'mov {getRegister(rm, w).lower()}, {getRegister(reg, w).lower()}')
    elif (instruction[0:7] == "1100011"):
        w = instruction[7]
        decodeImmediateToRegMem(w)
    else:
        print(f'Non-matched opcode {instruction}')

def decodeInstruction4(w, reg, data):
    print(f'mov {getRegister(reg, w).lower()}, {int(data, 2)}')

def decodeImmediateToRegMem(w):
    second_byte = getNextChunk(8)
    mod = second_byte[0:2]
    rm = second_byte[5:8]
    kwargs = {"mod":mod, "rm":rm, "w":w, "reg":-1}
    if (mod == "00"):
        data = getNextChunk(8)
        print(f'mov {getRegisterMod(**kwargs).lower()}, byte {int(data, 2)}')
    elif (mod == "10"):
        kwargs["disp_lo"] = getNextChunk(8)
        kwargs["disp_hi"] = getNextChunk(8)
        data = getNextChunk(8)
        print(f'mov {getRegisterMod(**kwargs).lower()}, byte {int(data, 2)}')
    else:
        print(f'modaaa {mod}')
    # disp_lo = getNextChunk(8)
    # data_lsb = getNextChunk(8)
    # print(f'Immediate to reg/mem {second_byte}, lo {disp_lo}, data {data_lsb}')
    # if (w == "1"):
    #     data_msb = getNextChunk(8)

def decodeRegMemToFromRegMem(d, w, second_byte):
    mod = second_byte[0:2]
    reg = second_byte[2:5]
    rm = second_byte[5:8]
    kwargs = {"mod":mod, "reg":reg, "rm":rm, "w":w}
    # print(f'd {d}, w {w}, mod {mod}, reg {reg}, rm {rm}')
    match mod:
        case '11':
            match d:
                case '0':
                    print(f'mov {getRegister(rm, w).lower()}, {getRegister(reg, w).lower()}')
                case '1':
                    print(f'mov {getRegister(reg, w).lower()}, {getRegister(rm, w).lower()}')
        case '01':
            kwargs["disp_lo"] = getNextChunk(8)
            match d:
                case '0':
                    print(f'mov {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                case '1':
                    print(f'mov {getRegister(reg, w).lower()}, {getRegisterMod(**kwargs).lower()}')
        case '10':
            kwargs["disp_lo"] = getNextChunk(8)
            kwargs["disp_hi"] = getNextChunk(8)
            match d:
                case '0':
                    print(f'mov {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                case '1':
                    print(f'mov {getRegister(rm, w).lower()}, {getRegisterMod(**kwargs).lower()}')
        case '00':
            match rm:
                case "110":
                    print(f'special case 16 bit displacement')
                    match d:
                        case '1':
                            kwargs["disp_lo"] = getNextChunk(8)
                            kwargs["disp_hi"] = getNextChunk(8)
                            print(f'{kwargs["disp_lo"]} {kwargs["disp_hi"]}')
                            kwargs["rm"] = reg
                            print(f'movsc {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                case _:
                    match d:
                        case '0':
                            print(f'mov00 {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                        case '1':
                            print(f'mov00 {getRegister(rm, w).lower()}, {getRegisterMod(**kwargs).lower()}')


def getNextChunk(chunk_size):
    global binary_representation
    next_chunk = binary_representation[0:chunk_size]
    binary_representation = binary_representation[chunk_size:]
    return next_chunk

def checkNextChunk():
    global binary_representation
    # print(f'checking next_chunk from {binary_representation}')
    next_chunk = getNextChunk(8)
    checkInstruction(next_chunk)

def main():
    print(f'{effectiveAddresses[0]}, {int("010", 2)}')
    with open(sys.argv[1], 'rb') as file:
        data = file.read()
        global binary_representation
        binary_representation = ''.join(format(byte, '08b') for byte in data)
        print("#############")
        chunk_size = 8
        while len(binary_representation) >= 8:
            checkNextChunk()

if __name__ == "__main__":
    main()