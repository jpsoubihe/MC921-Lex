operations = ['and_', 'or_', 'eq_', 'add_', 'mul_', 'div_', 'ne_', 'mod_']
class Available_Expressions():

    def __init__(self):
        self.definitions = {}
        self.gen_set = {}
        self.out_set = {}
        self.in_set = {}
        self.kill_set = {}
        self.scope = ''

    def generate_in(self, out_set, index):
        pass

    def generate_out(self, in_set, index):
        pass

    def gen(self, index, instruction):
        s = instruction[0].split('_')[0] + '_'
        if operations.__contains__(s):
            return index, instruction[1], instruction[2]

    def kill(self, instruction, v):
        pass

    def generate_in_out(self):
        '''
           Applies the values of in and out sets of each sentence of the block - single iteration. Returns a boolean indicating if the sets changed or not.
           in[n] = U out[p] (p -> predecessors)
           out[n] = gen[n] U (in[n] - kill[n])
       '''
        # index = 0
        # in_set = self.in_set
        # out_set = self.out_set
        # while index < len(self.kill_set):
        #     in_set[index] = self.generate_in(out_set, index)
        #     out_set[index] = self.generate_out(in_set, index)
        #     index += 1
        # if in_set != self.in_set and out_set != self.out_set:
        #     return True
        # self.in_set = in_set
        # self.out_set = out_set
        # return False

    def initialize(self):
        self.__init__()

    def parse(self, block):
        '''
            Parses the vector of instructions of a block into a tuple. ToDo: Check if structure of the sets for analysis shoould really be made here.
        '''
        v = []

        # 1st iteration - setting gens and kills
        for instruction in block:
            temp_vector = instruction.split(' ')
            for elem in temp_vector:
                if elem == '':
                    temp_vector.remove(elem)
            v.append(tuple(temp_vector))

        index = 0
        for instruction in v:
            self.gen_set[index] = self.gen(index, instruction)
            # self.kill_set[index] = self.kill(instruction, v)
            index += 1

        modified = True

        while modified is True:
            modified = self.generate_in_out()

    def analyze_block(self, block):
        '''
            Executes the reaching definitions analysis. ToDo: Maybe it will be refactored (see Parse function for more infos)
        '''
        self.initialize()
        self.scope = block.label
        self.parse(block)
        return self.gen_set, self.kill_set, self.in_set, self.out_set