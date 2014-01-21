#!/usr/bin/python

import sys
import types
from clojure.lang import *

from parsimonious.grammar import Grammar


class Vector(ASeq):
    def __init__(self, data=None, meta=None):
        ASeq.__init__(self, meta)
        if data is None:
            self.data = []
        else:
            self.data = data

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __str__(self):
        ret = "["

        for i in range(0, len(self.data)):
            if i != 0:
                ret += " "
            ret += str(self.data[i])

        return ret + "]"

    def first(self):
        return self.data[0]

    def next(self):
        return Vector(self.data[1:])

    def cons(self, n):
        self.data.append(n)
        return self

    def withMeta(self, meta):
        return Vector(self.data, meta)


class Map(IObj):
    def __init__(self, data=None, meta=None):
        if data is None:
            self._data = {}
        else:
            self._data = data
        self._meta = meta

    def assoc(self, key, value):
        self._data[key] = value
        return self

    def dissoc(self, key):
        del self._data[key]
        return self

    def get(self, key):
        return self._data[key]

    def __str__(self):
        ret = "{"
        for k, v in self._data.iteritems():
            if len(ret) > 1:
                ret += ", "
            ret = ret + str(k) + " " + str(v)
        ret += "}"
        return ret

    def __iter__(self):
        return self._data.__iter__()

    def meta(self):
        return self._meta

    def withMeta(self, meta):
        return Map(self._data, meta)


class Symbol(IObj):
    def __init__(self, a1, a2, a3=None):
        if a3 is None:
            self.ns = a1
            self.name = a2
            self._meta = None
        else:
            self._meta = a1
            self.ns = a2
            self.name = a3

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return isinstance(other, Symbol) and self.name.__lt__(other.name)

    def __le__(self, other):
        return isinstance(other, Symbol) and self.name.__le__(other.name)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name.__eq__(other.name)

    def __ne__(self, other):
        return isinstance(other, Symbol) and self.name.__ne__(other.name)

    def __gt__(self, other):
        return isinstance(other, Symbol) and self.name.__gt__(other.name)

    def __ge__(self, other):
        return isinstance(other, Symbol) and self.name.__ge__(other.name)

    def __hash__(self):
        return self.name.__hash__()

    def meta(self):
        return self._meta

    def withMeta(self, meta):
        return Symbol(meta, self.ns, self.name)

    @classmethod
    def intern(cls, nsname):
        try:
            i = nsname.index('/')
        except ValueError:
            i = -1

        if i == -1 or nsname == "/":
            return Symbol(None, intern(nsname))
        else:
            return Symbol(intern(nsname[0:i]), intern(nsname[(i + 1):]))


class String(object):
    def __init__(self, val):
        self._val = val

    def __str__(self):
        return "\"" + self._val + "\""

    def __lt__(self, other):
        return isinstance(other, String) and self._val.__lt__(other._val)

    def __le__(self, other):
        return isinstance(other, String) and self._val.__le__(other._val)

    def __eq__(self, other):
        return isinstance(other, String) and self._val.__eq__(other._val)

    def __ne__(self, other):
        return isinstance(other, String) and self._val.__ne__(other._val)

    def __gt__(self, other):
        return isinstance(other, String) and self._val.__gt__(other._val)

    def __ge__(self, other):
        return isinstance(other, String) and self._val.__ge__(other._val)

    def __hash__(self):
        return self._val.__hash__()


class Keyword(object):
    def __init__(self, val):
        self._val = val[1:]

    def __str__(self):
        return ":" + self._val

    def __lt__(self, other):
        return isinstance(other, Keyword) and self._val.__lt__(other._val)

    def __le__(self, other):
        return isinstance(other, Keyword) and self._val.__le__(other._val)

    def __eq__(self, other):
        return isinstance(other, Keyword) and self._val.__eq__(other._val)

    def __ne__(self, other):
        return isinstance(other, Keyword) and self._val.__ne__(other._val)

    def __gt__(self, other):
        return isinstance(other, Keyword) and self._val.__gt__(other._val)

    def __ge__(self, other):
        return isinstance(other, Keyword) and self._val.__ge__(other._val)

    def __hash__(self):
        return self._val.__hash__()

    @classmethod
    def intern(cls, ns, val):
        return Keyword(val)


