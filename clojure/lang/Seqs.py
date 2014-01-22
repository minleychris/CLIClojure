import RT
import Util
from interfaces import *


##
#
# Namespace containing some of the Seq datastructures from the JVM Clojure clojure.lang package
#
##


class ASeq(Obj, ISeq, Sequential, IHashEq):  # Note: Java version implements java.util.List & java.io.Serializable also
    def __init__(self, meta=None):
        Obj.__init__(self, meta)
        self._hash = -1
        self._hasheq = -1

    def empty(self):
        return PersistentList.EMPTY

    def equiv(self, obj):
        if not isinstance(obj, Sequential):  # Note: Java version supports List here also
            return False
        ms = RT.seq(obj)
        s = self.seq()
        while s is not None:
            if ms is None or not Util.equiv(s.first(), ms.first()):
                return False
            s = s.next()
            ms = ms.next()
        return ms is None

    def equals(self, obj):                    # TODO: This is java - what about python?
        if not isinstance(obj, Sequential):  # Note: Java version supports List here also
            return False
        ms = RT.seq(obj)
        s = self.seq()
        while s is not None:
            if ms is None or not Util.equals(s.first(), ms.first()):
                return False
            s = s.next()
            ms = ms.next()
        return ms is None

    def hashCode(self):                    # TODO: This is java - what about python?
        if self._hash == -1:
            rhash = 1
            s = self.seq()
            while s is not None:
                if s.first() is None:
                    hval = 0
                else:
                    hval = s.first().hashCode()
                rhash = 31 * rhash + hval
                s = s.next()
            self._hash = rhash
        return self._hash

    def hasheq(self):
        if self._hasheq == -1:
            rhash = 1
            s = self.seq()
            while s is not None:
                rhash = 31 * rhash + Util.hasheq(s.first())
                s = s.next()
            self._hasheq = rhash
        return self._hasheq

    def count(self):
        i = 1
        s = self.seq()
        while s is not None:
            if isinstance(s, Counted):
                return i + s.count()
            s = s.next()
            i += 1
        return i

    def seq(self):
        return self

    def cons(self, o):
        return Cons(o, self)

    def more(self):
        s = self.next()
        if s is None:
            return PersistentList.EMPTY
        return s

    def __len__(self):
        return self.count()

    def __iter__(self):
        class SeqIterator:
            def __init__(self, seq):
                self.seq = seq

            def next(self):
                if self.seq is None:
                    raise StopIteration
                head = self.seq.first()
                self.seq = self.seq.next()
                return head

        return SeqIterator(self)



class Cons(ASeq):  # TODO: Java implements Serializable also

    def __init__(self, a1, a2, a3=None):
        # To keep the overloading of the Java version I've got to have an optional first argument!
        if a3 is None:
            ASeq.__init__(self)
            self._first = a1
            self._more = a2
        else:
            ASeq.__init__(self, a1)
            self._first = a2
            self._more = a3

    def first(self):
        return self._first

    def next(self):
        return self.more().seq()

    def more(self):
        if self._more is None:
            return PersistentList.EMPTY
        return self._more

    def count(self):
        return 1 + RT.count(self._more)

    def withMeta(self, meta):
        return Cons(meta, self._first, self._more)

    def __str__(self):
        return self.first().__str__() + self.next().__str__()  # TODO: better


class PersistentList(ASeq, IReduce, Counted):  # TODO: Java implements List also

    def __init__(self, a, b=None, c=None, d=None):
        # To keep the overloading of the Java version I've got to have an optional first argument!
        if b is None:
            ASeq.__init__(self)
            self._first = a
            self._rest = None
            self._count = 1
        else:
            ASeq.__init__(self, a)
            self._first = b
            self._rest = c
            self._count = d

    @classmethod
    def create(cls, init):
        ret = PersistentList.EMPTY
        for i in reversed(init):
            ret = ret.cons(i)
        return ret

    def first(self):
        return self._first

    def next(self):
        return self._rest

    def peek(self):
        return self.first()

    def pop(self):
        if self._rest is None:
            return PersistentList.EMPTY.withMeta(self._meta)
        return self._rest

    def count(self):
        return self._count

    def cons(self, o):
        return PersistentList(self.meta(), o, self, self._count + 1)

    def empty(self):
        return PersistentList.EMPTY.withMeta(self.meta())

    def withMeta(self, meta):
        if meta != self._meta:
            return PersistentList(meta, self._first, self._rest, self._count)
        return self

    def reduce(self, f, start=None):
        if start is None:
            ret = self.first()
        else:
            ret = f.invoke(start, self.first())
        s = self.next()
        while s is not None:
            ret = f.invoke(ret, s.first())
            s = s.next()
        return ret

    def __iter__(self):
        class ListIterator:
            def __init__(self, lst):
                self.lst = lst

            def next(self):
                if self.lst is None:
                    raise StopIteration
                head = self.lst.first()
                self.lst = self.lst.next()
                return head

        return ListIterator(self)

    def _inner_str(self):
        if self._rest is None:
            return self._first.__str__()
        return self._first.__str__() + " " + self._rest._inner_str()

    def __str__(self):
        return "(" + self._inner_str() + ")"

    class EmptyList(Obj, IPersistentList, ISeq, Counted):  # TODO: Java is also List

        def hashCode(self):
            return 1

        def equals(self, o):
            return isinstance(o, Sequential) and RT.seq(o) is None  # TODO: Java is also List

        def equiv(self, o):
            return self.equals(o)

        def __init__(self, meta=None):
            Obj.__init__(self, meta)

        def first(self):
            return None

        def next(self):
            return None

        def more(self):
            return self

        def cons(self, o):
            return PersistentList(self.meta(), o, None, 1)

        def empty(self):
            return self

        def withMeta(self, meta):
            if meta != self.meta():
                return PersistentList.EmptyList(meta)
            return self

        def peek(self):
            return None

        def pop(self):
            # TODO: Throw better error
            raise Exception
            # throw new IllegalStateException("Can't pop empty list");

        def count(self):
            return 0

        def seq(self):
            return None

        def __iter__(self):
            return [].__iter__()


class creator(RestFn):  # TODO: static?????
    def getRequiredArity(self):
        return 0

    def doInvoke(self, *args):
        # if isinstance(args, ArraySeq):  # TODO: When ArraySeq defined implement this optimisation
        #     Object[] argsarray = (Object[]) ((ArraySeq) args).array;
        #     IPersistentList ret = EMPTY;
        #     for(int i = argsarray.length - 1; i >= 0; --i)
        #         ret = (IPersistentList) ret.cons(argsarray[i]);
        #     return ret;
        return PersistentList.create(args)

    def withMeta(self, meta):
        # TODO: Throw better error
        raise Exception
        # throw new UnsupportedOperationException()

    def meta(self):
        return None

PersistentList.creator = creator
PersistentList.EMPTY = PersistentList.EmptyList()