import unittest
from io import StringIO
import sys
from cpu_sim_bin import getRegisterMod, getEffectiveAddress, getRegister, decodeInstruction4, decodeRegMemToFromRegMem, checkNextChunk

class TestInstructionDecoding(unittest.TestCase):

    def test_getEffectiveAddress(self):
        self.assertEqual(getEffectiveAddress('000'), '[BX + SI]')
        self.assertEqual(getEffectiveAddress('001'), '[BX + DI]')
        self.assertEqual(getEffectiveAddress('010'), '[BP + SI]')
        self.assertEqual(getEffectiveAddress('011'), '[BP + DI]')
        self.assertEqual(getEffectiveAddress('100'), '[SI]')
        self.assertEqual(getEffectiveAddress('101'), '[DI]')
        self.assertEqual(getEffectiveAddress('110'), '[BP]')
        self.assertEqual(getEffectiveAddress('111'), '[BX]')

    def test_getRegister(self):
        self.assertEqual(getRegister('000', '0'), 'AL')
        self.assertEqual(getRegister('001', '0'), 'CL')
        self.assertEqual(getRegister('010', '0'), 'DL')
        self.assertEqual(getRegister('011', '0'), 'BL')
        self.assertEqual(getRegister('100', '0'), 'AH')
        self.assertEqual(getRegister('101', '0'), 'CH')
        self.assertEqual(getRegister('110', '0'), 'DH')
        self.assertEqual(getRegister('111', '0'), 'BH')

        self.assertEqual(getRegister('000', '1'), 'AX')
        self.assertEqual(getRegister('001', '1'), 'CX')
        self.assertEqual(getRegister('010', '1'), 'DX')
        self.assertEqual(getRegister('011', '1'), 'BX')
        self.assertEqual(getRegister('100', '1'), 'SP')
        self.assertEqual(getRegister('101', '1'), 'BP')
        self.assertEqual(getRegister('110', '1'), 'SI')
        self.assertEqual(getRegister('111', '1'), 'DI')

    def test_getRegisterMod(self):
        self.assertEqual(getRegisterMod('00', '000', '1', '000'), '[BX + SI]')
        self.assertEqual(getRegisterMod('00', '000', '1', '001'), '[BX + DI]')
        self.assertEqual(getRegisterMod('11', '000', '1', '000'), 'AX')

    def test_decodeInstruction4(self):
        output = StringIO()
        sys.stdout = output
        decodeInstruction4('1011', '0', '000', '00000001')  # mov al, 1
        sys.stdout = sys.__stdout__
        self.assertEqual(output.getvalue().strip(), 'mov al, 1')

    def test_decodeRegMemToFromRegMem(self):
        output = StringIO()
        sys.stdout = output
        decodeRegMemToFromRegMem('1', '1', '11000000')  # mov ax, ax
        sys.stdout = sys.__stdout__
        self.assertTrue('mov 11 ax, ax' in output.getvalue().strip())

    def test_decodeListing37(self):
        output = StringIO()
        sys.stdout = output
        import cpu_sim_bin
        cpu_sim_bin.binary_representation = '1000100111011001'
        checkNextChunk() # mov cx, bx
        sys.stdout = sys.__stdout__
        self.assertTrue('mov 11 cx, bx' in output.getvalue().strip())

if __name__ == '__main__':
    unittest.main()