class Boolean(object):
    def __init__(self, val):
        self._val = val == "true"

    def __str__(self):
        if self._val:
            return "true"
        return "false"

    def __eq__(self, other):
        return isinstance(other, Boolean) and self._val == other._val

    def __hash__(self):
        return self._val.__hash__()


class Nil(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Nil, cls).__new__(cls, *args)
        return cls._instance

    def __str__(self):
        return "nil"


# TODO: How to handle function environment vs namespace
class Namespace(AReference):
    mappings = {}

    def __init__(self, name, parent=None, meta=None):
        AReference.__init__(self, meta)
        self.name = name
        self.parent = parent
        self.ns = {}

    def assign(self, name, value):
        self.ns[name] = value

    def resolve(self, name):
        if name in self.ns:
            return self.ns[name]

        if self.parent is not None:
            return self.parent.resolve(name)

        return None

    def resolveClass(self, name, mod=None):
        parts = str(name).split('.', 1)
        if len(parts) == 0:
            return None
        if len(parts) == 1:
            return mod.__dict__[name]

        if mod is None:
            top_level, rest = parts
            mod = sys.modules[top_level]
            return self.resolveClass(rest, mod)
        elif isinstance(mod, types.ModuleType):
            top_level, rest = parts
            mod = mod.__dict__[top_level]
            return self.resolveClass(rest, mod)

        return None

    def __str__(self):
        if self.parent is None:
            return self.ns.__str__() + " => None"
        return self.ns.__str__() + " => " + self.parent.__str__()

    def getMapping(self, name):
        return self.resolve(name)

    def intern(self, sym):
        if sym.ns is not None:
            raise Exception  # TODO: throw new IllegalArgumentException("Can't intern namespace-qualified symbol")

        v = None
        if sym in self.mappings:
            o = self.mappings[sym]
        else:
            o = None

        if o is None:
            v = Var(self, sym)
            self.mappings[sym] = v
            o = self.mappings[sym]

        if isinstance(o, Var) and o.ns == self:
            return o

        if v is not None:
            v = Var(self, sym)

        self.mappings[sym] = v

        return v

    @classmethod
    def find_or_create(cls, name):
        if cls.find(name) is not None:
            return cls.find(name)
        ns = Namespace(name)
        cls.mappings[name] = ns
        return ns

    @classmethod
    def find(cls, name):
        if name in cls.mappings:
            return cls.mappings[name]
        return None


class Var(ARef, IFn, IRef, Settable):
    macroKey = Keyword.intern(None, "macro")
    nameKey = Keyword.intern(None, "name")
    nsKey = Keyword.intern(None, "ns")
    rev = 0

    def __init__(self, ns, sym, root=None):
        ARef.__init__(self, None)
        self.ns = ns
        self.sym = sym
        # self.threadBound = AtomicBoolean(false)
        # self.root = Unbound(this)
        # self.setMeta(PersistentHashMap.EMPTY)
        self.threadBound = False
        self.root = None
        self.setMeta(Map())

        if root is not None:
            self.root = root
            self.rev += 1

    def setMeta(self, m):
        # ensure these basis keys
        # TODO: Should never be null?
        if m is None:
            m = Map()

        self.resetMeta(m.assoc(self.nameKey, self.sym).assoc(self.nsKey, self.ns))

    def isMacro(self):
        # TODO: Should never be null?
        if self.meta() is None:
            return False

        if self.macroKey in self.meta():
            return self.meta()[self.macroKey]
        else:
            return False


CURRENT_NS = None


def IF(args, ns):
    if l_eval(args.first(), ns):
        return l_eval(args.next().first(), ns)
    else:
        return l_eval(args.next().next().first(), ns)


def QUOTE(args, ns):
    return args.first()


def DEF(args, ns):
    name = args.first()
    if args.next() is not None:
        value = l_eval(args.next().first(), ns)
    else:
        value = None
    ns.assign(name, value)
    return name


def FN(args, ns):
    if isinstance(args.first(), Vector):
        argz = args.first()
        body = args.next().first()
    else:
        argz = args.next().first()
        body = args.next().next().first()

    class Func(AFunction):
        def invoke(self, *args):
            new_ns = Namespace("temp", ns)
            i = 0
            for arg in argz:
                new_ns.assign(arg, args[i])
                i += 1

            return l_eval(body, new_ns)

        def applyTo(self, arglist):
            self.invoke(*arglist)

    return Func


