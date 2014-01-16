class IMeta(object):
    def meta(self):
        pass


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


class Seqable(object):
    def seq(self):
        pass


class Counted(object):
    def count(self):
        pass

    def __len__(self):
        return self.count()


class IPersistentCollection(Seqable):
    def count(self):
        pass

    def cons(self, o):
        pass

    def empty(self):
        pass

    def equiv(self, o):
        pass


class ISeq(IPersistentCollection):
    def first(self):
        pass

    def next(self):
        pass

    def more(self):
        pass

    def cons(self, o):
        pass


class Sequential(object):
    pass


class IHashEq(object):
    def hasheq(self):
        pass


class IPersistentStack(IPersistentCollection):
    def peek(self):
        pass

    def pop(self):
        pass


class IReduce(object):
    def reduce(self, f, start=None):
        pass


class IPersistentList(Sequential, IPersistentStack):
    pass


class IFn(object):  # TODO: Java version implements Callable and Runnable
    def invoke(self, *args):
        pass

    def applyTo(self, arglist):
        pass


class AFn(IFn):
    # TODO: Make invoke throw arity error if its not of the right arity
    def applyTo(self, arglist):
        self.invoke(arglist)


class Fn(object):
    pass


class AFunction (AFn, IObj, Fn):  # TODO: Java version implements Serializable and Comparator

    # public volatile MethodImplCache __methodImplCache;

    def meta(self):
        return None

    def withMeta(self, meta):   # TODO: implement
        class ret(RestFn):
            def doInvoke(self, args):
                return AFunction.applyTo(self, args)

            def meta(self):
                return meta

            def withMeta(self, meta):
                return AFunction.withMeta(self, meta)

            def getRequiredArity(self):
                return 0
        return ret


class RestFn(AFunction):  # TODO: This is not implemented as fully as it probably should be...
    def getRequiredArity(self):
        pass

    def invoke(self, *args):
        return self.doInvoke(*args)

    def doInvoke(self, *args):
        return None

    def applyTo(self, arglist):
        self.doInvoke(arglist)


class IReference(IMeta):
    def alterMeta(self, alterFn, args):
        pass

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


class IDeref(object):
    def deref(self):
        pass


class IRef(IDeref):

    def setValidator(self, vf):
        pass

    def getValidator(self):
        pass

    def getWatches(self):
        pass

    def addWatch(self, key,  callback):
        pass

    def removeWatch(self, key):
        pass


class ARef(AReference, IRef):
    # protected volatile IFn validator = null;
    # private volatile IPersistentMap watches = PersistentHashMap.EMPTY;

    def __init__(self, meta=None):
        AReference.__init__(self, meta)
        self.validator = None
        self.watches = {}  # TODO: PersistentHashMap.EMPTY

    def validate(self, a1, a2=None):
        if a2 is None:
            vf = a1
            val = a2
            if vf is not None and not RT.booleanCast(vf.invoke(val)):
                #throw new IllegalStateException("Invalid reference state") TODO - plus better validation in general
                raise Exception
        else:
            val = a1
            self.validate(self.validator, val)

    def setValidator(self, vf):
        self.validate(vf, self.deref())
        self.validator = vf

    def getValidator(self):
        return self.validator

    def getWatches(self):                  # TODO: Watches stuff is syncronised - do we need to do anything with this??
        return self.watches

    def addWatch(self, key, callback):
        self.watches = self.watches.assoc(key, callback)
        return self

    def removeWatch(self, key):
        watches = self.watches.without(key)
        return self

    def notifyWatches(self, oldval, newval):
        ws = self.watches
        if ws.count() > 0:
            for k,fn in ws:
                if fn is not None:
                    fn.invoke(k, self, oldval, newval)


class Settable(object):
    def doSet(self, val):
        pass

    def doReset(self, val):
        pass