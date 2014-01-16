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