def LET(args, ns):
    argz = args.first()
    body = args.next().first()

    new_ns = Namespace("temp", ns)
    for i in range(0, len(argz)/2):
        name = argz[i*2]
        val = l_eval(argz[(i*2)+1], new_ns)
        new_ns.assign(name, val)

    return l_eval(body, new_ns)


def DO(args, ns):
    last = Nil()
    for form in args:
        last = l_eval(form, ns)

    return last


def NS(args, __env):
    global CURRENT_NS
    nsname = args.first()
    ns = Namespace.find_or_create(nsname)
    CURRENT_NS = ns
    return ns


def COMMENT(args, __env):
    return Nil()


def DOT(args, __env):
    clazz = __env.resolveClass(args.first())
    rest = args.next()
    if isinstance(clazz, types.TypeType) or isinstance(clazz, types.ModuleType):
        if rest.count() == 1 and isinstance(rest.first(), Symbol):
            member = rest.first()
            return clazz.__dict__[member.name]
        if rest.count() == 1 and isinstance(rest.first(), PersistentList):
            lst = rest.first()
            method = lst.first()
            argz = lst.next()
            return clazz.__dict__[method.name](*map(lambda r: l_eval(r, __env), argz))
        raise Exception  # TODO: implement this
    else:
        raise Exception  # TODO: implement this


def FIRST(*args):
    return args[0].first()


def REST(*args):
    return args[0].next()


def PLUS(*args):
    return sum(args)


def EQUALS(*args):
    return reduce(lambda x, y: x == y, args)


def META(obj):
    if isinstance(obj, IMeta):
        meta = obj.meta()
        if meta is None:
            return Nil()
        return meta
    return Nil()


def WITH_META(obj, m):
    return obj.withMeta(m)


def is_special(func):
    return func in [IF, QUOTE, DEF, FN, LET, DO, NS, COMMENT, DOT]


def eval_s_exp(s_exp, ns):
    rest = s_exp.next()
    func = l_eval(s_exp.first(), ns)

    if is_special(func):
        return func(rest, ns)
    elif isinstance(func, types.FunctionType):
        if rest is None:
            return func()
        evaled = map(lambda r: l_eval(r, ns), rest)
        return func(*evaled)
    else:
        if rest is None:
            return func().invoke()
        evaled = map(lambda r: l_eval(r, ns), rest)
        return func().invoke(*evaled)


def l_eval(exp, ns):
    if isinstance(exp, int):
        return exp
    if isinstance(exp, String):
        return exp
    if isinstance(exp, Boolean):
        return exp
    if isinstance(exp, Nil):
        return exp
    if isinstance(exp, Symbol):
        return ns.resolve(exp)
    if isinstance(exp, Keyword):
        return exp
    if isinstance(exp, PersistentList):
        return eval_s_exp(exp, ns)
    if isinstance(exp, Vector):
        return exp
    if isinstance(exp, Map):
        return exp


grammar = Grammar(
    """
    # regular language
    exps = whitespace* (exp whitespace*)+
    exp = number / boolean / nil / symbol / s_exp / vector / string / keyword / map / reader_macro
    number = ~"[0-9]+"
    symbol = "." / ~"[&*+=!_?\-a-zA-Z][.&*+=!_?\-a-zA-Z0-9]*"
    s_exp  = "(" whitespace* (exp whitespace*)* ")"
    vector = "[" whitespace* (exp whitespace*)* "]"
    string = ~"\\".*?\\""S
    keyword = ~":[a-z]*"
    boolean = "true" / "false"
    map = "{" whitespace* (exp whitespace exp whitespace*)* "}"
    nil = "nil"
    whitespace = single_whitespace_char+
    single_whitespace_char = " " / "\\n" / "\\t" / "\\r" / ","

    # reader macro table
    reader_macro = reader_comment / reader_quote / reader_metadata
    reader_comment = ~";.*$"M
    reader_quote = "'" exp
    reader_metadata = "^" (symbol / string / keyword / map) whitespace exp
    """)


def reduce_exp_tree(exp):
    """
    Trim the tree to get rid of unwanted nodes.  Ideally we wouldn't create them in the first place, though...
    """

    if exp.expr_name == "" and len(exp.children) == 0:
        return None

    children = []

    for node in exp.children:
        child = reduce_exp_tree(node)
        if child:
            if child['type'] != "" and child['type'] != "whitespace" and child['type'] != "single_whitespace_char"\
                    and child['type'] != "exp":
                children.append(child)
            else:
                children.extend(child['children'])

    return {'type': exp.expr_name,
            'children': children,
            'text': exp.text}


