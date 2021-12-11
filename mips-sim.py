import sys
import copy
if len(sys.argv) == 5:
    cache_num = sys.argv[1]
    inst_num = sys.argv[2]
    file_path1 = sys.argv[3]
    file_path2 = sys.argv[4]
else:
    cache_num = sys.argv[1]
    inst_num = sys.argv[2]
    file_path1 = sys.argv[3]
FunctSet = {"100000": "add", "100001": "addu", "100100": "and", "011010": "div", "011011": "divu", "001001": "jalr",
            "001000": "jr", "010000": "mfhi", "010010": "mflo",
            "010001": "mthi", "010011": "mtlo", "011000": "mult", "011001": "multu", "100111": "nor", "100101": "or",
            "000000": "sll", "000100": "sllv", "101010": "slt", "101011": "sltu",
            "000011": "sra", "000111": "srav", "000010": "srl", "000110": "srlv", "100010": "sub", "100011": "subu",
            "001100": "syscall", "100110": "xor"}

OpcodeSet = {"001000": "addi", "001001": "addiu", "001100": "andi", "000100": "beq", "000101": "bne", "100000": "lb",
             "100100": "lbu", "100001": "lh", "100101": "lhu", "001111": "lui", "100011": "lw",
             "001101": "ori", "101000": "sb", "001010": "slti", "001011": "sltiu", "101001": "sh", "101011": "sw",
             "001110": "xori", "000010": "j", "000011": "jal"}

Memory_size = 2**16 #64KB

#data memory

if len(sys.argv) == 4:
    with open(file_path2, "rb") as f:
        datafile = f.read()
    f.close()
    total_inst = int(len(datafile)/4)
    hexacode = ""

    for i in range(len(datafile)):
        if datafile[i]<16:
            hexacode += '0'
            hexacode += str(format(datafile[i], 'x'))
        else:
            hexacode += str(format(datafile[i],'x'))

    # print(hexacode)
    # for i in range(total_inst):
    #     binarycode = ""
    #     for j in range(4):
    #         hx = str(format(datafile[i*4 + j], 'x'))
    #         hexacode += '0'*(2-len(hx))
    #         hexacode += hx
    #         val = datafile[i*4 + j]
    # if len(datafile)/4 !=0:
    #     hx = str(format(datafile[total_inst * 2 + ], 'x'))
    #     hexacode += hx


    DataMemory = hexacode
    DataMemory = '{0:F<1310720}'.format(DataMemory)
    # DataMemory = '{0:F<1310}'.format(DataMemory)


    DataMemory = list(DataMemory)

with open(file_path1, "rb") as f:
    binarycodeT = f.read()

