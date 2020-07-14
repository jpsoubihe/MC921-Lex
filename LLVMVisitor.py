from llvmlite import ir

from uc_new_block import BlockVisitor


def make_bytearray(buf):
    # Make a byte array constant from *buf*.
    b = bytearray(buf)
    n = len(b)
    return ir.Constant(ir.ArrayType(ir.IntType(8), n), b)


class LLVMFunctionVisitor(BlockVisitor):

    def __init__(self, module):
        self.module = module
        self.func = None
        self.builder = None
        self.loc = {}

    def _global_constant(self, builder_or_module, name, value, linkage='internal'):
        # Get or create a (LLVM module-)global constant with *name* or *value*.
        if isinstance(builder_or_module, ir.Module):
            mod = builder_or_module
        else:
            mod = builder_or_module.module
        data = ir.GlobalVariable(mod, value.type, name=name)
        data.linkage = linkage
        data.global_constant = True
        data.initializer = value
        data.align = 1
        return data

    def _cio(self, fname, format, *target):
        # Make global constant for string format
        mod = self.builder.module
        fmt_bytes = make_bytearray((format + '\00').encode('ascii'))
        global_fmt = self._global_constant(mod, mod.get_unique_name('.fmt'), fmt_bytes)
        fn = mod.get_global(fname)
        ptr_fmt = self.builder.bitcast(global_fmt, ir.IntType(8).as_pointer())
        return self.builder.call(fn, [ptr_fmt] + list(target))

    def _build_print(self, val_type, target):
        if target:
            # get the object assigned to target
            _value = self._get_loc(target)
            if val_type == 'int':
                self._cio('printf', '%d', _value)
            elif val_type == 'float':
                self._cio('printf', '%.2f', _value)
            elif val_type == 'char':
                self._cio('printf', '%c', _value)
            elif val_type == 'string':
                self._cio('printf', '%s', _value)
        else:
            self._cio('printf', '\n')