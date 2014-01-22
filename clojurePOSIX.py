#!/usr/bin/python

import sys
import types
from clojure.lang import *

from parsimonious.grammar import Grammar


##
#
# This is the main file for the clojurePOSIX project.  This contains the parser and runtime interaction stuff along with
# datastructures that are not yet finished and functions that have not yet found there final home.  Its a bit big but
# things will be removed from here when they are finished enough
#
##


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
        if val[0:1] == ":":
            self._val = val[1:]
        else:
            self._val = val

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
        if sym in self.ns:
            o = self.ns[sym]
        else:
            o = None

        if o is None:
            v = Var(self, sym)
            self.ns[sym] = v
            o = self.ns[sym]

        if isinstance(o, Var) and o.ns == self:
            return o

        if v is not None:
            v = Var(self, sym)

        self.ns[sym] = v

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
    privateKey = Keyword.intern(None, "private")
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
            return self.meta().get(self.macroKey)
        else:
            return False

    def isPublic(self):
        return not self.meta()[self.privateKey]

    def get(self):
        # if(!threadBound.get()) TODO
        #     return root;
        # return deref();
        return self.root

    def set(self, val):  # TODO
        self.root = val
        return self.root

    def invoke(self, *args):
        return self.root().invoke(*args)

    def applyTo(self, arglist):
        r = self.invoke(*arglist)
        return r

    @classmethod
    def create(cls, root):
        return Var(None, None, root)


CURRENT_NS = None
LOCAL_ENV = Var.create(None)


def currentNS():
    return CURRENT_NS


def IF(args, ns):
    if l_eval(args.first(), ns):
        return l_eval(args.next().first(), ns)
    else:
        return l_eval(args.next().next().first(), ns)


def QUOTE(args, ns):
    return args.first()


def DEF(args, ns):
    # (def x) or (def x initexpr) or (def x "docstring" initexpr)
    docstring = None

    if len(args) == 3 and isinstance(second(args), String):
        docstring = second(args)
        args = PersistentList.create([first(args), third(args)])

    if len(args) > 2:
        raise Exception  # TODO: Util.runtimeException("Too many arguments to def");
    elif len(args) < 1:
        raise Exception  # TODO: Util.runtimeException("Too few arguments to def");
    elif not isinstance(first(args), Symbol):
        raise Exception  # TODO: Util.runtimeException("First argument to def must be a Symbol");
    sym = first(args)
    v = lookupVar(sym, True)
    if v is None:
        raise Exception  # Util.runtimeException("Can't refer to qualified var that doesn't exist");
    if not v.ns == currentNS():
        if sym.ns is None:
            v = currentNS().intern(sym)
        else:
            raise Exception  # throw Util.runtimeException("Can't create defs outside of current ns")
    mm = sym.meta()
    # isDynamic = booleanCast(get(mm, dynamicKey))       TODO: Dynamic vars
    # if isDynamic:
    #     v.setDynamic()
    # if(!isDynamic && sym.name.startsWith("*") && sym.name.endsWith("*") && sym.name.length() > 2)
    # {
    #     RT.errPrintWriter().format("Warning: %1$s not declared dynamic and thus is not dynamically rebindable, "
    #                                +"but its name suggests otherwise. Please either indicate ^:dynamic %1$s or change the name. (%2$s:%3$d)\n",
    #                                sym, SOURCE_PATH.get(), LINE.get());
    # }
    # if booleanCast(get(mm, arglistsKey)):
    #     vm = v.meta()
    #     #drop quote
    #     vm = RT.assoc(vm, arglistsKey, second(mm.valAt(arglistsKey)))
    #     v.setMeta(vm)
    # source_path = SOURCE_PATH.get()       TODO: line numbers etc
    # source_path = source_path == null ? "NO_SOURCE_FILE" : source_path;
    # mm = (IPersistentMap) RT.assoc(mm, RT.LINE_KEY, LINE.get()).assoc(RT.COLUMN_KEY, COLUMN.get()).assoc(RT.FILE_KEY, source_path);

    if docstring is not None:
        mm = assoc(mm, DOC_KEY, docstring)
    # mm = elideMeta(mm)
    # meta = mm.count()==0 ? null:analyze(context == C.EVAL ? context : C.EXPRESSION, mm);

    v.setMeta(mm)

    name = args.first()
    if args.next() is not None:
        value = l_eval(args.next().first(), ns)
    else:
        value = None
    ns.intern(name).set(value)
    return name


