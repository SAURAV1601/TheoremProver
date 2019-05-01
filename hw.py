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
        if self.expr[0] == '~':
            return self.expr[1:self.expr.index('(')]
        return self.expr[0:self.expr.index('(')]


def is_var(x):
    if len(x) == 1 and x.islower():
        return True
    elif len(x) > 1 and (x[1] != '(' and x.islower()):
        return True
    return False


def is_compound(x):
    return re.findall('~?.*\(.+\)', x)


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


def eliminate_tautology(resolvents):
    global thetaDict
    to_be_removed = set()
    for i in resolvents:
        for j in resolvents:
            comp1 = Compound(i)
            comp2 = Compound(j)
            if comp1.op() == comp2.op() and i[0] != j[0]:
                theta = []
                thetaDict = {}
                unify(i, j, theta)
                if theta:
                    to_be_removed.add(i)
                    to_be_removed.add(j)
    return resolvents.difference(to_be_removed)


def is_subsumption(resolvents, B, G):
    global thetaDict
    U = B.union(G)
    for clause in resolvents:
        for kb_clause in U:
            if len(kb_clause) == 1:
                if clause == kb_clause:
                    return True
                c1 = Compound(clause)
                c2 = Compound(kb_clause[0])
                if c1.op() == c2.op() and clause[0] == kb_clause[0][0]:
                    args1 = c1.args()
                    args2 = c2.args()

                    if isinstance(args1, list) and isinstance(args2, list):
                        subsumed = True
                        for i in range(args1):
                            if not is_var(args2[i]) and args1[i] != args2[i]:
                                subsumed = False
                        return subsumed
                    else:
                        if type(args1) != type(args2):
                            return False
                        if not is_var(args2) and args1 != args2:
                            return False
                        return True
    return False


def fol_resolve(c1, c2):
    global thetaDict
    resolvents = set([])
    for idx1, ic1 in enumerate(c1):
        for idx2, ic2 in enumerate(c2):
            comp1 = Compound(ic1)
            comp2 = Compound(ic2)
            if comp1.op() == comp2.op() and ic1[0] != ic2[0]:
                theta = []
                thetaDict = {}
                unify(ic1, ic2, theta)
                c1 = apply_unification(c1, theta)
                c2 = apply_unification(c2, theta)
                del c1[idx1]
                del c2[idx2]
                sc1 = set(c1)
                sc2 = set(c2)
                sc1.update(sc2)
                resolvents.update(sc1)
                if not resolvents:
                    return 'empty_clause'
                resolvents = eliminate_tautology(resolvents)
                return tuple(resolvents)


def fol_resolution(B, G):
    new = set([])
    bstr = ''
    while True:
        for c_i in B:
            for c_j in G:

                resolvents = fol_resolve(c_i, c_j)
                if resolvents == 'empty_clause':
                    bstr += ','.join(map(str, c_j)) + '$' + ','.join(map(str, c_i)) + '$' + 'empty_clause'
                    print('yes')
                    print(bstr)
                    return True
                elif resolvents and resolvents in G:
                    continue
                elif resolvents:
                    if not is_subsumption(resolvents, B, G):
                        bstr += ','.join(map(str, c_j)) + '$' + ','.join(map(str, c_i)) + '$' + ','.join(
                            map(str, resolvents)) + '\n'
                        new.add(resolvents)
        if new <= G or new <= B:
            return False
        G.update(new)


def apply_unification(C, theta):
    new = []
    for c in C:
        tmp = ''
        for rep in theta:
            tmp = re.sub(rep[0], rep[1], c)
        new.append(tmp)
    return new


def read_file():
    B = []
    G = []
    with open('input.txt') as f:
        nums = list(map(int, f.readline()[:-1].split(' ')))
        for i in range(sum(nums)):
            lstr = f.readline()[:-1]
            cnt = 0
            idxs = []
            for idx, chr in enumerate(lstr):
                if chr == '(':
                    cnt += 1
                elif chr == ')':
                    cnt -= 1
                elif chr == ',' and cnt == 0:
                    idxs.append(idx)
            if not idxs:
                if i >= nums[0]:
                    G.append(tuple([lstr]))
                else:
                    B.append(tuple([lstr]))
                continue

            clauses = []
            end = len(lstr) - 1
            idxs.append(end)
            for idx in range(len(idxs)):
                if idx == 0:
                    clauses.append(lstr[0:idxs[idx]])
                else:
                    clauses.append(lstr[idxs[idx - 1] + 1:idxs[idx]+1])
            if i >= nums[0]:
                G.append(tuple(clauses))
            else:
                B.append(tuple(clauses))
    return (G, B)


if __name__ == '__main__':
    G,B = read_file()
    fol_resolution(set(B), set(G))
