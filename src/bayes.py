""" Bayes Network module
"""

from errors import *


class Variable(object):
    """ Node of the Bayesian Network

    Attributes:
        name(str): Name of the variable.
        values(str): Possible values in lowercase
        alias: Optional name that can be used to refer to the variable
        parents: Parents of the node
        children: children of the node

    """

    def __init__(self, data={}):
        if not data:
            self.parents = {
                "list": [],
                "dict": {}
            }

            self.table_header = []
            self.table = []
            return

        if "name" not in data or "values" not in data:
            raise BNIncompleteEntry

        self.name = data["name"]
        self.values = [a.lower() for a in data["values"]]

        if "alias" in data:
            self.alias = data["alias"]
        else:
            self.alias = None

        if "parents" in data:
            self._parents = data["parents"]
        else:
            self._parents = []

        self.children = []

    def convert_parents(self, node):
        """ Converts the parents from strings to actual references to the
            parent nodes.

        Arguments:
            node: Node on which to turn the parents from strings to references
        """

        self.parents = {
            "list": [],
            "dict": {}
        }

        for parent in self._parents:
            parent_obj = node[parent]
            parent_obj.children.append(self)

            self.parents["list"].append(parent_obj)

            for name in parent_obj.names():
                self.parents["dict"][name] = parent_obj

        del(self._parents)

    def populate_cpt(self, table):
        """ Populates the CPT based of the string read from the file

        Arguments:
            table: The CPT
        """

        cols = len(self.parents["list"]) + 2
        lines = len(table) / cols

        if int(lines) != lines:
            raise BNMalformedTable

        # check if number of lines is correct
        l = len(self.values)
        for parent in self.parents["list"]:
            l *= len(parent.values)

        if l != lines:
            raise BNMalformedTable

        self.table_header = [self] + self.parents["list"]
        self.table = []
        for n in range(l):
            line = table[n*cols:(n+1)*cols]

            values = [a.lower() for a in line[:-1]]
            values.append(float(line[-1]))
            self.table.append(values)

    def names(self):
        """ Get all the names which this variable can have

        Returns:
            A list containing the name and the alias, if it is defined.
        """

        names = [self.name]
        if self.alias:
            names.append(self.alias)

        return names


class BayesN(object):
    """ Represents a Bayesian Network

    Attributes:
        filename(str): Bayesian Network input file.
        nodes(dict): Nodes of the BN in both list and dict format for
            unique and easy access by name respectively.
    """

    # Entry types fields can be:
    #  - single (one value after field name)
    #  - multiple (multiple values after field name)
    #  - multiple-lines (multiple values in multiple lines after field name)
    ENTRY_TYPES = {
        "VAR": {
            "class": Variable,
            "valid-fields": {
                "name": "single",
                "alias": "single",
                "parents": "multiple",
                "values": "multiple"
            }
        },
        "CPT": {
            "Class": Variable,
            "valid-fields": {
                "var": "single",
                "table": "multiple-lines"
            }
        }
    }

    def __init__(self, filename):

        self.filename = filename
        self.nodes = None

        CheckExtension(self.filename)

        data = self.parse_file(filename)

        self.populate_vars(data["VAR"])
        self.populate_cpts(data["CPT"])

    def populate_vars(self, variables):
        """ Creates all the variables as objects, and converts the parents \
            stings into references

        Arguments:
            variables: Variables on which to perform the operation.
        """

        # create all the nodes
        self.nodes = {
            "list": [],
            "dict": {}
        }
        for variable in variables:
            new_var = Variable(variable)
            self.nodes["list"].append(new_var)

            names = new_var.names()
            for name in names:
                # check for name/alias clashes
                if name in self.nodes:
                    raise BNDuplicatedNameOrAlias
                self.nodes["dict"][name] = new_var

        # for each variable, transform the parents into actual references
        #to the parent object
        for node in self.nodes["list"]:
            node.convert_parents(self.nodes["dict"])

    def populate_cpts(self, cpts):
        """ Creates all the CPTs as objects, and converts the variable names \
            stings into references

        Arguments:
            cpts: All the tables as described in the input file.
        """

        for cpt in cpts:
            if "var" in cpt and "table" in cpt:
                self.nodes["dict"][cpt["var"]].populate_cpt(cpt["table"])
            else:
                raise BNIncompleteEntry

    def parse_file(self, filename):
        """ Parses an input file

        Arguments:
            filename: The name of the file to be parsed.
        """

        # Opens input file and starts parsing it
        bnfile = open(self.filename, 'r')

        current = {
        }

        data = {
            "VAR": [],
            "CPT": []
        }

        line = bnfile.readline()

        while line:
            elements = line.split()

            # Ignore comment lines and blank lines
            if line[0] == '#' or not elements:
                line = bnfile.readline()
                continue

            # beginning of a new entry
            elif len(elements) == 1 and elements[0] in self.ENTRY_TYPES:
                # save the previous entry
                if current:
                    data[current["type"]].append(current["data"])

                # create a new empty entry
                current = {
                    "type": elements[0],
                    "data": {}
                }
                line = bnfile.readline()
                continue

            # check for duplicated fields
            elif elements[0] in current["data"]:
                raise BNDuplicatedField

            # check if the field is a valid one
            valid_fields = self.ENTRY_TYPES[current["type"]]["valid-fields"]

            if elements[0] in valid_fields:
                field_type = valid_fields[elements[0]]

                if field_type == "single":
                    if len(elements) != 2:
                        raise BNWrongNumberArguments

                    current["data"][elements[0]] = elements[1]

                elif field_type == "multiple":
                    if len(elements) < 2:
                        raise BNWrongNumberArguments

                    current["data"][elements[0]] = elements[1:]

                elif field_type == "multiple-lines":
                    new_data = []
                    tag = elements[0]

                    if len(elements) > 1:
                        new_data += elements[1:]

                    line = bnfile.readline()
                    while line:
                        mul_elements = line.split()

                        # Ignore comment lines and blank lines
                        if line[0] == '#' or not mul_elements:
                            line = bnfile.readline()
                            continue

                        # beginning of a new entry
                        elif (len(mul_elements) == 1 and
                              mul_elements[0] in self.ENTRY_TYPES):
                            # break and let the outer loop take care of the
                            #line
                            break

                        # check if another field of the same entry has come up
                        elif line[0] in valid_fields:
                            # break and let the outer loop take care of the
                            #line
                            break
                        else:
                            new_data += mul_elements

                        line = bnfile.readline()

                    current["data"][tag] = new_data
                    continue

                else:
                    raise BNUnknownFieldType

            line = bnfile.readline()

        if current:
            data[current["type"]].append(current["data"])

        return data


def CheckExtension(filename):
    """ Checks if the filename is correct

    Arguments:
        filename: The filename to check
    """

    ext = ".bn"
    extfn = filename[filename.rfind('.'):]
    if ext != extfn:
        raise ExtensionError(ext)