def first(l):
    return l.first()


def second(l):
    return l.rest.first()


def third(l):
    return l.rest.rest.first()


def lookupVar(sym, internNew, registerMacro=True):
    var = None

    # note - ns-qualified vars in other namespaces must already exist
    if sym.ns is not None:
        ns = namespaceFor(sym)
        if ns is None:
            return None
        name = Symbol.intern(sym.name)
        if internNew and ns == currentNS():
            var = currentNS().intern(name)
        else:
            var = ns.findInternedVar(name)
    # elif sym.equals(NS):      TODO: Deal with at some time
    #     var = RT.NS_VAR
    # elif sym.equals(IN_NS):
    #     var = RT.IN_NS_VAR
    else:
        # is it mapped?
        o = currentNS().getMapping(sym)
        if o is None:
            # introduce a new var in the current ns
            if internNew:
                var = currentNS().intern(Symbol.intern(sym.name))
        elif isinstance(o, Var):
            var = o
        else:
            raise Exception("Expecting var, but " + str(sym) + " is mapped to " + str(o))  # TODO: Util.runtimeException("Expecting var, but " + sym + " is mapped to " + o)

    if var is not None and (not var.isMacro() or registerMacro):
        registerVar(var)
    return var

varsMap = {}


def registerVar(var):
    # if not VARS.isBound():   TODO: Make this better
    #     return
    # varsMap = VARS.deref()
    # id = RT.get(varsMap, var)
    # if id is None:
    #     VARS.set(RT.assoc(varsMap, var, registerConstant(var)))

    if varsMap is not None and (var not in varsMap or varsMap[var] is None):
        varsMap[var] = var


def namespaceFor(a1, a2=None):

    if a2 is None:
        inns = currentNS()
        sym = a1
    else:
        inns = a1
        sym = a2

    # note, presumes non-nil sym.ns
    # first check against currentNS' aliases...
    nsSym = Symbol.intern(sym.ns)
    ns = inns.lookupAlias(nsSym)
    if ns is None:
        # ...otherwise check the Namespaces map.
        ns = Namespace.find(nsSym)
    return ns


def FN(args, ns):
    if isinstance(args.first(), Vector):
        argz = args.first()
        body = args.next().first()
    elif isinstance(args.first(), Symbol):
        argz = args.next().first()
        body = args.next().next().first()

    class Func(AFunction):
        def invoke(self, *args):
            new_ns = Namespace("temp", ns)
            i = 0
            for arg in argz:
                if arg.name == "&":
                    new_ns.intern(argz[i+1]).set(PersistentList.create(args[i:]))
                    break
                new_ns.intern(arg).set(args[i])
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
        new_ns.intern(name).set(val)

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


def isSpecial(op):
    if not isinstance(op, Symbol):
        return False
    return op.name in ["if", "quote", "def", "fn*", "let*", "do", "ns", "comment", "."]

# Stuff from RT


def booleanCast(x):
    if isinstance(x, types.BooleanType):
        return x
    if isinstance(x, Boolean):
        return x._val
    return x is not None


def get(coll, key):
    # if isinstance(coll, ILookup):   TODO
    #     return coll.valAt(key);
    return getFrom(coll, key)


def getFrom(coll, key):
    if coll is None:
        return None
    elif isinstance(coll, Map):
        return coll.get(key)
    # else if(coll instanceof IPersistentSet) {  TODO
    #     IPersistentSet set = (IPersistentSet) coll;
    #     return set.get(key);
    # }
    elif isinstance(key, types.IntType) and (isinstance(coll, String) or isinstance(coll, types.StringType) or isinstance(coll, types.ListType)):
        if key >= 0 and key < len(coll):
            return coll[key]
        return None

    return None


def assoc(coll, key, val):
    if coll is None:
        #return PersistentArrayMap(new Object[]{key, val}) TODO
        return Map({key: val})
    return coll.assoc(key, val)


DOC_KEY = Keyword.intern(None, "doc")

# / Stuff from RT


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
        if not isSpecial(exp):
            return l_eval(ns.resolve(exp), ns)
        return ns.resolve(exp)
    if isinstance(exp, Keyword):
        return exp
    if isinstance(exp, PersistentList):
        return eval_s_exp(macroexpand(exp), ns)
    if isinstance(exp, Vector):
        return exp
    if isinstance(exp, Map):
        return exp
    if isinstance(exp, Var):
        return exp.get()


