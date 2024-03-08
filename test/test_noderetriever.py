import unittest
import os
import sys
import xmltodict
import yaml
from pprint import pprint
from utils import format_dict

file_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(file_dir, '..', 'src')))

from node_retriever import NodeRetriever

class TestNodeRetriever(unittest.TestCase):

    def setUp(self):
        xml_file = open("sample_tree.xml", "r")
        self.xml_dict = xmltodict.parse(xml_file.read(), dict_constructor=dict)
        self.property_tree = {}
        format_dict(self.xml_dict, self.property_tree)
        self.property_tree = self.property_tree["settings.xml"]
        xml_file.close()
        self.NR = NodeRetriever(self.property_tree)
        mapping_yaml = open("../mapping_config.yaml", "r")
        self.mapping_config = yaml.safe_load(mapping_yaml)
        mapping_yaml.close()

    def test_syntax_sugar(self):
        # Test to see if the syntax sugar /.../ is working
        path1 = self.NR.str2path("/.../isCaseSensitive")
        path2 = self.NR.str2path("/model/frequencyColumns/patternFilter/isCaseSensitive")
        result1 = self.NR.find_node(path1)
        result2 = self.NR.find_node(path2)
        self.assertEqual(result1, result2)
        self.assertEqual(result1, "false")
        
    def test_find_node_1(self):
        path = "/.../isInverted"
        path = self.NR.str2path(path)
        result  = self.NR.find_node(path)
        self.assertEqual(result, "false")
    
    def test_find_node_2(self):
        path = "/model/frequencyColumns/selected_Internals/0"
        path = self.NR.str2path(path)
        result  = self.NR.find_node(path)
        self.assertEqual(result, "favorite_count")

    def test_find_node_3(self):
        path = "/foo/blah"
        path = self.NR.str2path(path)
        result  = self.NR.find_node(path)
        self.assertIsNone(result)
    
    def test_find_node_4(self):
        path = "/model/frequencyColumns/manualFilter/0"
        path = self.NR.str2path(path)
        result  = self.NR.find_node(path)
        self.assertEqual(result, "favorite_count")
    
    def test_retrieve_nodes_1(self):
        aggregations_setting = self.mapping_config["Row Aggregator"]["property_mapping"]["aggregations"]
        nodes = aggregations_setting["nodes"]
        action = aggregations_setting["action"]
        result = self.NR.retrieve_nodes(nodes, action)
        self.assertIsInstance(result, list)
        ans = {"aggFunction": "count", "result attribute": "COUNT", "attribute": "favorite_count"}
        self.assertDictEqual(result[0], ans)
    
    def test_retrieve_nodes_2(self):
        groupby_setting = self.mapping_config["Row Aggregator"]["property_mapping"]["groupByKeys"]
        nodes = groupby_setting["nodes"]
        action = groupby_setting["action"]
        result = self.NR.retrieve_nodes(nodes, action)
        self.assertIsInstance(result, list)
        ans = ["geo_tag.cityID"]
        self.assertListEqual(result, ans)

        
if __name__ == "__main__":
    unittest.main()