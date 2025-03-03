import sys

def getRegisterMod(mod, reg, w):
    match mod:
        case '00':
            return "mod00"
        case '01':
            return "mod01"
        case '10':
            return "mod10"
        case '11':
            return getRegister(reg, w)

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
    opcode = instruction[0:4]
    match opcode:
        case '1011':
            w = instruction[4]
            reg = instruction[5:8]
            # match w:
            #     case '0':
            data = instruction[8:]
            print(f'decodeInst4 w {w}, reg {reg}, data {data}')
            decodeInstruction4(opcode, w, reg, data)
            return
    opcode = instruction[0:6]
    match opcode:
        case '100010':
            d = instruction[6]
            w = instruction[7]
            second_byte = getNextChunk(8)
            mod = second_byte[0:2]
            reg = second_byte[2:5]
            rm = second_byte[5:8]
            print(f'mov {getRegister(rm, w).lower()} {getRegister(reg, w).lower()}')
            return

def decodeInstruction4(opcode, w, reg, data):
    match w:
        case '0':
            print(f'mov {getRegister(reg, w).lower()}, {int(data, 2)}')
        case '1':
            print(f'mov {getRegister(reg, w).lower()}, {int(data, 2)}')

def decodeInstruction6(opcode, d, w, mod, reg, rm):
    match opcode:
        case '100010':
            #print(f'register {getRegister(reg, w)}')
            print(f'mov {getRegister(rm, w).lower()} {getRegister(reg, w).lower()}')
            return "Register/memory to/from memory"
        case _: 
            print(f'')
            return "Something's wrong with the internet"

# binary_representation = ""

def getNextChunk(chunk_size):
    global binary_representation
    next_chunk = binary_representation[0:chunk_size]
    binary_representation = binary_representation[chunk_size:]
    return next_chunk

with open(sys.argv[1], 'rb') as file:
    data = file.read()
    binary_representation = ''.join(format(byte, '08b') for byte in data)
    # print(binary_representation)
    chunk_size = 8
    next_chunk = getNextChunk(chunk_size)
    checkInstruction(next_chunk)
    # binary_chunks = [binary_representation[i:i+chunk_size] for i in range(0, len(binary_representation), chunk_size)]

    # for instruction in binary_chunks:
        # print(f"Instruction: {instruction}")
        # checkInstruction(instruction)