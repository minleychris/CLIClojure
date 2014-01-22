from interfaces import *
from Seqs import *
import sys
import types


##
#
# This namespace contains the datastructures that are not yet finished and functions that have not yet found there final
# home.
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