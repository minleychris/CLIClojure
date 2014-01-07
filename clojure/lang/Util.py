from interfaces import *


def equiv(k1, k2):  # TODO: Improve
    if k1 == k2:
        return True
    # if k1 is not None:
        # if(k1 instanceof Number && k2 instanceof Number)
        #     return Numbers.equal((Number)k1, (Number)k2);
        # elif(k1 instanceof IPersistentCollection || k2 instanceof IPersistentCollection)
        #     return pcequiv(k1,k2);
        # return k1.equals(k2)
    return False


def equals(k1, k2):
    if k1 == k2:
        return True
    return k1 is not None and k1.equals(k2)


def hasheq(o):
    if o is None:
        return 0
    if isinstance(o, IHashEq):
        return dohasheq(o)
    # if isinstance(o, Number):
    #     return Numbers.hasheq(o)         # TODO: We need to think about numbers differently here
    return o.hashCode()


def dohasheq(o):
    return o.hasheq()