def process_tree(node):
    if node["type"] == "s_exp":
        return tree_to_list(node)
    elif node["type"] == "vector":
        return tree_to_vector(node)
    elif node["type"] == "map":
        return tree_to_map(node)
    elif node["type"] == "number":
        return int(node["text"])
    elif node["type"] == "symbol":
        return Symbol.intern(node["text"])
    elif node["type"] == "keyword":
        return Keyword(node["text"])
    elif node["type"] == "string":
        return String(node["text"][1:-1])
    elif node["type"] == "boolean":
        return Boolean(node["text"])
    elif node["type"] == "nil":
        return Nil()
    elif node["type"] == "reader_macro":
        return process_reader_macro(node["children"][0])


def process_reader_macro(node):
    if node["type"] == "reader_comment":
        return None
    elif node["type"] == "reader_quote":
        quote = {'type': "symbol",
                 'children': [],
                 'text': "quote"}
        new_children = node["children"]
        new_children.insert(0, quote)
        return process_tree({'type': "s_exp",
                             'children': node["children"],
                             'text': node["text"]})
    elif node["type"] == "reader_metadata":
        meta = process_tree(node["children"][0])

        if isinstance(meta, Symbol) or isinstance(meta, String):
            val = meta
            meta = Map()
            meta.assoc(Keyword(":tag"), val)
        elif isinstance(meta, Keyword):
            val = meta
            meta = Map()
            meta.assoc(val, Boolean("true"))
        elif not isinstance(meta, Map):
            print(type(meta))
            # TODO: better throw new IllegalArgumentException("Metadata must be Symbol,Keyword,String or Map");
            raise Exception

        exp = process_tree(node["children"][1])
        if isinstance(exp, IMeta):
            if isinstance(exp, IReference):
                exp.resetMeta(meta)
                return exp
            elif isinstance(exp, IObj):  # TODO: Maybe remove for speed???
                # TODO: Merge with existing meta
                return exp.withMeta(meta)
        else:
            # TODO: Throw error
            raise Exception


def tree_to_vector(tree):

    vec = Vector()

    for node in tree["children"]:
        vec.cons(process_tree(node))

    return vec


def tree_to_map(tree):

    ma = Map()

    for i in range(0, len(tree["children"])/2):
        key = tree["children"][i*2]
        value = tree["children"][(i*2)+1]

        ma.assoc(process_tree(key), process_tree(value))

    return ma


def tree_to_list(tree):
    """
    Put the tree into the internal list structure.  Ideally we'd load it into this in the first place, though...
    """

    lst = PersistentList.EMPTY

    for node in reversed(tree["children"]):
        p_node = process_tree(node)
        if p_node is not None:
            lst = lst.cons(p_node)

    if tree["type"] == "exp":
        return lst.first()
    else:
        return lst


def parse_eval(inp, ns):
    reduced_tree = reduce_exp_tree(grammar.parse(inp))
    program_list = tree_to_list(reduced_tree)

    ret = []

    for exp in program_list:
        ret.append(l_eval(exp, ns))

    return ret


def create_base_ns():
    ns = Namespace.find_or_create(Symbol.intern("clojure.core"))
    ns.ns = {Symbol.intern("if"): IF,
             Symbol.intern("quote"): QUOTE,
             Symbol.intern("def"): DEF,
             Symbol.intern("fn*"): FN,
             Symbol.intern("let"): LET,
             Symbol.intern("do"): DO,
             Symbol.intern("ns"): NS,
             Symbol.intern("comment"): COMMENT,
             Symbol.intern("."): DOT,
             Symbol.intern("+"): PLUS,
             Symbol.intern("="): EQUALS,
             Symbol.intern("first"): FIRST,
             Symbol.intern("rest"): REST,
             Symbol.intern("meta"): META,
             Symbol.intern("with-meta"): WITH_META}
    return ns


def main():
    global CURRENT_NS
    CURRENT_NS = create_base_ns()

    while True:
        line = raw_input(str(CURRENT_NS.name) + "=> ")
        evaled = parse_eval(line, CURRENT_NS)
        for val in evaled:
            if val is not None:
                print val

if __name__ == "__main__":
    sys.exit(main())
