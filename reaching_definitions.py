




class Analyzer():
    def __init__(self, blocks):
        self.blocks = blocks
        self.definitions = {}
        self.gen_set = {}
        self.out_set = {}
        self.gen_set = {}
        self.kill_set = {}

    def gen(self, instruction):
        '''
        Given an instruction it returns the respective gen[n] set.
        '''
        if instruction[0].startswith('store'):
            return instruction[2]


    def kill(self, sentence, kill_set, block):
        '''
        Given a sentence and the block being analyzed, it returns the respective kill[n] set.
        '''
        kills = []
        if sentence[0].startswith('store'):
            for definition in block:
                if definition[0].startswith('store') and definition != sentence:
                    if definition[2] == sentence[2]:
                        kills.append(definition)
        if len(kills) > 0:
            return kills

    def parse(self, block):
        '''
        Parses the vector of instructions of a block into a tuple. ToDo: Check if structure of the sets for analysis shoould really be made here.
        '''
        v = []
        in_set = {}
        out_set = {}
        gen_set = {}
        kill_set = {}

        # 1st iteration - setting gens and kills
        for instruction in block:
            temp_vector = instruction.split(' ')
            for elem in temp_vector:
                if elem == '':
                    temp_vector.remove(elem)
            v.append(tuple(temp_vector))

        index = 0
        for instruction in v:
            gen_set[index] = self.gen(instruction)
            kill_set[index] = self.kill(instruction, kill_set, v)
            index += 1

        return v

    def fix_label_name(self, instruction):
        '''
        Removes the '@' from each label, just for better view.
        '''
        index = instruction.index('@')
        label = instruction[index:]
        return label + '.1'


    def find_definitions(self, label, b):
        '''
        Finds all the definitions present in a block. ToDo: we're going to use it?
        '''
        definitions = []
        for instruction in b.instructions:
            if instruction.startswith('store_'):
                definitions.append(instruction)
        return definitions

    def reaching_definitions(self):
        '''
        Executes the reaching definitions analysis. ToDo: Maybe it will be refactored (see Parse function for more infos)
        '''
        for block_list in self.blocks:
            for block in block_list:
                block_set = self.parse(block)
                # gen(block_set)


                # print("instructions = " + str(b.instructions[0]))
                if block.instructions is not None and block.instructions[0].startswith('def'):
                    label = self.fix_label_name(block.instructions[0])
                    # label = label[:-1] + str(int(label[-1]) + 1)

                print(label)
                self.definitions[label] = self.find_definitions(label, block)
                label = label[:-1] + str(int(label[-1]) + 1)
        return self.definitions
