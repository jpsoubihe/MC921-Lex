import uc_new_block


def check_existence(dic, value):
    pass
    # for k in dic.keys():
    #     if dic[k].__contains__()

class Copy_Analysis():

    def __init__(self, functions):
        self.global_in = {}
        self.global_out = {}
        self.block_in = {}
        self.block_out = {}
        self.functions = functions
        self.copies = {}
        self.gen = {}
        self.kill = {}
        self.visited = []
        self.to_visit = []
        self.to_drop = {}

    def resolve_blocks(self, block):
        print(block.label)
        for n, inst in enumerate(block.instructions):
            # if we have a load followed by a store, we have a copy!
            if inst.startswith("load_"):
                adjacent = block.instructions[min(n + 1, len(block.instructions) - 1)]
                if adjacent.startswith("store_"):
                    self.copies[n] = (adjacent.split(' ')[2], inst.split(' ')[1])
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

    def pop_gen(self, instruction, predecessor_inst, n):
        # if we have a store after a load, we have a copy!
        if instruction.startswith("store_"):
            if predecessor_inst.startswith("load_"):
                # if confirmed we registered it in a list storing ALL copies present on the code...
                self.copies[n] = (predecessor_inst.split(' ')[1], instruction.split(' ')[2])
                # And a tuple indicating (value, assigned) will be the value of key n (index of STORE instruction on the code)
                return predecessor_inst.split(' ')[1], instruction.split(' ')[2]
        # case it's not a copy we return an empty tuple, empty gen set
        return ()

    def pop_kill(self, instruction):
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

    def intersection_sets(self, original_in, pred_out):
        entry = []
        for tuples in pred_out:
            for originals in original_in:
                if originals == tuples:
                    entry.append(originals)
        if len(entry) < 1:
            return [()]
        return entry

    def refactor_analysis(self, block):
        for visit in self.visited:
            if visit.predecessors.__contains__(block):
                self.gen[visit.label], self.kill[visit.label], self.in_set[visit.label], self.out_set[visit.label] = self.analysis(visit)
                # self.refactor_analysis(visit)

    def analysis(self, block):
        gen = {}
        kill = {}
        size = 0
        in_set = {}
        in_set[0] = None
        if len(block.predecessors) > 0:
            for i in block.predecessors:
                if self.out_set.__contains__(i.label):
                    if in_set[0] is None:
                        in_set[0] = self.out_set[i.label][len(self.out_set[i.label]) - 1]
                    else:
                        in_set[0] = self.intersection_sets(in_set[0], self.out_set[i.label][len(self.out_set[i.label]) - 1])
                else:
                    self.to_visit.append(i.label)
        else:
            in_set[0] = [()]
        out_set = {}
        for n, instruc in enumerate(block.instructions):
            pred = block.instructions[max(n - 1, 0)]
            gen[n] = self.pop_gen(instruc, pred, n)
            kill[n] = self.pop_kill(instruc)
            if n > 0:
                in_set[n] = self.pop_in(out_set[n - 1])
            out_set[n] = self.pop_out(gen[n], in_set[n], kill[n])
            size += 1
        return gen, kill, in_set, out_set

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
        if self.visited.__contains__(block) is False:
            self.visited.append(block)
            if self.to_visit.__contains__(block.label):
                self.gen[block.label], self.kill[block.label], self.in_set[block.label], self.out_set[block.label] = self.analysis(block)
                self.block_in[block.label] = self.in_set[block.label][0]
                self.block_out[block.label] = self.in_set[block.label][len(self.in_set[block.label]) - 1]
                self.refactor_analysis(block)
                self.to_visit.remove(block.label)
            else:
                self.gen[block.label], self.kill[block.label], self.in_set[block.label], self.out_set[block.label] = self.analysis(block)
                self.block_in[block.label] = self.in_set[block.label][0]
                self.block_out[block.label] = self.in_set[block.label][len(self.in_set[block.label]) - 1]

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
            self.to_visit = []
            self.surf_function_blocks(function[0])
            self.global_in[function[0].function] = self.in_set
            self.global_out[function[0].function] = self.out_set

    def refactor_instruction(self, dic, instruction):
        for elem in instruction:
            if instruction[0].startswith('define'):
                return instruction
            if dic.keys().__contains__(elem):
                index = instruction.index(elem)
                return instruction[:index] + (dic[elem],) + instruction[index+1:]
        return instruction

    def isFirst(self, function, block, instruction, index, t):
        if index == 0:
            predecessor = None
            for function in self.functions:
                if function[0].function == function:
                    for blck in function:
                        if blck.label == block:
                            predecessor = blck.predecessor
            if predecessor is not None:
                if self.block_out[predecessor.label][-1].__contains__(t):
                    return False
                else:
                    return True
        else:
            if self.global_in[function][block][index - 1].__contains__(t):
                return False
            else:
                return True

    def any_func(self, function, block, instruction, index):
        base_dic = self.global_in[function][block][index]
        if base_dic[0] != ():
            dic = {}
            for t in base_dic:
                if not self.isFirst(function, block, instruction, index, t):
                    dic[t[1]] = t[0]
                    self.to_drop[index] = t
                    return self.refactor_instruction(dic, instruction)
            return instruction
        else:
            return instruction

    def propagation(self, code):
        g = 0
        other_list = []
        function = "global"
        block = "global"
        dic = self.global_in[function][block]
        cont = 0
        for i in code:
            if i[0].startswith('define'):
                function = i[1][1:]
                block = i[1][1:]
                dic = self.global_in[function][block]
                cont = 0
            elif len(i) == 1:
                if i[0].startswith('return') is False:
                    block = i[0]
                    dic = self.global_in[function][block]
                    cont = 0
            instruction = self.any_func(function, block, code[g], cont)
            other_list.append(instruction)
            g += 1
            cont += 1
        return other_list
