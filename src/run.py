#!/usr/bin/python3

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
import logging
import sys

from bayes import *
from qe import *
from ve import *


class ArgParser(ArgumentParser):
    """ Modify ArgumentParser error handling behaviour """

    def error(self, message):
        """ Writes the error message in arguments handling

        Args:
            message (str): Error message.
        """

        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    """ Main function of the program.

    Parses arguments and invokes the processing functions.
    """

    # Parse the arguments

    parser = ArgParser(description="", epilog="",
                       formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "bayes",
        help="input file where the bayesian network is defined.")
    parser.add_argument(
        "qande",
        help="input file where the query and evidence are defined.")
    parser.add_argument("-verbose", action="store_true",
                        help="Print out all steps of the VE algorithm")
    parser.add_argument("-l", "--logfile",
                        help="file where the log is to be written to (instead \
                            of the console)")
    parser.add_argument("-d", "--debug",
                        help="debug", action="count",
                        default=0)

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S',
                        filename=args.logfile,
                        level=10*(
                            (4-args.debug) if args.debug < 4 else 1
                        ))

    # Parses the Bayesian Network description file
    logging.debug("Parsing file {}".format(args.bayes))
    bn = BayesN(args.bayes)
    logging.debug("Done parsing BN file")

    # Parses the query and evidence description file
    logging.debug("Parsing file {}".format(args.qande))
    qe = QandE(args.qande)
    logging.debug("Done parsing Q&E file")

    # Parses the query and evidence description file
    logging.debug("Solving...")
    ve = VE(bn.nodes, qe, args.verbose)
    logging.debug("Solved!")

    logging.debug("Writing solution file...")
    qe.write_solution(ve, args.verbose)
    logging.debug("Solution written to file!")


if __name__ == '__main__':
    main()
