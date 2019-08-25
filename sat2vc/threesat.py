#!/usr/bin/false
#
# Copyright 2019
# M. Ayaz Dzulfikar, University of Indonesia, Indonesia
# Johannes K. Fichte, TU Dresden, Germany
# Markus Hecher, TU Wien, Austria
#
# sat2vc is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# sat2vc is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with
# sat2vc.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import logging
import mimetypes
from bz2 import BZ2File
import gzip

try:
    import backports.lzma as xz

    xz = True
except ImportError:
    xz = False


class ThreeSat:
    def __init__(self):
        self._variables = set()
        self._clauses = []
        self._aux_counter = 1000000000

    @property
    def variables(self):
        return self._variables

    @property
    def clauses(self):
        return self._clauses

    def set_counter(self, counter):
        self._aux_counter = counter

    def get_new_aux(self):
        self._aux_counter += 1
        return self._aux_counter

    def _real_add_clause(self, variables):
        self._clauses.append(variables)
        for var in variables:
            self._variables.add(abs(var))

    def add_clause(self, variables):
        if len(variables) == 0:
            return
        if len(variables) > 3:
            logging.error(
                "Invalid number of variables in disjunction clause. Expected in range[1, 3], got {} instead".format(
                    len(variables)))
            exit(2)

        if len(variables) == 1:
            a = self.get_new_aux()
            b = self.get_new_aux()

            for i in range(-1, 2, 2):
                for j in range(-1, 2, 2):
                    self._real_add_clause([variables[0], i * a, j * b])
        elif len(variables) == 2:
            a = self.get_new_aux()

            for i in range(-1, 2, 2):
                self._real_add_clause([variables[0], variables[1], i * a])
        else:
            self._real_add_clause(variables)

            # add x <=> (y {^/v} z)

    def add_biimplication_clause(self, variables, is_conjunction):
        if len(variables) == 0 or len(variables) > 3:
            logging.error(
                "Invalid number of variables in biimplication clause. Expected in range[1, 3], got {} instead".format(
                    len(variables)))
            exit(2)

        if len(variables) == 1:
            self.add_clause(variables)
            return
        elif len(variables) == 2:
            for i in range(-1, 2, 2):
                for j in range(-1, 2, 2):
                    if i != j:
                        self.add_clause([i * variables[0], j * variables[1]])
            return

        c_truth_values = [
            [1, -1, -1],
            [-1, 1, 1],
            [-1, 1, -1],
            [-1, -1, 1]
        ]

        d_truth_values = [
            [1, 1, -1],
            [1, -1, 1],
            [1, -1, -1],
            [-1, 1, 1]
        ]

        if is_conjunction:
            for t in c_truth_values:
                self.add_clause([variables[i] * t[i] for i in range(len(t))])
        else:
            for t in d_truth_values:
                self.add_clause([variables[i] * t[i] for i in range(len(t))])

    def parse_disjoint_clause(self, root, variables):
        if len(variables) == 0:
            return
        if len(variables) == 1:
            self.add_biimplication_clause([root, variables[0]], False)
            return

        for v in variables[:-2]:
            next_root = self.get_new_aux()
            self.add_biimplication_clause([root, next_root, v], False)
            root = next_root

        self.add_biimplication_clause([root, variables[-2], variables[-1]], False)

    def parse_conjunction_clauses(self, root, clauses):
        if len(clauses) == 0:
            return
        if len(clauses) == 1:
            self.parse_disjoint_clause(root, clauses[0])
            return

        for c in clauses[:-1]:
            next_root = self.get_new_aux()
            clause_root = self.get_new_aux()

            self.add_biimplication_clause([root, next_root, clause_root], True)
            self.parse_disjoint_clause(clause_root, c)

            root = next_root

        self.parse_disjoint_clause(root, clauses[-1])

    def get_stats(self):
        num_variables = len(self.variables)
        num_clauses = len(self.clauses)

        return {
            "num_variables": num_variables,
            "num_clauses": num_clauses,
            "clauses": self.clauses
        }

    def write(self, stream=sys.stdout):
        stream.write("p cnf {} {}\n".format(len(self.variables), len(self.clauses)))
        for c in self.clauses:
            stream.write("{} 0\n".format(" ".join([str(x) for x in c])))

    def parse_tree_method(self, clauses):
        root = self.get_new_aux()
        self.add_biimplication_clause([root], False)
        self.parse_conjunction_clauses(root, clauses)

    def linear_method(self, clauses):
        for c in clauses:
            if len(c) <= 3:
                self.add_clause(c)
            else:
                y = self.get_new_aux()
                self.add_clause([c[0], c[1], y])

                for i in range(2, len(c) - 2):
                    next_y = self.get_new_aux()
                    self.add_clause([-y, c[i], next_y])
                    y = next_y

                self.add_clause([-y, c[-2], c[-1]])

    @classmethod
    def convert_to_threesat(clazz, num_variables, clauses, mode):
        s = clazz()

        s.set_counter(num_variables)
        s._variables = set(range(1, num_variables + 1))

        if mode == "pt":
            s.parse_tree_method(clauses)
        elif mode == "lm":
            s.linear_method(clauses)
        else:
            s._clauses = clauses

        return s

    @classmethod
    def from_sat_file(clazz, filename, mode):
        header = {}
        clauses = []
        stream = None

        nr = 0

        def log_error(msg):
            logging.error(msg)
            exit(2)

        try:
            mtype = mimetypes.guess_type(filename)[1]
            if mtype is None:
                stream = open(filename, 'r')
            elif mtype == 'bzip2':
                stream = BZ2File(filename, 'r')
            elif mtype == 'gz' or mtype == 'gzip':
                stream = gzip.open(filename, 'r')
            elif mtype == 'xz' and xz:
                stream = xz.open(filename, 'r')
            else:
                raise IOError('Unknown input type "%s" for file "%s"' % (mtype, filename))
            for line in stream:
                if isinstance(line, bytes):
                    line = line.decode("utf-8")
                if len(line.rstrip()) == 0:
                    continue

                line = line.split()
                nr += 1

                if line[0] == "p":
                    logging.info("Reading header")

                    if len(header.keys()) != 0:
                        log_error("Multiple header in line {}".format(nr))
                    if len(line) != 4:
                        log_error(
                            "Wrong header. expected 4 tokens (p cnf num_variables num_edges). Got {} instead".format(
                                len(line)))

                    if line[1] != "cnf":
                        log_error("Expected cnf identifier. Got {} instead".format(line[1]))

                    try:
                        header["num_variables"] = int(line[2])
                        header["num_clauses"] = int(line[3])
                    except ValueError as e:
                        logging.error(e)
                        log_error("Invalid format for number of variables or clauses. Expected integer")

                elif line[0] == "c" or line[0] == "%" or line[0] == "w":
                    logging.info("#" * 20 + "Reading comment")
                    logging.info(" ".join(line))
                else:
                    if len(header.keys()) == 0:
                        log_error("Reading edge before header in line {}".format(nr))

                    try:
                        if int(line[-1]) == 0:
                            line = line[:-1]
                        line = [int(x) for x in line]
                    except ValueError as e:
                        logging.error(e)
                        log_error("Invalid format for clause. Variables should be in integer")

                    for v in line:
                        if abs(v) < 1 or abs(v) > header["num_variables"]:
                            log_error("Vertex {} out of bounds. Expected abs in range [1, {}]".format(v, header[
                                "num_variables"]))

                    if len(line) > 0:
                        clauses.append(line)
        finally:
            if stream:
                stream.close()

        t_sat = clazz.convert_to_threesat(header["num_variables"], clauses, mode)
        return t_sat
