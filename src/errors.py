""" Errors
"""

class ExtensionError(Exception):
    """ Wrong file extension
    """

    def __init__(self, desired_ext):
        self.desired_ext = desired_ext

    def __str__(self):
        return repr("Wrong file extension! Must be {}".format(
                self.desired_ext))


class BNFileError(Exception):
    """ Error in the file
    """

    def __init__(self, ind):
        ERROR_DICT = {
        1: "name is always mandatory and should always be the first VAR key!",
        2: "variable values are always mandatory and were not defined!",
        999: "bn input file not correctly defined"
        }

        self.error_ind = int(ind)
        self.ERROR_DICT = ERROR_DICT

    def __str__(self):
        return repr(self.ERROR_DICT[self.error_ind])


class BNDuplicatedField(Exception):
    """ Duplicated Field
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Duplicated Field")


class BNIncompleteEntry(Exception):
    """ Incomplete Entry
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Incomplete Entry")


class BNDuplicatedEntry(Exception):
    """ Duplicated Entry
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Duplicated Entry")


class BNUnknownFieldType(Exception):
    """ Unknown Field Type
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Unknown Field Type")


class BNWrongNumberArguments(Exception):
    """ Wrong Number of Arguments
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Wrong Number of Arguments")


class BNDuplicatedNameOrAlias(Exception):
    """ Duplicated Name or Alias
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Duplicated Name or Alias")


class BNMalformedTable(Exception):
    """ Malformed Table
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Malformed Table")


class QEIncompleteEvidence(Exception):
    """ Incomplete Evidence
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Incomplete Evidence")


class QEMalformedEvidence(Exception):
    """ Malformed Evidence
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Malformed Evidence")


class QEDuplicatedEvidence(Exception):
    """ Duplicated Evidence
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Duplicated Evidence")


class QEDuplicatedQuery(Exception):
    """ Duplicated Query
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Duplicated Query")


class QEMalformedQuery(Exception):
    """ Malformed Query
    """

    def __init__(self):
        pass

    def __str__(self):
        return repr("Malformed Query")