f.close()
total_inst = int(len(binarycodeT)/4)
regVal = [0 for i in range(32)]
inst = []
for i in range(total_inst):
    binarycode = ""
    hexacode = ""
    for j in range(4):
        hx = str(format(binarycodeT[i*4 + j], 'x'))
        hexacode += '0'*(2-len(hx))
        hexacode += hx
        val = binarycodeT[i*4 + j]
        bc = format(val, 'b')
        binarycode += '0'*(8-len(bc))
        binarycode += bc
    # print("bincode: ",binarycode)
    # print("hexacode:",hexacode)
    value = int(binarycode,2)
    opcode = copy.deepcopy(binarycode[0:6])
    rs = copy.deepcopy(binarycode[6:11])
    rt = copy.deepcopy(binarycode[11:16])
    rd = copy.deepcopy(binarycode[16:21])
    shamt = copy.deepcopy(binarycode[21:26])
    funct = copy.deepcopy(binarycode[26:32])
    coa = copy.deepcopy(binarycode[16:32]) #constant or address
    coa2 = copy.deepcopy(binarycode[16:32])
    sign =1
    if coa[0]=='1':
        sign *= -1
        new_coa = ""
        for s in coa:
            if s=='0':
                new_coa +="1"
            else:
                new_coa += "0"
        coa = new_coa
    jal_address = binarycode[6:32]
    instruction = ""
    register1 = -1
    register2 = -1
    register3 = -1

    # ◼ Part1:
    #   ❖ Arithmetic / logical: add, addu, sub, subu, and, or, slt, sltu
    #   ❖ Arithmetic / logical with immediate: addi, addiu, andi, ori, lui, slti, sltiu
    #   ❖ Control transfer: beq, bne, j, jal, jr
    #   ❖ Shift instructions: sll, srl
    # ◼ Part2:
    #   ❖ Memory access: lw, sw
    # ◼ Part3:
    #   ❖ System call instruction: syscall
    R_Type = 0#R = 1 ,I&J = 0
    if opcode!="000000":#ij_type
        if opcode in OpcodeSet:
            instruction = OpcodeSet[opcode]
            register1 = int(rs, 2)
            register2 = int(rt, 2)
            if sign >0:
                constant = int(coa, 2)*sign
            else:
                constant = (int(coa, 2)+1) * sign
            if instruction =='lw' or instruction =='sw':#or instruction == "sh" or instruction=='lb' or instruction=='lbu' or instruction=='sb' or instruction=='lh'
                inst.append(f'{instruction} ${register2}, {constant}(${register1})')
            elif instruction == "addi" or instruction == "slti":
                inst.append(f'{instruction} ${register2}, ${register1}, {constant}')
            elif instruction == "ori" or instruction == "andi":
                constant = int(coa2, 2)
                inst.append(f'{instruction} ${register2}, ${register1}, {constant}')
            elif instruction == "addiu" or instruction == "sltiu":
                constant = int(coa2, 2)
                inst.append(f'{instruction} ${register2}, ${register1}, {constant}')
            elif instruction == "bne" or instruction == "beq":
                inst.append(f'{instruction} ${register1}, ${register2}, {constant}')
            elif instruction == "lui":
                constant = int(coa2, 2)
                inst.append(f'{instruction} ${register2}, {constant}')
            elif instruction == "jal" or instruction=='j':
                inst.append(f'{instruction} {int(jal_address, 2)}')
            else:
                inst.append(f'{instruction} ${register2}, ${register1} ')
        else:
            inst.append("unknown instruction")
    else:#r_type
        if funct in FunctSet:
            instruction = FunctSet[funct]
            register1 = int(rs, 2)
            register2 = int(rt, 2)
            register3 = int(rd, 2)
            if instruction == 'sll' or instruction == "srl" or instruction == "sra":
                inst.append(f'{instruction} ${register3}, ${register2}, {int(shamt, 2)}')
            elif instruction == "srav":
                inst.append(f'{instruction} ${register3}, ${register2}, ${register1}')
            elif instruction == "jr" or instruction == "mthi":
                inst.append(f'{instruction} ${register1}')
            elif instruction == "mflo":
                inst.append(f'{instruction} ${register3}')
            elif instruction == "mult" or instruction == "div":
               inst.append(f'{instruction} ${register1}, ${register2}')
            elif instruction == "syscall":
                inst.append(f'{instruction}')
            elif instruction == "jalr":
                inst.append(f'{instruction} ${register3}, ${register1}')
            else:
                inst.append(f'{instruction} ${register3}, ${register1}, ${register2}')
        else:
            inst.append(f'unknown instruction')
idx = 0
for i in range(16000 - len(inst)):
    inst.append('FFFFFFFF')

cnt = 0
for ins in inst:
    if cnt<total_inst:
        print(f"isnt{cnt}:{ins}")
    cnt +=1

print(f"Isntrutions: {total_inst}")
#캐쉬 1,2 나눠서 구현한다
cache1 = []
cache2 = []

