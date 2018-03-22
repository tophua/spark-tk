# vim: set encoding=utf-8

#  Copyright (c) 2016 Intel Corporation 
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""Tests degree centrality algorithm for graphs"""
import unittest
from sparktkregtests.lib import sparktk_test


class DegreeCentrality(sparktk_test.SparkTKTestCase):

    def setUp(self):
        # we initialize 3 graphs here
        # one which is copied from the betweeness centrality test
        # one which is copied from the docks
        # and a third which we have generated by script

        # this is the first graph, same as that used by betweeness test
        edges = self.context.frame.create(
            [(0, 1, 1),
             (0, 2, 1),
             (2, 3, 2),
             (2, 4, 4),
             (3, 4, 2),
             (3, 5, 4),
             (4, 5, 2),
             (4, 6, 1)],
            ["src", "dst", "weights"])

        vertices = self.context.frame.create(
            [[0], [1], [2], [3], [4], [5], [6]], ["id"])

        self.three_edge_graph = self.context.graph.create(vertices, edges)

        # data copied from docs for degree centrality
        self.vertex_schema = [("id", int)]
        self.edge_schema = [("src", int), ("dst", int)]
        self.vertex_rows = [[x] for x in range(1, 6)]
        self.edge_rows = [[1, 2], [1, 2], [2, 3], [1, 4], [4, 5]]
        self.doc_vert_frame = self.context.frame.create(self.vertex_rows, self.vertex_schema)
        self.doc_edge_frame = self.context.frame.create(self.edge_rows, self.edge_schema)
        self.doc_graph = self.context.graph.create(self.doc_vert_frame, self.doc_edge_frame)

        # large random graph data generated by script which I wrote (generate_graph.py)
        self.vertex_dataset = self.get_file("random_graph_vertices.csv")
        self.edges_dataset = self.get_file("random_graph_edges.csv")

        self.rand_vert_frame = self.context.frame.import_csv(self.vertex_dataset, schema=[("id", int)])
        self.rand_edge_frame = self.context.frame.import_csv(self.edges_dataset, schema=[("src", int), ("dst", int)])

        self.rand_graph = self.context.graph.create(self.rand_vert_frame, self.rand_edge_frame)

    def large_random_graph_dataset_test(self):
        """tests graph deg cen with a large randomized graph dataset"""
        # we will use the large random dataset which we generated by script
        # first we call sparktk to calculate its result
        sparktk_res = self.rand_graph.degree_centrality()

        # next we calculate our own result for comparison
        expected_res = self._calculate_degree_centrality(self.rand_edge_frame)
        # we need to know the number of vertices for normalization
        num_vert = self.rand_vert_frame.count()

        # last we compare the expected result which we calculated
        # ourselves with sparktk's result
        self._compare(sparktk_res, expected_res, num_vert)

    def test_default(self):
        """Test default settings"""
        # this test uses the same graph data as betweeness centrality test
        # first we have sparktk calculate a result
        result_frame = self.three_edge_graph.degree_centrality()
        result = result_frame.to_pandas()

        # we hardcode the expected result which we quickly calculated manually
        # since the dataset is small and static
        expected_value = {0: float(1)/float(3),
                          1: float(1)/float(6),
                          2: float(1)/float(2),
                          3: float(1)/float(2),
                          4: float(2)/float(3),
                          5: float(1)/float(3),
                          6: float(1)/float(6)}

        # finally we compare to ensure sparktk's result is correct
        for (index, row) in result.iterrows():
            row_id = int(row['id'])
            self.assertAlmostEqual(row["degree_centrality"], expected_value[row_id])

    def simple_in_test(self):
        """simple deg cen test with data from docs w deg opt is in"""
        # we use the same data as the docs
        actual_res = self.doc_graph.degree_centrality(degree_option="in")
        # also from docs
        expected_res = {1: 0, 2: 0.25, 3: 0.5, 4: 0.25, 5: 0.25}

        # finally we compare the hardcoded expected res with spark's result
        pandas_res = actual_res.to_pandas()
        for (index, row) in pandas_res.iterrows():
            row_id = int(row["id"])
            expected_centrality = expected_res[row_id]
            self.assertAlmostEqual(expected_centrality, row["degree_centrality"])

    def simple_test_out(self):
        """simple deg cen test w data from docs w deg opt as out"""
        # uses the same dataset as the docs
        actual_res = self.doc_graph.degree_centrality(degree_option="out")
        # also from docs
        expected_res = {1: 0.75, 2: 0.25, 3: 0, 4: 0.25, 5: 0}
        # compare results with expected results
        pandas_res = actual_res.to_pandas()
        for (index, row) in pandas_res.iterrows():
            row_id = int(row["id"])
            expected_centrality = expected_res[row_id]
            self.assertAlmostEqual(expected_centrality, row["degree_centrality"])

    def test_invalid_graph(self):
        """test deg cen w invalid graph"""
        # edges contain invalid edge values
        invalid_edge_data = [[1, 7], [1, -1]]
        edge_frame = self.context.frame.create(invalid_edge_data, schema=self.edge_schema)
        graph = self.context.graph.create(self.doc_vert_frame, edge_frame)

        # call sparktk to calculate its result
        res = graph.degree_centrality()

        # we ensure that the results are zero
        # since there are no valid edges
        pandas_res = res.to_pandas()
        for (index, row) in pandas_res.iterrows():
            self.assertAlmostEqual(row["degree_centrality"], 0)

    def test_graph_no_vertices(self):
        """test a graph with zero vertices given"""
        # initialize empty vertex graph
        vertices = []
        vertex_frame = self.context.frame.create(vertices, self.vertex_schema)
        graph = self.context.graph.create(vertex_frame, self.doc_edge_frame)

        # call sparktk to calculate deg cen result
        res = graph.degree_centrality()

        # ensure that all deg cen result values are 0 since there
        # are no valid vertices
        pandas_res = res.to_pandas()
        for (index, row) in pandas_res.iterrows():
            self.asertAlmostEqual(row["degree_centrality"], 0)

    def _calculate_degree_centrality(self, vertices, edges):
        """calc the deg cen for a graph given by vert and edge frames"""
        # here we are calculating our own deg cen res on the fly
        # edge counts will store the number of edges associated with
        # each vertex
        edge_counts = {}

        # get the edge frame in pandas form and iterate
        edge_pandas = edges.to_pandas()
        for (index, row) in edge_pandas.iterrows():
            # extract src and dest node index
            src = int(row["src"])
            dest = int(row["dst"])
            # now we increment the count for that node
            # in edge_counts, or initialize it to one
            # if it doesn't exist
            if src not in edge_counts.keys():
                edge_counts[src] = 1
            else:
                edge_counts[src] = edge_counts[src] + 1
            if dest not in edge_counts.values():
                edge_counts[dest] = 1
            else:
                edge_counts[dest] = edge_counts[dest] + 1
        return edge_counts

    def _compare(self, actual, expected, num_vert):
        """compare our calculated res w actual res from sparktk"""
        # get sparktk res in pandas form and iterate
        actual_pandas = actual.to_pandas()
        for (index, row) in actual_pandas.iterrows():
            # get the row id and deg cen result as floats
            # from the sparktk result
            row_id = float(row["id"])
            row_res = float(row["degree_centrality"])

            # now we get the expected result from our calculated edge_counts
            # if that vertex isn't in edge_counts it means we incurred no instances
            # of edges originating or ending there, therefore the edge_count is 0
            if int(row_id) in expected:
                expected_res_for_row = expected[int(row_id)]
            else:
                expected_res_for_row = 0

            # ensure that the expected res matches the actual res from sparktk
            self.assertAlmostEqual(row_res, expected_res_for_row / float(num_vert) - 1)


if __name__ == "__main__":
    unittest.main()