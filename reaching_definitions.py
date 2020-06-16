


def parse_code(code):
    if isinstance(code[0], tuple):
        return code
    instructions = []
    for block in code:
        for inst in block.instructions:
            line = inst.split(' ')
            for elem in line:
                if elem == '':
                    line.remove(elem)
            instructions.append(tuple(line))
    return instructions


class Reaching_Definition():
    def __init__(self, blocks=None):
        self.blocks = blocks
        self.definitions = {}
        self.gen_set = {}
        self.out_set = {}
        self.in_set = {}
        self.kill_set = {}
        self.scope = ''

    def gen(self, index, instruction):
        '''
        Given an instruction it returns the respective gen[n] set.
        Maybe needs some refinement. (return and parameter)
        '''
        if instruction[0].startswith('store'):
            if instruction[1].startswith('%' + self.scope + '_'):
                pass
            elif instruction[2].endswith('return'):
                pass
            else:
                return index, instruction[2][1:]

    def store_kill(self, index, definition):
        attribute = definition[len(definition) - 1]
        return index, attribute[1:]

    def kill(self, sentence, block):
        '''
        Given a sentence and the block being analyzed, it returns the respective kill[n] set.
        '''
        kills = []
        if sentence[0].startswith('store'):
            for index, definition in enumerate(block):
                if definition[0].startswith('store') and definition != sentence:
                    if definition[2] == sentence[2]:
                        kills.append(self.store_kill(index, definition))
        if len(kills) > 0:
            return kills

    def generate_in(self,  out_set, index):
        in_set = set()
        if index > 0 and out_set[index - 1] is not None:
            out_set_set = set(out_set[index - 1])
            in_set = in_set | out_set_set
        return in_set

    def generate_out(self, in_set, index):
        in_set_set = set(in_set[index])
        if self.gen_set[index] is not None:
            gen = set([self.gen_set[index][0]])
            if self.kill_set[index] is not None:
                kill = set([self.kill_set[index][0][0]])
                return list(gen | (in_set_set - kill))
            else:
                return list(gen | in_set_set)
        else:
            if self.kill_set[index] is not None:
                kill = set([self.kill_set[index][0][0]])
                return list(in_set_set - kill)
            else:
                return list(in_set_set)

    def generate_in_out(self):
        '''
        Applies the values of in and out sets of each sentence of the block - single iteration. Returns a boolean indicating if the sets changed or not.
        in[n] = U out[p] (p -> predecessors)
        out[n] = gen[n] U (in[n] - kill[n])
        '''
        index = 0
        in_set = self.in_set
        out_set = self.out_set
        while index < len(self.kill_set):
            in_set[index] = self.generate_in(out_set, index)
            out_set[index] = self.generate_out(in_set, index)
            index += 1
        '''
                Applies the values of in and out sets of each sentence of the block - single iteration. Returns a boolean indicating if the sets changed or not.
                in[n] = U out[p] (p -> predecessors)
                out[n] = gen[n] U (in[n] - kill[n])
        '''
        if in_set != self.in_set and out_set != self.out_set:
            return True
        self.in_set = in_set
        self.out_set = out_set
        return False

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
            self.kill_set[index] = self.kill(instruction, v)
            index += 1

        modified = True

        while modified is True:
            modified = self.generate_in_out()

    def fix_label_name(self, instruction):
        '''
        Removes the '@' from each label, just for better view.
        '''
        index = instruction.index('@')
        label = instruction[index:]
        return label + '.1'

    def initialize(self):
        self.__init__()

    def analyze_block(self, block):
        '''
        Executes the reaching definitions analysis. ToDo: Maybe it will be refactored (see Parse function for more infos)
        '''
        self.initialize()
        self.scope = block.label
        self.parse(block)
        return self.gen_set, self.kill_set, self.in_set, self.out_set