class cache1():#tag 싹 바꿔줘야함
    def __init__(self,index_len,offset_len):

        #bits of cache1
        self.valid = [0 for i in range(2**index_len)]#공부해서 이부분 반영
        self.tag = [0 for i in range(2**index_len)]
        self.cache_data = [[0 for i in range(2 ** index_len)] for i in range((2 ** offset_len) / 4)]

        # bit's length
        self.tag_len = 32- (index_len + offset_len)
        self.index_len = index_len
        self.offset_len = offset_len
        self.word_num = int((2 ** offset_len) / 4)

        # hit of miss count
        self.miss = 0
        self.hit = 0

    def read_process(self,memnum,rd):
        memory_address = format(memnum,'b')

        tag_bit = memory_address[0:self.tag_len]
        index_bit = memory_address[self.tag_len:self.tag_len+self.index_len]
        offset_bit = memory_address[32-self.offset_len:32]
        index = int(index_bit,2)
        tag_val = int(tag_bit,2)
        word = int(int(offset_bit,2)/4)
        if self.valid[index] and self.tag[index] == tag_val:
            self.hit += 1
            regVal[rd] = self.cache_data[index][word]
        else:
            #miss process
            self.tag[index] = tag_val
            self.valid[index] = 1
            self.miss +=1
            # memory address translation
            memnum -= int('10000000', 16)
            memnum *= 2
            if memnum >= 0:
                DataM = "".join(DataMemory[memnum:memnum + 8])
                regVal[rd] = int(DataM, 16)
                # 블록단위로 가져오기
                memnum = int(memnum/(2 ** self.offset_len))
                for i in range(self.word_num):
                    DataM = "".join(DataMemory[memnum + i * 8:memnum + i * 8 + 8])
                    self.cache_data[index][i] = int(DataM, 16)
            else:
                print("memory address error")
    def write_process(self,memnum,rd):#write-through,no write allocate
        memory_address = format(memnum, 'b')

        tag_bit = memory_address[0:self.tag_len]
        index_bit = memory_address[self.tag_len:self.tag_len + self.index_len]
        offset_bit = memory_address[32 - self.offset_len:32]
        index = int(index_bit, 2)
        tag_val = int(tag_bit, 2)
        word = int(int(offset_bit,2)/4)
        if self.valid[index] and self.tag[index] == tag_val:
            self.hit += 1
            self.cache_data[index][word] = regVal[rd]

            # memory address translation
            memnum -= int('10000000',16)
            memnum *= 2
            if memnum >= 0:
                if regVal[rd] < 0:
                    regVal[rd] = regVal[rd] + int('100000000', 16)
                store_num = format(regVal[rd], 'x')
                store_num = '{0:0>8}'.format(store_num)
                for idx in range(8):
                    DataMemory[memnum+idx] = store_num[idx]
            else:
                print("memory address error")
        else:
            #miss process
            self.miss += 1
            self.tag[index] = tag_val
            self.valid[index] = 1

            #memory address translation
            memnum -= int('10000000', 16)
            memnum *= 2
            if memnum >= 0:
                if regVal[rd] < 0:
                    regVal[rd] = regVal[rd] + int('100000000', 16)
                store_num = format(regVal[rd], 'x')
                store_num = '{0:0>8}'.format(store_num)
                for idx in range(8):
                    DataMemory[memnum+idx] = store_num[idx]
                else:
                    print("memory address error")
    def print_hit_ratio(self):
        print("Total: ",self.hit + self.miss)
        print("Hits: ", self.hit )
        print("Misses: ", self.miss )


