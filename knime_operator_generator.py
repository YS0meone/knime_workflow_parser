import uuid
import json
from pprint import pprint


TEMPLATE_PATH = "template.json"


class OperatorGenerator():
    """
        OperatorGenerator takes in knime operator type and the dict representation of the operator to create an operator section in the texera workflow. Itrequres a .json file which specify the mapping between the knime operator type and the texera operator template
    """

    def __init__(self, operator_type, input_dict):
        # loads the .json as dictionary
        template_json = open(TEMPLATE_PATH, "r")
        self.template_table = json.load(template_json)
        template_json.close()
        self.type = operator_type
        self.input = input_dict
        # set up the basic template for this particular knime operator type
        self.convert()

    def convert(self):
        # maps knime operator type to each attribute mapping function to support attribute mapping
        attr_mapping = {
            "CSV Reader": self.convert_read_csv,
            "Row Aggregator": self.convert_aggregate
        }
        # generate the basic template if we cannot find the mapping we use the template of dummy op
        if self.type in self.template_table:
            self.temp = self.template_table[self.type]
        else:
            self.temp = self.template_table["Dummy"]
        # generate the operatorID for the operator
        self.temp["operatorID"] = self.generate_id(self.temp["operatorType"])
        # maps the attribute
        if self.type in attr_mapping:
            attr_mapping[self.type]()
        else:
            self.convert_to_dummy()

    def convert_to_dummy(self):
        """
            store the source information of the operator attribute in the dummy property. NOT FINISHED YET
        """
        self.temp["operatorProperties"]["dumProp"].append(
            {"dummyAttribute": "source", "dummyValue": "placeholder"})
        self.temp["customDisplayName"] = self.type

    def convert_read_csv(self):
        """
            TODO: maps the attribute using the setting.xml 
        """
        pass

    def convert_aggregate(self):
        """
            TODO: maps the attribute using the setting.xml 
        """
        pass

    def get_temp(self):
        return self.temp

    def generate_id(self, operator_type):
        return operator_type + "-" + "operator" + "-" + str(uuid.uuid4())

    def get_id(self):
        return self.temp["operatorID"]

    def generate_pos(self):
        """get the position of the knime's operator. NOTICE: MIGHT BE BOUNDARY ISSUE. SHOULD TEST FOR BOUNDARY IF NEEDED"""
        return {"x": float(self.input["ui_settings"]["extrainfo.node.bounds"]["0"]), "y": float(self.input["ui_settings"]["extrainfo.node.bounds"]["1"])}
