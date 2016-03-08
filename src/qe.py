""" Query and Evidence module
"""

from errors import *


class QandE(object):
    """ Represents a query variable
        and the evidence variables

    Attributes:
        filename(str): Query and Evidence input file.
        evidence(dict): The evidence
        query(str): The query
    """

    def __init__(self, filename):

        self.filename = filename
        self.evidence = {}
        self.query = None

        CheckExtension(self.filename)

        self.parse_file()

    def parse_file(self):
        """ Parses a Query and Evidence file
        """

        qefile = open(self.filename, 'r')

        for line in qefile:
            elements = line.split()

            # Ignore comment lines and blank lines
            if line[0] == '#' or not elements:
                continue

            if elements[0] == "QUERY":
                if self.query:
                    raise QEDuplicatedQuery

                if len(elements) != 2:
                    raise QEMalformedQuery

                self.query = elements[1]

            elif elements[0] == "EVIDENCE":
                if self.evidence:
                    raise QEDuplicatedEvidence

                if len(elements) < 2:
                    raise QEIncompleteEvidence

                if len(elements) - 2 != int(elements[1]) * 2:
                    raise QEMalformedEvidence

                for i in range(int(elements[1])):
                    self.evidence[elements[2*(i+1)]] = elements[2*(i+1)+1].lower()

    def write_solution(self, distrib, verbose):
        """ Write the solution contained in distrib to the solution file.

        Arguments:
            distrib: The VE object containing the result of the algorithm.
            verbose: Whether or not to write each step to the solution file.
        """

        out_filename = self.filename[:self.filename.rfind('.')] + ".sol"

        out_file = open(out_filename, 'w+')

        out_file.write("########## SOLUTION ##########\n")

        out_file.write("QUERY {}\n".format(self.query))

        evid_str = "EVIDENCE"
        for evid in self.evidence:
            evid_str += " {} {}".format(evid, self.evidence[evid])
        out_file.write(evid_str + "\n")

        probab_str = "QUERY_DIST"
        for probab in distrib.result.table:
            probab_str += " {} {}".format(probab[0], probab[-1])
        out_file.write(probab_str + "\n")

        if verbose:
            # write steps
            out_file.write("########## STEPS ##########\n")
            for log_line in distrib.log:
                out_file.write(log_line+"\n")

        out_file.close()


def CheckExtension(filename):
    """ Checks if the filename is correct

    Arguments:
        filename: The filename to check
    """

    ext = ".in"
    extfn = filename[filename.rfind('.'):]
    if ext != extfn:
        raise ExtensionError(ext)
