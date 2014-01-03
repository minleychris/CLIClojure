#!/usr/bin/python

import sys
import getopt
import re

from parsimonious.grammar import Grammar



class IMeta(object):
    def meta(self):
        pass

class IReference(IMeta):
    def alterMeta(self, alterFn, args):
        pass;
    def resetMeta(self, m):
        pass

class AReference(IReference):
    def __init__(self, meta=None):
        self._meta = meta

    def meta(self):
        return self._meta

    def alterMeta(self, alterFn, args):
# TODO: This isn't implemented yet...        self._meta = alterFn.applyTo(Cons(self._meta, args))
        return self._meta

    def resetMeta(self, m):
        self._meta = m

class IObj(IMeta):
    def withMeta(self, meta):
        pass

class Obj(IObj):
    def __init__(self, meta=None):
        self._meta = meta

    def meta(self):
        return self._meta

    def withMeta(self, meta):
        pass

class ISeq(object):
    def first(self):
        pass
    def rest(self):
        pass
    def cons(self, n):
        pass

class ASeq(Obj, ISeq):
    def __init__(self, meta=None):
        Obj.__init__(self, meta)

class List(ASeq):
    def __init__(self, head=None, tail=None, meta=None):
        ASeq.__init__(self, meta)
        self._head = head
        self._tail = tail

    def __iter__(self):
        class ListIterator:
            def __init__(self, lst):
                self.lst = lst
            def next(self):
                if self.lst is None:
                    raise StopIteration
                head = self.lst._head
                self.lst = self.lst._tail
                return head

        return ListIterator(self)

    def _inner_str(self):
        if self._tail is None:
            return self._head.__str__()
        return self._head.__str__() + " " + self._tail._inner_str()

    def __str__(self):
        return "(" + self._inner_str() + ")"

    def first(self):
        return self._head
    def rest(self):
        return self._tail
    def cons(self, n):
        return List(n, self)
    def withMeta(self, meta):
        return List(self._head, self._tail, meta)

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
                ret = ret + " "
            ret = ret + str(self.data[i])

        return ret + "]"


    def first(self):
        return self.data[0]
    def rest(self):
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
        return self._data

    def __str__(self):
        ret = "{"
        for k,v in self._data.iteritems():
            ret = ret + str(k) + " " + str(v)
        ret = ret + "}"
        return ret

    def meta(self):
        return self._meta

    def withMeta(self, meta):
        return Map(self._data, meta)