def macroexpand1(x):
    if isinstance(x, ISeq):
        form = x
        op = first(form)
        if isSpecial(op):
            return x

        # macro expansion
        v = isMacro(op)
        if v is not None:
            # try
            # {
            return v.applyTo(RT.cons(form, RT.cons(LOCAL_ENV.get(),form.next())))
            # }
            # catch(ArityException e)    TODO
            # {
            # // hide the 2 extra params for a macro
            # throw new ArityException(e.actual - 2, e.name);
            # }
        else:
            if isinstance(op, Symbol):
                sym = op
                sname = sym.name
                # (.substring s 2 5) => (. s substring 2 5)
                if sym.name[0] == '.':
                    raise Exception  # TOD: implement
                    # if length(form) < 2:
                    #     # throw new IllegalArgumentException("Malformed member expression, expecting (.member target ...)");  TODO
                    #     raise Exception
                    # meth = Symbol.intern(sname.substring(1))
                    # target = second(form)
                    # if HostExpr.maybeClass(target, False) is not None:
                    #     target = RT.list(IDENTITY, target).withMeta(RT.map(RT.TAG_KEY,CLASS))
                    # return preserveTag(form, RT.listStar(DOT, target, meth, form.next().next()))
                elif namesStaticMember(sym):
                    raise Exception  # TOD: implement
                    # target = Symbol.intern(sym.ns);
                    # c = HostExpr.maybeClass(target, False)
                    # if c is not None:
                    #     meth = Symbol.intern(sym.name);
                    #     return preserveTag(form, RT.listStar(DOT, target, meth, form.next()))
                else:
                    # (s.substring 2 5) => (. s substring 2 5)
                    # also (package.class.name ...) (. package.class name ...)
                    if sname[-1:] == ".":
                        raise Exception  # TOD: implement
                        # return RT.listStar(NEW, Symbol.intern(sname.substring(0, idx)), form.next())
    return x


def macroexpand(form):
    exf = macroexpand1(form)
    if exf != form:
        return macroexpand(exf)
    return form


def namesStaticMember(sym):
    return sym.ns is not None and namespaceFor(sym) is None


def isMacro(op):
    # no local macros for now
    if isinstance(op, Symbol) and referenceLocal(op) is not None:
        return None

    if isinstance(op, Symbol) or isinstance(op, Var):
        if isinstance(op, Var):
            v = op
        else:
            v = lookupVar(op, False, False)
        if v is not None and v.isMacro():
            if v.ns != currentNS() and not v.isPublic():
                # throw new IllegalStateException("var: " + v + " is not public") TODO
                raise Exception
            return v
    return None


def referenceLocal(sym):
    # if not LOCAL_ENV.isBound():
    #     return None
    # b = RT.get(LOCAL_ENV.deref(), sym)
    # if b is not None:
    #     method = METHOD.deref()
    #     closeOver(b, method)
    # return b
    return None


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
    global CURRENT_NS

    ns = Namespace.find_or_create(Symbol.intern("clojure.core"))
    ns.ns = {Symbol.intern("if"): IF,
             Symbol.intern("quote"): QUOTE,
             Symbol.intern("def"): DEF,
             Symbol.intern("fn*"): FN,
             Symbol.intern("let*"): LET,
             Symbol.intern("do"): DO,
             Symbol.intern("ns"): NS,
             Symbol.intern("comment"): COMMENT,
             Symbol.intern("."): DOT}

    ns.intern(Symbol.intern("+")).set(PLUS)
    ns.intern(Symbol.intern("=")).set(EQUALS)
    ns.intern(Symbol.intern("first")).set(FIRST)
    ns.intern(Symbol.intern("rest")).set(REST)
    ns.intern(Symbol.intern("meta")).set(META)
    ns.intern(Symbol.intern("with-meta")).set(WITH_META)

    CURRENT_NS = ns

    f = open('core.clj', 'r')
    f_string = f.read()
    evaled = parse_eval(f_string, ns)

    #TODO: debug
    for val in evaled:
        if val is not None:
            print val
    return ns


def main():
    create_base_ns()

    while True:
        line = raw_input(str(CURRENT_NS.name) + "=> ")
        evaled = parse_eval(line, CURRENT_NS)
        for val in evaled:
            if val is not None:
                print val

if __name__ == "__main__":
    sys.exit(main())
