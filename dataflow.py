from available_expressions import Available_Expressions
from liveness import Liveness
from reaching_definitions import Reaching_Definition
from uc_block import Block_Visitor


class DataFlow():
    def __init__(self, gencode):
        block_const = Block_Visitor(gencode)
        blocks = block_const.divide()

        # sets of reaching definitions analysis
        gen_block_rd = {}
        kill_block_rd = {}
        in_block_rd = {}
        out_block_rd = {}

        # sets of available expressions analysis
        gen_block_ae = {}
        kill_block_ae = {}
        in_block_ae = {}
        out_block_ae = {}

        # sets of liveness analysis
        gen_block_lv = {}
        kill_block_lv = {}
        in_block_lv = {}
        out_block_lv = {}



        for function in blocks:
            index = 0
            reaching = Reaching_Definition(function, function)
            for block in function:
                available = Available_Expressions(function, block)
                liveness = Liveness(function, block)
                gen_block_rd[block.label], kill_block_rd[block.label], in_block_rd[block.label], out_block_rd[block.label] = reaching.analyze_block(block, index)
                gen_block_ae[block.label], kill_block_ae[block.label], in_block_ae[block.label], out_block_ae[block.label] = available.analyze_block(block, index)
                gen_block_lv[block.label], kill_block_lv[block.label], in_block_lv[block.label], out_block_lv[block.label] = liveness.analyze_block(block, index)
                index += len(block.instructions) - 1