class cache2():
    def __init__(self, index_len, offset_len):#4-way associative
        # bit's length
        self.tag_len = 32 - (index_len + offset_len)
        self.index_len = index_len
        self.set_len = index_len-2
        self.offset_len = offset_len
        self.word_num = int((2**offset_len)/4)

        #bits of cache2
        self.LRU = [[0,1,2,3] for i in range(2**self.set_len)] #가장 참조거리가 먼 블록을 바꿈
        self.valid = [0 for i in range(2**index_len)]
        self.dirty = [0 for i in range(2**index_len)]
        self.tag = [0 for i in range(2**index_len)]
        self.cache_data = [[[ 0 for i in range(2**self.word_num)] for i in range(4)] for i in range(2**self.set_len)]

        #hit of miss count
        self.miss = 0
        self.hit = 0


    def read_process(self,memnum,rd):

        #bits of address setting
        memory_address = format(memnum,'b')
        tag_bit = memory_address[0:self.tag_len]
        index_bit = memory_address[self.tag_len:self.tag_len+self.index_len]
        offset_bit = memory_address[32-self.offset_len:32]

        #bit's value setting
        index = int(index_bit,2)
        set_num = int(index/4)
        tag_val = int(tag_bit,2)
        word = int(int(offset_bit,2)/4)

        #hit or miss
        for i in range(4):
            if self.valid[index] and self.tag[set_num*4 + i] == tag_val:
                self.hit += 1
                self.LRU[set_num].remove(i)
                self.LRU[set_num].append(i)
                regVal[rd] = self.cache_data[set_num][i][word]
                return

        self.tag[index] = tag_val
        self.valid[index] = 1
        self.miss +=1

        if memnum >= 0:
            memnum -= int('10000000',16)
            memnum *= 2
            DataM = "".join(DataMemory[memnum:memnum + 8])
            regVal[rd] = int(DataM, 16)
            #LRU_bit setting
            victim = self.LRU[set_num][0]
            del self.LRU[set_num][0]
            self.LRU[set_num].append(victim)
            # 블록단위로 가져오기
            per = 2 ** (self.offset_len+1)
            memnum = int(memnum/per)
            memnum *= per
            for i in range(self.word_num):
                DataM = "".join(DataMemory[memnum + i * 8:memnum + i * 8 + 8])
                self.cache_data[set_num][victim][i] = int(DataM,16)
        else:
            print("memory address error")
    def write_process(self,memnum,rd):#write-through,no write allocate

        # bits of address setting
        memory_address = format(memnum, 'b')
        tag_bit = memory_address[0:self.tag_len]
        index_bit = memory_address[self.tag_len:self.tag_len + self.index_len]
        offset_bit = memory_address[32 - self.offset_len:32]

        #bit's value setting
        index = int(index_bit, 2)
        tag_val = int(tag_bit, 2)
        set_num = int(index/4)
        word = int(int(offset_bit,2)/4)

        #hit of miss
        for i in range(4):
            if self.valid[index] and self.tag[set_num*4 + i] == tag_val:
                self.hit += 1
                if self.dirty[index] == 1:
                    memnum -= int('10000000',16)
                    memnum *= 2
                    if memnum >= 0:
                        for w in range(word):
                            store_num = format(self.cache_data[set_num][i][w], 'x')
                            store_num = '{0:0>8}'.format(store_num)
                            for idx in range(8):
                                DataMemory[memnum + idx] = store_num[idx]
                self.LRU[set_num].remove(i)
                self.LRU[set_num].append(i)
                self.cache_data[set_num][i][word] = regVal[rd]
                self.dirty[index] = 1
                return
        #miss process
        self.tag[index] = tag_val
        self.valid[index] = 1
        self.miss += 1

        #LRU_bit setting
        victim = self.LRU[set_num][0]
        del self.LRU[set_num][0]
        self.LRU[set_num].append(victim)

        if self.dirty[set_num*4+victim] == 1:
            victim_mem = int(format(self.tag[set_num*4+victim],'b') + format(index,'b') + '000000',2)
            victim_mem -= int('10000000',16)
            victim_mem *= 2
            for w in range(word):
                store_num = format(self.cache_data[set_num][victim][w], 'x')
                store_num = '{0:0>8}'.format(store_num)
                for idx in range(8):
                    DataMemory[victim_mem + idx] = store_num[idx]

        #memory address translation
        memnum = int(memnum / 2 ** self.offset_len)
        memnum *= 2 ** self.offset_len
        memnum -= int('10000000', 16)
        memnum *= 2
        for i in range(self.word_num):#block fetch
            DataM = "".join(DataMemory[memnum + i * 8:memnum + i * 8 + 8])
            self.cache_data[set_num][victim][i] = int(DataM, 16)
        self.cache_data[set_num][victim][word] = regVal[rd]#update cache
        self.dirty[index] = 1


    def print_hit_ratio(self):
        print("Total: ",self.hit + self.miss)
        print("Hits: ", self.hit )
        print("Misses: ", self.miss )

if cache_num==1:
    cache = cache1(5, 5)
elif cache_num==2:
    cache = cache2(6, 6)


# Do not print “unknown instruction” even if the simulator has stopped due to the unknown instruction.
# ◼ Do not print the register values
# ◼ Do not print the PC value


