import uc_new_block


def check_existence(dic, value):
    pass
    # for k in dic.keys():
    #     if dic[k].__contains__()

class Copy_Analysis():

    def __init__(self, functions):
        self.functions = functions
        self.copies = []
        self.gen = {}
        self.kill = {}
        self.visited = []
        self.to_visit = []

    def resolve_blocks(self, block):
        print(block.label)
        for n, inst in enumerate(block.instructions):
            # if we have a load followed by a store, we have a copy!
            if inst.startswith("load_"):
                adjacent = block.instructions[min(n + 1, len(block.instructions) - 1)]
                if adjacent.startswith("store_"):
                    self.copies.append((adjacent.split(' ')[2], inst.split(' ')[1]))
                    # self.gen[bias] = (adjacent.split(' ')[2], inst.split(' ')[1])

        if isinstance(block, uc_new_block.BasicBlock):
            if block.next_block is not None:
                self.index += 1
                self.resolve_blocks(block.next_block)
        elif isinstance(block, uc_new_block.ConditionBlock):
            self.index += 1
            self.resolve_blocks(block.taken)
            self.index += 1
            self.resolve_blocks(block.fall_through)

    def resolve_function(self, blocks):
        self.index = 0
        while self.index < len(blocks):
            self.resolve_blocks(blocks[self.index])
            self.index += 1

    def pop_gen(self, instruction, predecessor_inst):
        # if we have a store after a load, we have a copy!
        if instruction.startswith("store_"):
            if predecessor_inst.startswith("load_"):
                # if confirmed we registered it in a list storing ALL copies present on the code...
                self.copies.append((predecessor_inst.split(' ')[1], instruction.split(' ')[2]))
                # And a tuple indicating (value, assigned) will be the value of key n (index of STORE instruction on the code)
                return predecessor_inst.split(' ')[1], instruction.split(' ')[2]
        # case it's not a copy we return an empty tuple, empty gen set
        return ()

    def pop_kill(self, instruction, gen):
        if instruction.startswith("store_"):
            return instruction.split(' ')[2]

    def pop_in(self, pred_out):
        return pred_out

    def set_sub(self, _set, element):
        new_list = []
        for reg in _set:
            if reg.__contains__(element):
                pass
            else:
                new_list.append(reg)
        if len(new_list) < 1:
            return [()]
        return new_list

    def set_union(self, in_set, gen):
        l = []
        exists = False
        for element in in_set:
            if element != ():
                l.append(element)
        for element in in_set:
            if element == gen:
                exists = True
        if not exists:
            if len(gen) > 0:
                l.append(gen)
        if len(l) < 1:
            return in_set
        return l

    def pop_out(self, gen, in_set, kill):
        if kill is None:
            l = in_set
        else:
            l = self.set_sub(in_set, kill)
        return self.set_union(l, gen)

    def analysis(self, block, block_label):
        gen = {}
        kill = {}
        size = 0
        in_set = {}
        if len(block.predecessors) > 0:
            for i in block.predecessors:
                in_set[0] = self.out_set[i.label][len(self.out_set[i.label]) - 1]
        else:
            in_set[0] = [()]
        out_set = {}
        for n, instruc in enumerate(block.instructions):
            pred = block.instructions[max(n - 1, 0)]
            gen[n] = self.pop_gen(instruc, pred)
            kill[n] = self.pop_kill(instruc, gen[n])
            if n > 0:
                in_set[n] = self.pop_in(out_set[n - 1])
            out_set[n] = self.pop_out(gen[n], in_set[n], kill[n])
            size += 1
        return gen, kill, in_set, out_set

    # def analysis_intrablock(self, block, index):
    #     gen = {}
    #     kill = {}
    #     size = 0
    #     in_set = {}
    #     if index >= 1:
    #         in_set[0] = self.out_set[index - 1][len(self.out_set[index - 1]) - 1]
    #     else:
    #         in_set[0] = [()]
    #     out_set = {}
    #     for n, instruc in enumerate(block.instructions):
    #         pred = block.instructions[max(n - 1, 0)]
    #         gen[n] = self.pop_gen(instruc, pred)
    #         kill[n] = self.pop_kill(instruc, gen[n])
    #         if n > 0:
    #             in_set[n] = self.pop_in(out_set[n - 1])
    #         out_set[n] = self.pop_out(gen[n], in_set[n], kill[n])
    #         size += 1
    #     return gen, kill, in_set, out_set


    # def analyze_function(self, function):
    #     gen = {}
    #     kill = {}
    #     in_set = {}
    #     out_set = {}
    #     for n, block in enumerate(function):
    #         gen[block.label], kill[block.label], in_set[block.label], out_set[block.label] = self.analysis_intrablock(block, block.label)

    def find_block(self, block):
        actual_f = None
        for function in self.functions:
            if block.function == function[0].function:
                actual_f = function
                break

        if actual_f is not None:
            for blc in actual_f:
                if blc.label == block.label:
                    return blc

    def surf_function_blocks(self, block):
        if self.visited.__contains__(block.label) is False:
            self.visited.append(block.label)
            self.gen[block.label], self.kill[block.label], self.in_set[block.label], self.out_set[block.label] = self.analysis(block, block.label)
            if isinstance(block, uc_new_block.BasicBlock):
                if block.next_block is not None:
                    self.surf_function_blocks(self.find_block(block.next_block))

            else:
                self.surf_function_blocks(self.find_block(block.taken))
                self.surf_function_blocks(self.find_block(block.fall_through))




    def find_copies(self):
        for function in self.functions:
            self.bias = 0
            self.gen = {}
            self.kill = {}
            self.in_set = {}
            self.out_set = {}
            # self.analyze_function(function)
            self.visited = []
            self.surf_function_blocks(function[0])
