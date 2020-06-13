operations = ['and_', 'or_', 'eq_', 'add_', 'mul_', 'div_', 'ne_', 'mod_', 'store_']
class Available_Expressions():

    def __init__(self, block):
        self.definitions = {}
        self.gen_set = {}
        self.out_set = {}
        self.in_set = {}
        self.kill_set = {}
        self.variables = {}
        self.temp = {}
        self.scope = ''

    def generate_in(self, out_set, index):
        in_set = set()
        #in the intra-block case it's ok to consider the index-1 block as the predecessor
        if index > 0 and out_set[index - 1] is not None:
            out_set_set = set(out_set[index - 1])
            # ToDo: when it comes the time for optimization between blocks this will have to change
            in_set = out_set_set
        return in_set

    def generate_out(self, in_set, index):
        in_set_set = set(in_set[index])
        if len(self.gen_set[index]) > 0:
            gen = set([self.gen_set[index][0]])
            if len(self.kill_set[index]) > 0:
                kill = set([self.kill_set[index][0][0]])
                return list(gen | (in_set_set - kill))
            else:
                return list(gen | in_set_set)
        else:
            if len(self.kill_set[index]) > 0:
                kill = set([self.kill_set[index][0][0]])
                return list(in_set_set - kill)
            else:
                return list(in_set_set)

    def gen(self, index, instruction):
        if self.kill_set.keys().__contains__(index):
            kill_set = set(self.kill_set[index])
        else:
            kill_set = set()
        gen_set = set()

        s = instruction[0].split('_')[0] + '_'
        if operations.__contains__(s):
            if s == "store_":
                gen_set.add((index, instruction[1]))
            else:
                gen_set.add((index, instruction[1], instruction[2]))

        return list(gen_set - kill_set)

    def belongs_to(self, argument, variable):
        if self.temp.keys().__contains__(variable) is False:
            return False
        temp = self.temp[variable]
        for j in temp:
            if j == argument:
                return True
        return False

    def store_kill(self, index, definition):
        attribute = definition[len(definition) - 1]
        return index, attribute[1:]

    def search_for_kill(self, block, operand, inst_index):

        # need to check where the operands values are being changed
        operand_changes = []
        for index, instruction in enumerate(block):
            s = instruction[0].split('_')[0] + '_'
            if operations.__contains__(s):
                if instruction[0].startswith('store_'):
                    if instruction[2] == operand:
                        if index != inst_index:
                            operand_changes.append((index, instruction[2][1:]))
                else:
                    if instruction[3] == operand:
                        if index != inst_index:
                            operand_changes.append((index, instruction[3][1:]))
        return operand_changes

        # kill_expressions = []
        # for index, instruction in enumerate(block):
        #     s = instruction[0].split('_')[0] + '_'
        #     if operations.__contains__(s):
        #         if s == "store_":
        #             if instruction[2] == variable:
        #                 kill_expressions.append(self.store_kill(index, instruction))
        #                 # kill_expressions.append(instruction)
        #         elif len(instruction) > 3 and instruction[1] is not "cbranch":
        #             if instruction[3] == variable or self.belongs_to(instruction[3], variable):
        #                 kill_expressions.append((index, instruction[3]))
        # return kill_expressions


    def kill(self, index, sentence, block):
        if sentence[0].startswith("store"):
            # sentence[2] is the variable whose value is being modified
            return self.search_for_kill(block, sentence[2], index)
        return []


    def generate_in_out(self):
        '''
           Applies the values of in and out sets of each sentence of the block - single iteration. Returns a boolean indicating if the sets changed or not.
           in[n] = intersec out[p] (p -> predecessors)
           out[n] = gen[n] U (in[n] - kill[n])
       '''
        index = 0

        in_set = self.in_set
        out_set = self.out_set
        while index < len(self.kill_set):
            in_set[index] = self.generate_in(out_set, index)
            out_set[index] = self.generate_out(in_set, index)
            index += 1
        if in_set != self.in_set and out_set != self.out_set:
            return True
        self.in_set = in_set
        self.out_set = out_set
        return False

    def merge_dict(self, vars, ops):
        m = {}

        for variables in vars.values():
            m[variables] = []

        for i in vars:
            t = vars[i]
            for p in m.keys():
                if p == t:
                    temp = m[p]
                    temp.append(i)
                    m[p] = temp

        for i in ops.keys():
            for operator in ops[i]:
                for j in m.keys():
                    if m[j].__contains__(operator):
                        temp = m[j]
                        temp.append(i)
                        m[j] = temp
        return m

    def prepare_var(self, block):
        mapping = {}
        for instruction in block:
            if instruction[0].startswith('load_'):
                mapping[instruction[2]] = instruction[1]

        return mapping

    def prepare_ops(self, block):
        mapping = {}
        for instruction in block:
            s = instruction[0].split('_')[0] + '_'
            if operations.__contains__(s):
                if s == "store_":
                    self.variables[instruction[2][1:]] = instruction[1]
                else:
                    mapping[instruction[3]] = instruction[1], instruction[2]
        return mapping

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

        # self.temp and ops_map together gather the temporary variables used in each block
        var_map = self.prepare_var(v)
        ops_map = self.prepare_ops(v)
        self.temp = self.merge_dict(var_map, ops_map)
        for index, instruction in enumerate(v):
            self.kill_set[index] = self.kill(index, instruction, v)
            self.gen_set[index] = self.gen(index, instruction)


        for ind, instruction in enumerate(v):
            self.in_set[ind] = instruction
            self.out_set[ind] = instruction

        modified = True
        while modified is True:
            modified = self.generate_in_out()

    def initialize(self, block):
        self.__init__(block)

    def analyze_block(self, block):
        '''
            Executes the Available Expressions analysis. ToDo: Maybe it will be refactored (see Parse function for more infos)
        '''
        self.initialize(block)
        self.scope = block.label
        self.parse(block)
        return self.gen_set, self.kill_set, self.in_set, self.out_set
