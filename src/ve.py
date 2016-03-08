""" VE Algorithm
"""

from errors import *
from bayes import Variable


class VE(object):
    """ Class containing all the methods for the VE algorithm

    Attributes:
        bn: The beysian network on which to perform the algorithm.
        qe: The dictionary containing the evidence.
        query: The query.
        result: The result of the algorithm.
        log: The log array.
    """

    def __init__(self, bn, qe, verbose):
        self.bn = bn
        self.qe = {}

        # Transform the name of the query variable into an actual reference
        self.query = bn["dict"][qe.query]

        # Transform the names in the evidence into actual references
        for e in qe.evidence:
            self.qe[bn["dict"][e]] = qe.evidence[e]

        (self.result, self.log) = VE.elimination_ask(self.query, self.qe, self.bn, verbose)

    @staticmethod
    def elimination_ask(X, e, bn, verbose=False):
        """ Variable elimination algorithm

        Arguments:
            X: Query variable
            e: Evidence specified as an event
            bn: Belief network
        Returns:
            The probability P(X|e)
        """

        log = []

        factors = []
        variables = VE.sort_nodes(bn["list"])

        for variable in variables:
            factors.append(VE.make_factors(variable, e))
            if verbose:
                log.append("Added {} to the factors".format(variable.name))
                log.append("Factors are now:")

                for factor in factors:
                    VE.write_table_log(log, factor)


            # check if variable is hidden
            if variable != X and variable not in e:
                PwP = VE.pointwise_product(factors)
                if verbose:
                    log.append("The variable {} is not in the query nor in the evidence".format(variable.name))
                    log.append("The pointwise product of the factors results in:")
                    VE.write_table_log(log, PwP)
                    log.append("These were summed out")
                factors = VE.sum_out(variable, PwP)

        log.append("Factors are in the end:")
        for factor in factors:
            factor_log = ""
            for fac_var in factor.table_header:
                factor_log += "{} ".format(fac_var.name)
            log.append(factor_log)

            for line in factor.table:
                log_line = ""
                for col in line:
                    log_line += "{} ".format(str(col))
                log.append(log_line)

        PwP = VE.pointwise_product(factors)
        if verbose:
            log.append("The pointwise product of the factors results in:")
            VE.write_table_log(log, PwP)
        normalized = VE.normalize(PwP)
        if verbose:
            log.append("Which finally, normalizing the probabilities, result in:")
            VE.write_table_log(log, normalized)
        return (normalized, log)

    @staticmethod
    def write_table_log(log, node):
        """ Writes one CPT to the log array

        Arguments:
            log: The log array
            node: The node that contains the CPT
        """

        factor_log = ""
        for fac_var in node.table_header:
            factor_log += "{} ".format(fac_var.name)
        log.append(factor_log)

        for line in node.table:
            log_line = ""
            for col in line:
                log_line += "{} ".format(str(col))
            log.append(log_line)

    @staticmethod
    def sort_nodes(bn):
        """ Sort the nodes from leaf to root

        Arguments:
            bn: Belief network

        Returns:
            The sorted nodes of the belief network, from leaf to root
        """

        lsorted = []

        while True:
            done = True
            for node in bn:
                if (not node.children and node not in lsorted):
                    lsorted.append(node)
                    for parent in node.parents["list"]:
                        parent.children.remove(node)
                    done = False
            if done:
                break

        return lsorted

    @staticmethod
    def make_factors(variable, e):
        """ Remove evidence from CPT

        Arguments:
            variable: Node on which to remove the evidence from
            e: Evidence to be removed from variable

        Returns:
            The Node without the evidence
        """

        # return variable
        res_table = []
        res_table_header = list(variable.table_header)
        changed = False

        # makes a list of the variables of the table
        remind = []
        for i in range(len(variable.table_header)):
            if variable.table_header[i] in e:
                remind.append(i)
                changed = True

        if changed:
            remind.sort()
            remind.reverse()

            for j in variable.table:
                good = True
                for k in remind:
                    if e[variable.table_header[k]] != j[k]:
                        good = False
                        break
                if good:
                    res_table.append(j)
                    for i in remind:
                        res_table[-1].pop(i)

        if changed:
            variable.table = res_table
            variable.table_header = res_table_header
            for i in remind:
                variable.table_header.pop(i)

        return variable

    @staticmethod
    def sum_out(variable, PwP):
        """ Removes the column of the given variable, and sums the \
            probabilities of the common remaining lines.

        Arguments:
            variable: Variable to remove
            factors: Node on which to perform the removal

        Returns:
            The new node containing the table without the variable.
        """

        new_var = Variable()
        new_var.table_header = list(PwP.table_header)
        new_var.table_header.remove(variable)
        new_var.table = []
        checked = [False for i in range(len(PwP.table))]

        # index of the variable to skip
        askip = PwP.table_header.index(variable)

        for i in range(len(PwP.table)):
            summed = 0
            # skips the already checked
            if not checked[i]:
                for j in range(i, len(PwP.table)):
                    if (not checked[j]):
                        toappend = []
                        flag = True
                        for a in range(len(PwP.table_header)):
                            if a == askip:
                                continue
                            elif (PwP.table[i][a] != PwP.table[j][a]):
                                flag = False
                                break
                            else:
                                toappend.append(PwP.table[i][a])
                        if flag:
                            summed += PwP.table[j][-1]
                            checked[j] = True
                toappend = []
                for j in range(len(PwP.table_header)):
                    if (PwP.table_header[j] != variable):
                        toappend.append(PwP.table[i][j])
                toappend.append(summed)
                new_var.table.append(toappend)
        return [new_var]

    @staticmethod
    def normalize(variable):
        """ Normalizes the probabilities of the result of a pointwise
            product operation.

        Arguments:
            variable: The variable containing the CPT to normalize

        Returns:
            The normalized matrix (the sum of all probabilities is 1)
        """

        PwPsum = 0

        for line in variable.table:
            PwPsum += line[-1]

        for i in range(len(variable.table)):
            variable.table[i][-1] = variable.table[i][-1]/PwPsum

        return variable

    @staticmethod
    def pointwise_product(factors):
        """ Performs the pointwise product between all the nodes in the \
            factors list

        Arguments:
            factors: The several nodes on which to perform the product

        """

        if len(factors) == 1:
            return factors[0]

        new_var = Variable()

        for f in factors:
            if not new_var.table_header:
                new_var.table_header = f.table_header
                new_var.table = f.table
                continue
            else:
                common = set(new_var.table_header) & set(f.table_header)
                # get their indexes in the res
                new_varindex = [new_var.table_header.index(k) for k in common]
                findex = []

                # get their indexes in the new factor
                for i in new_varindex:
                    findex.append(
                        f.table_header.index(new_var.table_header[i])
                    )

                # New table_header with all the variables
                newtable_header = []
                # the common variables
                for i in range(len(common)):
                    newtable_header.append(
                        new_var.table_header[new_varindex[i]]
                    )
                # the variables only in the new_var factor
                for i in range(len(new_var.table_header)):
                    if new_var.table_header[i] not in common:
                        newtable_header.append(new_var.table_header[i])
                # the variables only in the new factor
                for i in range(len(f.table_header)):
                    if f.table_header[i] not in common:
                        newtable_header.append(f.table_header[i])

                # create and fill the new table
                newtable = []

                # for each line of the new_var factor
                for l in new_var.table:
                    # and for each line of the new factor
                    for t in f.table:
                        same = True
                        # if it's common skip
                        for i in range(len(common)):
                            if t[findex[i]] != l[new_varindex[i]]:
                                same = False
                                break
                        # if it has the same common var values
                        if same:
                            toappend = []
                            # values of the common variables
                            for i in range(len(common)):
                                toappend.append(t[findex[i]])
                            # values of the variables in the existing table
                            for i in range(len(new_var.table_header)):
                                if new_var.table_header[i] not in common:
                                    toappend.append(l[i])
                            # values in the new table
                            for i in range(len(f.table_header)):
                                if f.table_header[i] not in common:
                                    toappend.append(t[i])
                            toappend.append(t[-1]*l[-1])
                            newtable.append(toappend)

                # set the newly calculated table as the new_var table
                new_var.table = newtable
                # set the newly calculated header as the res header
                new_var.table_header = newtable_header

        return new_var
