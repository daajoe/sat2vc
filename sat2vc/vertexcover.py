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
import networkx as nx
import sys


class VertexCover(nx.Graph):
    def __init__(self, data=None):
        super(VertexCover, self).__init__(data=data)
        self._cover_size = None

    @property
    def cover_size(self):
        return self._cover_size

    def set_cover_size(self, cover_size):
        self._cover_size = cover_size

    def write(self, stream=sys.stdout):
        stream.write("c vc size = {}\n".format(self.cover_size))
        stream.write("p vc {} {}\n".format(self.number_of_nodes(), self.number_of_edges()))
        for u, v in self.edges():
            stream.write("{} {}\n".format(u, v))

    @classmethod
    def from_three_sat(clazz, t_sat):
        vc = clazz()
        vc.set_cover_size(len(t_sat.variables) + 2 * len(t_sat.clauses))

        vertex_nums = len(t_sat.variables) + 1
        end_vertex_nums = vertex_nums + 3 * len(t_sat.clauses)

        def mapping(x):
            if x < 0:
                return -x + end_vertex_nums - 1
            return x

        for v in t_sat.variables:
            vc.add_edge(v, mapping(-v))

        for c in t_sat.clauses:
            vc.add_edge(vertex_nums, vertex_nums + 1)
            vc.add_edge(vertex_nums + 1, vertex_nums + 2)
            vc.add_edge(vertex_nums + 2, vertex_nums)

            for i in range(len(c)):
                vc.add_edge(vertex_nums + i, mapping(c[i]))

            vertex_nums += 3

        assert (vertex_nums == end_vertex_nums)

        return vc