class Symbol(IObj):
    def __init__(self, val, meta = None):
        self._val = val
        self._meta = meta

    def __str__(self):
        return self._val

    def __lt__(self, other):
        return isinstance(other, Symbol) and self._val.__lt__(other._val)

    def __le__(self, other):
        return isinstance(other, Symbol) and self._val.__le__(other._val)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self._val.__eq__(other._val)

    def __ne__(self, other):
        return isinstance(other, Symbol) and self._val.__ne__(other._val)

    def __gt__(self, other):
        return isinstance(other, Symbol) and self._val.__gt__(other._val)

    def __ge__(self, other):
        return isinstance(other, Symbol) and self._val.__ge__(other._val)

    def __hash__(self):
        return self._val.__hash__()

    def meta(self):
        return self._meta

    def withMeta(self, meta):
        return Symbol(self._val, self._meta)

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
            cls._instance = super(Nil, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __str__(self):
        return "nil"



# TODO: How to handle function environment vs namespace
class Namespace(AReference):
    mappings = {}

    def __init__(self, name, parent=None, meta=None):
        AReference.__init__(self, meta);
        self.name = name
        self.parent = parent
        self.ns = {}

    def assign(self, name, value):
        self.ns[name] = value

    def resolve(self, name):
        if self.ns.has_key(name):
            return self.ns[name]

        if self.parent != None:
            return self.parent.resolve(name)

        return None

    def __str__(self):
        if self.parent is None:
            return self.ns.__str__() + " => None"
        return self.ns.__str__() + " => " + self.parent.__str__()

    @classmethod
    def find_or_create(cls, name):
        if cls.mappings.has_key(name):
            return cls.mappings[name]
        ns = Namespace(name)
        cls.mappings[name] = ns
        return ns

CURRENT_NS = None


def IF(args, ns):
    if eval(args.first(), ns):
        return eval(args.rest().first(), ns)
    else:
        return eval(args.rest().rest().first(), ns)

def QUOTE(args, ns):
    return args.first()

def DEF(args, ns):
    name = args.first()
    value = eval(args.rest().first(), ns)
    ns.assign(name, value);
    return name

def FN(args, ns):
    argz = args.first()
    body = args.rest().first()

    class Func:
        def __init__(self, argz, body):
            self.argz = argz
            self.body = body

        def __call__(self, *args):
            new_ns = Namespace("temp", ns)
            i=0
            for arg in argz:
                new_ns.assign(arg, args[i])
                i = i+1

            return eval(body, new_ns)

    return Func(argz, body)

def LET(args, ns):
    argz = args.first()
    body = args.rest().first()

    new_ns = Namespace("temp", ns)
    for i in range(0,len(argz)/2):
        name = argz[i*2]
        val = eval(argz[(i*2)+1], new_ns)
        new_ns.assign(name, val)

    return eval(body, new_ns)

def DO(args, ns):
    last = Nil()
    for form in args:
        last = eval(form, ns)

    return last

def NS(args, __env):
    global CURRENT_NS
    nsname = args.first()
    ns = Namespace.find_or_create(nsname)
    CURRENT_NS = ns
    return ns

def COMMENT(args, __env):
    return Nil()


def CONS(*args):
    return args[1].cons(args[0])

def FIRST(*args):
    return args[0].first()

def REST(*args):
    return args[0].rest()

def PLUS(*args):
    return sum(args)

def EQUALS(*args):
    return reduce(lambda x,y: x==y, args)

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
    return func in [IF, QUOTE, DEF, FN, LET, DO, NS, COMMENT]



def eval_s_exp(s_exp, ns):
    rest = s_exp.rest()
    func = eval(s_exp.first(), ns)

    if is_special(func):
        return func(rest, ns)
    else:
        if rest is None:
            return func()
        evaled = map(lambda r: eval(r, ns), rest)
        return func(*evaled)

def eval(exp, ns):
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
    if isinstance(exp, List):
        return eval_s_exp(exp, ns)
    if isinstance(exp, Vector):
        return exp
    if isinstance(exp, Map):
        return exp





grammar = Grammar(
    """
    # regular language
    exps = (exp space)* exp
    exp = number / boolean / nil / symbol / s_exp / vector / string / keyword / map / reader_macro
    number = ~"[0-9]+"
    symbol = ~"[*+=!_?\-a-zA-Z][.*+=!_?\-a-zA-Z0-9]*"
    s_exp  = "(" (exp space)* exp ")"
    vector = "[" (exp space)* exp "]"
    string = ~"\\".*\\""
    keyword = ~":[a-z]*"
    boolean = "true" / "false"
    map = "{" exp space exp "}"
    nil = "nil"
    space = " "

    # reader macro table
    reader_macro = reader_comment / reader_quote
    reader_comment = ~";.*$"
    reader_quote = "'" exp
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
            if child['type'] != "" and child['type'] != "space" and child['type'] != "exp":
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
        return Symbol(node["text"])
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
    if node["type"] == "reader_quote":
        quote = {'type': "symbol",
                 'children': [],
                 'text': "quote"}
        new_children = node["children"]
        new_children.insert(0, quote)
        return process_tree({'type': "s_exp",
                             'children': node["children"],
                             'text': node["text"]})

def tree_to_vector(tree):

    vec = Vector()

    for node in tree["children"]:
        vec.cons(process_tree(node))

    return vec

def tree_to_map(tree):

    ma = Map()

    for i in range(0,len(tree["children"])/2):
        key = tree["children"][i*2]
        value = tree["children"][(i*2)+1]

        ma.assoc(process_tree(key), process_tree(value))

    return ma

def tree_to_list(tree):
    """
    Put the tree into the internal list structure.  Ideally we'd load it into this in the first place, though...
    """

    lst = None

    for node in reversed(tree["children"]):
        lst = List(process_tree(node), lst)

    if tree["type"] == "exp":
        return lst.first()
    else:
        return lst;


def parse_eval(input, ns):
    reduced_tree = reduce_exp_tree(grammar.parse(input))
    program_list = tree_to_list(reduced_tree)

    ret = []

    for exp in program_list:
        ret.append(eval(exp, ns))

    return ret

def create_base_ns():
    ns = Namespace.find_or_create(Symbol("clojure.core"))
    ns.ns = {Symbol("if"): IF,
             Symbol("quote"): QUOTE,
             Symbol("def"): DEF,
             Symbol("fn"): FN,
             Symbol("let"): LET,
             Symbol("do"): DO,
             Symbol("ns"): NS,
             Symbol("comment"): COMMENT,
             Symbol("+"): PLUS,
             Symbol("="): EQUALS,
             Symbol("cons"): CONS,
             Symbol("first"): FIRST,
             Symbol("rest"): REST,
             Symbol("meta"): META,
             Symbol("with-meta"): WITH_META}
    return ns

def main(argv=None):
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
