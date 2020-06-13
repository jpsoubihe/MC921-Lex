import copy

operations = ['and_', 'or_', 'eq_', 'add_', 'mul_', 'div_', 'ne_', 'mod_', 'store_']

class Liveness():

    def __init__(self, block):
        self.definitions = {}
        self.gen_set = {}
        self.out_set = {}
        self.in_set = {}
        self.kill_set = {}
        self.variables = {}
        self.temp = {}
        self.scope = ''

    def kill(self, index, instruction, block):
        s = instruction[0].split('_')[0] + '_'
        if operations.__contains__(s):
            if s == 'store_':
                return [instruction[2]]
        return []

    def get_func_param(self, index, block):
        ind = index
        par = True
        parameters = []
        while par:
            if block[ind + 1][0].startswith('param_'):
                parameters.append(block[ind + 2][1][1:])
                ind += 1
            elif len(block) > (ind + 1) and block[ind + 1][0].startswith('load_'):
                if len(block) > (ind + 2):
                    if block[ind + 2][0].startswith('param_'):
                        ind += 1
                    else:
                        par = False
                else:
                    par = False
            else:
                par = False
        return parameters

    def gen(self, index, instruction, block):
        s = instruction[0].split('_')[0] + '_'
        if operations.__contains__(s):
            if s == 'store_':
                return [instruction[1]]
            else:
                return [instruction[1], instruction[2]]
        elif instruction[0] == 'cbranch':
            return [instruction[1], instruction[2]]
        elif instruction[0].startswith('call'):
            return self.get_func_param(index, block)
        else:
            return []

    def generate_in(self, out_set, index):
        out_set_set = set(out_set[index])
        if len(self.gen_set[index]) > 0:
            gen = set([self.gen_set[index][0]])
            if len(self.kill_set[index]) > 0:
                kill = set([self.kill_set[index][0]])
                return list(gen | (out_set_set - kill))
            else:
                return list(gen | out_set_set)
        else:
            if len(self.kill_set[index]) > 0:
                kill = set([self.kill_set[index][0][0]])
                return list(out_set_set - kill)
            else:
                return list(out_set_set)

    def generate_out(self, in_set, index):
        '''
        For the intrablock analysis its ok to consider that the successor is the preceding one in the IN_SET (remember that its reversed comparing with the block of instructions)
        '''
        if index == 0:
            return []
        return in_set[index - 1]

    def generate_in_out(self):
        '''
           Applies the values of in and out sets of each sentence of the block - single iteration. Returns a boolean indicating if the sets changed or not.
           in[n] = U in[s] (s -> successors)
           out[n] = gen[n] U (out[n] - kill[n])
       '''
        index = 0

        in_set = self.in_set
        out_set = self.out_set
        while index < len(self.kill_set):
            out_set[index] = self.generate_out(in_set, index)
            in_set[index] = self.generate_in(out_set, index)
            index += 1
        if in_set != self.in_set and out_set != self.out_set:
            return True
        self.in_set = in_set
        self.out_set = out_set
        return False

    def parse(self, block):
        # do the steps to prepare our backward analysis
        v = copy.deepcopy(block.instructions)
        v.reverse()
        instructions = []
        for instruction in v:
            temp_vector = instruction.split(' ')
            for elem in temp_vector:
                if elem == '':
                    temp_vector.remove(elem)
            instructions.append(tuple(temp_vector))

        # after formatting the instructions of the block into tuples we can process our gen & kill sets
        for index, instruction in enumerate(instructions):
            self.gen_set[index] = self.gen(index, instruction, instructions)
            self.kill_set[index] = self.kill(index, instruction, instructions)

        modified = True
        while modified is True:
            modified = self.generate_in_out()

    def initialize(self, block):
        self.__init__(block)

    def analyze_block(self, block):
        '''
            Executes the Liveness analysis. ToDo: Maybe it will be refactored (see Parse function for more infos)
        '''
        self.initialize(block)
        self.scope = block.label
        self.parse(block)
        return self.gen_set, self.kill_set, self.in_set, self.out_set
