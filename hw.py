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
        return self.expr[0:self.expr.index('(')]


def is_var(x):
    if len(x) == 1 and x.islower():
        return True
    elif len(x) > 1 and (x[1] != '(' and x.islower()):
        return True
    return False


def is_compound(x):
    return re.findall('.*\(.+\)', x)


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
    pass


def fol_resolution(clauses, alpha):
    new = set([])
    while True:
        for c_i in clauses:
            for c_j in clauses:
                unify(c_i, c_j)
                # Apply unification
                resolvents = fol_resolve(c_i, c_j)
                if 'empty_clause' in resolvents:
                    return True
                new.add(resolvents)
        if new <= clauses:
            return False
        clauses.update(new)


if __name__ == '__main__':
    x = [['p(A,f(t))'],
         ['q(z)', '~p(z,f(B))'],
         ['~q(y)', 'r(y)'],
         ['~r(A)']]
    y = 'p(y,z)'
    mTheta = []
    unify(x, y, mTheta)
    '''
    TODO: 
    1-Make it accept negated form
    2-Make it apply the unifinigger
    3-Apply resolution
    '''
    print(mTheta)
'''
def unifinigger(E1,E2):

    pass
'''
