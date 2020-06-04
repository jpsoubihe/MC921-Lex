
class Analyzer():
    def __init__(self, blocks):
        self.blocks = blocks
        self.definitions = {}

    def fix_label_name(self, instruction):
        index = instruction.index('@')
        label = instruction[index:]
        return label + '.1'


    def find_definitions(self, label, b):
        definitions = []
        for instruction in b.instructions:
            if instruction.startswith('store_'):
                definitions.append(instruction)
        return definitions

    def reaching_definitions(self):
        for b in self.blocks:
            # print("instructions = " + str(b.instructions[0]))
            if b.instructions is not None and b.instructions[0].startswith('def'):
                label = self.fix_label_name(b.instructions[0])
            print(label)
            label = label[:-1] + str(int(label[-1]) + 1)
            self.definitions[label] = self.find_definitions(label, b)
        return self.definitions
