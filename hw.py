import re

thetaDict = {}


class Compound:
    def __init__(self, expr):
        self.expr = expr

    def args(self):
        argList = re.search(r'\((.*)\)', self.expr).group(1).split(',')
        if len(argList) == 1:
            return argList[0]
        return argList

    def op(self):
        if self.expr[0] == '^':
            return self.expr[1:self.expr.index('(')]
        return self.expr[0:self.expr.index('(')]


def is_var(x):
    if len(x) == 1 and x.islower():
        return True
    elif len(x) > 1 and (x[1] != '(' and x.islower()):
        return True
    return False


def is_compound(x):
    return re.findall('\^?.*\(.+\)', x)


# noinspection PyTypeChecker
def unify(exp1, exp2, theta):
    if theta == 'fail':
        return 'fail'
    elif exp1 == exp2:
        return theta
    elif not isinstance(exp1, list) and is_var(exp1):
        return unify_var(exp1, exp2, theta)
    elif not isinstance(exp2, list) and is_var(exp2):
        return unify_var(exp2, exp1, theta)
    elif (not isinstance(exp1, list) and not isinstance(exp1, list)) and (is_compound(exp1) and is_compound(exp2)):
        comp1 = Compound(exp1)
        comp2 = Compound(exp2)
        return unify(comp1.args(), comp2.args(), unify(comp1.op(), comp2.op(), theta))
    elif isinstance(exp1, list) and isinstance(exp2, list):
        return unify(exp1[1:], exp2[1:], unify(exp1[0], exp2[0], theta))


    else:
        return 'fail'


def unify_var(var, x, theta):
    if (var in thetaDict) and (var, thetaDict[var]) in theta:
        return unify(thetaDict[var], x, theta)
    elif (x in thetaDict) and (x, thetaDict[x]) in theta:
        return unify(var, thetaDict[x], theta)
    else:
        thetaDict[var] = x
        theta.append((var, x))
        return theta


def fol_resolve(c1, c2):
    global thetaDict
    resolvents = set([])
    for idx1,ic1 in enumerate(c1):
        for idx2,ic2 in enumerate(c2):
            comp1 = Compound(ic1)
            comp2 = Compound(ic2)
            if comp1.op() == comp2.op():
                theta = []
                thetaDict = {}
                unify(ic1,ic2,theta)
                c2 = apply_unification(c2,theta)
                del c1[idx1]
                del c2[idx2]
                sc1= set(c1)
                sc2 = set(c2)
                sc1.update(sc2)
                resolvents.update(sc1)
                return resolvents




def fol_resolution(B,G, alpha):
    new = set([])
    while True:
        for c_i in B:
            for c_j in G:
                resolvents = fol_resolve(c_i, c_j)
                if 'empty_clause' in resolvents:
                    return True
                new.update(resolvents)
        total = B.update(G)
        if new <= total:
            return False
        G.update(new)

def apply_unification(C,theta):
    new  = []
    for c in C:
        tmp = ''
        for rep in theta:
            tmp = re.sub(rep[0],rep[1],c)
        new.append(tmp)
    return new
if __name__ == '__main__':
    x = [['p(A,f(t))'],
         ['q(z)', '~p(z,f(B))'],
         ['~q(y)', 'r(y)'],
         ['~r(A)']]
    test = 'p(A,z)'
    y = 'p(y,B)'
    mTheta = []
    unify(test, y, mTheta)
    '''
    TODO: 
    2-Make it apply the unifinigger
    3-Apply resolution
    '''
    resolve1 = ['^r(A)']
    resolve2 = ['^q(y)','r(y)']
    fol_resolve(resolve1,resolve2)
    print(mTheta)
'''
def unifinigger(E1,E2):

    pass
'''
