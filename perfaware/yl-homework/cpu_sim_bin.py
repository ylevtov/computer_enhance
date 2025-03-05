import sys

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
            disp_int -= int("11111111", 2) + 1
    if (disp_int > 0):
        displacement = f" + {disp_int}"
    elif (disp_int < 0):
        displacement = f" - {abs(disp_int)}"

    match rm:
        case '000':
            return f'[BX + SI{displacement}]'
        case '001':
            return f'[BX + DI{displacement}]'
        case '010':
            return f'[BP + SI{displacement}]'
        case '011':
            return f'[BP + DI{displacement}]'
        case '100':
            return f'[SI{displacement}]'
        case '101':
            return f'[DI{displacement}]'
        case '110':
            return f'[BP{displacement}]'
        case '111':
            return f'[BX{displacement}]'

def getRegister(reg, w):
    match w:
        case '0':
            match reg:
                case '000':
                    return 'AL'
                case '001':
                    return 'CL'
                case '010':
                    return 'DL'
                case '011':
                    return 'BL'
                case '100':
                    return 'AH'
                case '101':
                    return 'CH'
                case '110':
                    return 'DH'
                case '111':
                    return 'BH'
        case '1':
            match reg:
                case '000':
                    return 'AX'
                case '001':
                    return 'CX'
                case '010':
                    return 'DX'
                case '011':
                    return 'BX'
                case '100':
                    return 'SP'
                case '101':
                    return 'BP'
                case '110':
                    return 'SI'
                case '111':
                    return 'DI'

def checkInstruction(instruction):
    # print(f'checking instruction {instruction}')
    opcode = instruction[0:4]
    match opcode:
        case '1011':
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
            decodeInstruction4(opcode, w, reg, data)
    opcode = instruction[0:6]
    match opcode:
        case '100010':
            d = instruction[6]
            w = instruction[7]
            second_byte = getNextChunk(8)
            # print(f'{instruction} {second_byte}')
            decodeRegMemToFromRegMem(d, w, second_byte)
            # print(f'mov {getRegister(rm, w).lower()}, {getRegister(reg, w).lower()}')

def decodeInstruction4(opcode, w, reg, data):
    print(f'mov {getRegister(reg, w).lower()}, {int(data, 2)}')

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
            disp_lo = getNextChunk(8)
            kwargs["disp_lo"] = disp_lo
            match d:
                case '0':
                    print(f'mov {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                case '1':
                    print(f'mov {getRegister(reg, w).lower()}, {getRegisterMod(**kwargs).lower()}')
        case '10':
            disp_lo = getNextChunk(8)
            disp_hi = getNextChunk(8)
            kwargs["disp_lo"] = disp_lo
            kwargs["disp_hi"] = disp_hi
            match d:
                case '0':
                    print(f'mov 149 {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                case '1':
                    print(f'mov {getRegister(rm, w).lower()}, {getRegisterMod(**kwargs).lower()}')
        case '00':
            match d:
                case '0':
                    print(f'mov00 {getRegisterMod(**kwargs).lower()}, {getRegister(reg, w).lower()}')
                case '1':
                    print(f'mov00 {getRegister(rm, w).lower()}, {getRegisterMod(**kwargs).lower()}')

# binary_representation = ""

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