from interfaces import *
from Seqs import *


def seq(coll):
    if isinstance(coll, ASeq):
        return coll
    # elif isinstance(coll, LazySeq):  # TODO: Need to implement lazyseq still
    #     return coll.seq()
    else:
        return seqFrom(coll)


def seqFrom(coll):
    if isinstance(coll, Seqable):
        return coll.seq()
    elif coll is None:
        return None
    # elif(coll instanceof Iterable):
    #     return IteratorSeq.create(((Iterable) coll).iterator());  TODO: Implement python interop equivs?
    # elif(coll.getClass().isArray()):
    #     return ArraySeq.createFromObject(coll);
    # elif(coll instanceof CharSequence):
    #     return StringSeq.create((CharSequence) coll);
    # elif(coll instanceof Map):
    #     return seq(((Map) coll).entrySet());
    else:
        # TODO: Throw better error
        raise Exception
        # Class c = coll.getClass();
        # Class sc = c.getSuperclass();
        # throw new ExceptionInfo("Don't know how to create ISeq from: " + c.getName(),
        #                         map(Keyword.intern("instance"), coll));


def count(o):
    if isinstance(o, Counted):
        return o.count()
    return countFrom(Util.ret1(o, o is None))

def countFrom(o):
    if o is None:
        return 0
    elif isinstance(o, IPersistentCollection):
        s = seq(o)
        o = None
        i = 0
        while s is not None:
            if isinstance(s, Counted):
                return i + s.count()
            i += 1
            s = s.next()
        return i
    # elif(o instanceof CharSequence)  TODO: Implement python interop equivs?
    #     return ((CharSequence) o).length();
    # elif(o instanceof Collection)
    #     return ((Collection) o).size();
    # elif(o instanceof Map)
    #     return ((Map) o).size();
    # elif(o.getClass().isArray())
    #     return Array.getLength(o);

    # TODO: Throw better error
    raise Exception
    # throw new UnsupportedOperationException("count not supported on this type: " + o.getClass().getSimpleName());

def cons(x, coll):
    if coll is None:
        return PersistentList(x)
    elif isinstance(coll, ISeq):
        return Cons(x, coll)
    else:
        return Cons(x, seq(coll))