pc = 0
inst_cnt = 0
while pc < len(inst) and inst_cnt < int(inst_num):
    # print(f"pc:{pc}")
    if inst[pc] =='FFFFFFFF':
        # print('unknown instruction')
        pc += 1
        break
    inst_str = inst[pc]
    inst_split = inst_str.split(' ')
    if inst_split[0] == 'add':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        regVal[rd] = regVal[rs] + regVal[rt]
    elif inst_split[0] == 'addu':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        rs_val = regVal[rs]
        rt_val = regVal[rt]
        if rs_val < 0:
            rs_val = rs_val + int('100000000', 16)
        if rt_val < 0:
            rt_val = rt_val + int('100000000', 16)

        regVal[rd] = (rs_val + rt_val)%int('100000000', 16)
    elif inst_split[0] == 'sub':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        regVal[rd] = regVal[rs] - regVal[rt]
    elif inst_split[0] == 'subu':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        rs_val = regVal[rs]
        rt_val = regVal[rt]
        if rs_val < 0:
            rs_val = rs_val + int('100000000', 16)
        if rt_val < 0:
            rt_val = rt_val + int('100000000', 16)

        regVal[rd] = rs_val - rt_val

    elif inst_split[0] == 'and':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        regVal[rd] = regVal[rs] & regVal[rt]

    elif inst_split[0] == 'or':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        regVal[rd] = regVal[rs] | regVal[rt]
    elif inst_split[0] == 'slt':
        rd = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        rt = int(inst_split[3].replace('$','').replace(',',''))
        rs_val = regVal[rs]
        rt_val = regVal[rt]

        if regVal[rs] >= int('100000000', 16)/2:
            rs_val -= int('100000000', 16)
        if regVal[rt] >= int('100000000', 16)/2:
            rt_val -= int('100000000', 16)

        if rs_val < rt_val:
            regVal[rd] = 1
        else:
            regVal[rd] = 0
    elif inst_split[0] == 'sltu':
        rd = int(inst_split[1].replace('$', '').replace(',', ''))
        rs = int(inst_split[2].replace('$', '').replace(',', ''))
        rt = int(inst_split[3].replace('$', '').replace(',', ''))
        rs_val = regVal[rs]
        rt_val = regVal[rt]
        if rs_val < 0:
            rs_val = rs_val + int('100000000', 16)
        if rt_val < 0:
            rt_val = rt_val + int('100000000', 16)

        if rs_val < rt_val:
            regVal[rd] = 1
        else:
            regVal[rd] = 0
    elif inst_split[0] == 'addi':
        rt = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        const = int(inst_split[3].replace('$','').replace(',',''))
        if const >= int('1000000000000000', 2):
            const = const + int('FFFF0000', 16)  # sign extend
        regVal[rt] = regVal[rs] + const
    elif inst_split[0] == 'addiu':
        rt = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        const = int(inst_split[3].replace('$','').replace(',',''))
        rs_val = regVal[rs]
        if rs_val < 0:
            rs_val = rs_val + int('100000000', 16)
        if const >= int('1000000000000000',2):
            const = const + int('FFFF0000', 16) #sign extend

        regVal[rt] = (rs_val + const)%(2**32)

    elif inst_split[0] == 'andi':
        rt = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        const = int(inst_split[3].replace('$','').replace(',',''))
        if const >= int('1000000000000000',2):
            const = const + int('FFFF0000', 16) #sign extend

        regVal[rt] = regVal[rs] & const
    elif inst_split[0] == 'ori':
        rt = int(inst_split[1].replace('$','').replace(',',''))
        rs = int(inst_split[2].replace('$','').replace(',',''))
        const = int(inst_split[3].replace('$','').replace(',',''))
        if const >= int('1000000000000000',2):
            const = const + int('FFFF0000', 16) #sign extend

        regVal[rt] = regVal[rs] | const
    elif inst_split[0] == 'lui':
        rt = int(inst_split[1].replace('$','').replace(',',''))
        const = int(inst_split[2].replace('$','').replace(',',''))
        regVal[rt] = 0
        regVal[rt] = regVal[rt] | (const*(2**16))
    elif inst_split[0] == 'slti':
        rt = int(inst_split[1].replace('$', '').replace(',', ''))
        rs = int(inst_split[2].replace('$', '').replace(',', ''))
        const = int(inst_split[3].replace('$', '').replace(',', ''))
        rs_val = regVal[rs]
        if rs_val >= int('100000000', 16)/2:
            rs_val -= int('100000000', 16)

        if const >= int('1000000000000000',2):
            const = const - int('10000', 16) #sign extend



        if regVal[rs] < const:
            regVal[rt] = 1
        else:
            regVal[rt] = 0
    elif inst_split[0] == 'sltiu':
        rt = int(inst_split[1].replace('$', '').replace(',', ''))
        rs = int(inst_split[2].replace('$', '').replace(',', ''))
        const = int(inst_split[3].replace('$', '').replace(',', ''))
        rs_val = regVal[rs]
        if rs_val < 0:
            rs_val = rs_val + int('100000000', 16)
        if const >= int('1000000000000000',2):
            const = const + int('FFFF0000', 16) #sign extend
        if rs_val < const:
            regVal[rt] = 1
        else:
            regVal[rt] = 0
    elif inst_split[0] == 'beq':
        rt = int(inst_split[1].replace('$', '').replace(',', ''))
        rs = int(inst_split[2].replace('$', '').replace(',', ''))
        const = int(inst_split[3].replace('$', '').replace(',', ''))
        if regVal[rt] == regVal[rs]:
            pc += const
    elif inst_split[0] == 'bne':
        rt = int(inst_split[1].replace('$', '').replace(',', ''))
        rs = int(inst_split[2].replace('$', '').replace(',', ''))
        const = int(inst_split[3].replace('$', '').replace(',', ''))
        if regVal[rt] != regVal[rs]:
            pc += const
    elif inst_split[0] == 'j':
        const = int(inst_split[1].replace('$', '').replace(',', ''))
        pc_4bit = (pc*4) & int('F0000000',16)
        pc = (const + pc_4bit)
        pc -= 1
    elif inst_split[0] == 'jal':
        const = int(inst_split[1].replace('$', '').replace(',', ''))
        pc_4bit = (pc*4) & int('F0000000',16)
        regVal[31] = (pc + 1)*4
        pc = (const + pc_4bit)
        pc -= 1
    elif inst_split[0] == 'jr':
        rt = int(inst_split[1].replace('$', '').replace(',', ''))
        pc = int(regVal[rt]/4)
        pc -= 1
    elif inst_split[0] == 'sll':
        rd = int(inst_split[1].replace('$', '').replace(',', ''))
        rt = int(inst_split[2].replace('$', '').replace(',', ''))
        Shamt = int(inst_split[3].replace('$', '').replace(',', ''))
        regVal[rd] = int(regVal[rt] << (Shamt))

    elif inst_split[0] == 'srl':
        rd = int(inst_split[1].replace('$', '').replace(',', ''))
        rt = int(inst_split[2].replace('$', '').replace(',', ''))
        Shamt = int(inst_split[3].replace('$', '').replace(',', ''))
        if regVal[rt] < 0:
            temp = regVal[rt] + int('100000000',16)
            regVal[rd] = temp >> Shamt
        else:
            regVal[rd] = regVal[rt] >> Shamt







    elif inst_split[0] == 'lw':
        #hit of miss 구현
        rd = int(inst_split[1].replace('$', '').replace(',', ''))
        const_reg = inst_split[2].split('(')
        const = int(const_reg[0])
        rt = int(const_reg[1].replace(')','').replace('$',''))
        memNum_c = const + regVal[rt]
        cache.read_process(memNum_c,rd)


    elif inst_split[0] == 'sw':
        #hit of miss 구현
        rd = int(inst_split[1].replace('$', '').replace(',', ''))
        const_reg = inst_split[2].split('(')
        const = int(const_reg[0])
        rt = int(const_reg[1].replace(')', '').replace('$', ''))
        memNum_c = const + regVal[rt]
        cache.write_process(memNum_c,rd)



    elif inst_split[0] == 'syscall':
        if regVal[2] == 1:
            regval4 = regVal[4]
            if regVal[4] >= int('100000000', 16)/2:
                regval4 = regVal[4] - int('100000000',16)
            print(regval4,end='')
        elif regVal[2] == 4:
            memNum = regVal[4] - int('10000000', 16)
            memNum *= 2
            while True:
                char0 = DataMemory[memNum] + DataMemory[memNum+1]
                char0 = int(char0, 16)
                print(chr(char0),end='')
                memNum += 2
                A = "".join(DataMemory[memNum:memNum+2])
                if A == 'FF' or A == '00':
                    break
        elif regVal[2] == 5:
            num = input()
            regVal[2] = int(num)
    # else:
        # print('unknown instruction')

    pc = int(pc)+ 1
    inst_cnt += 1

cache.print_hit_ratio()




