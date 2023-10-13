import uuid



# generate the dict template for operators
class OperatorGenerator():

    def __init__(self, operator_type, input_dict):
        self.mapping_table = {
                "CSV Reader": "CSVFileScan",
                "Row Aggregator": "Aggregate"
                }
        self.type = self.mapping_table[operator_type]
        self.input = input_dict
        # self.format_parameter()
        self.temp = {
                "operatorID": self.generate_id(self.type),
                "operatorType": self.type,
                "operatorVersion": "",
                "operatorProperties": {
                    "dumProp": []
                },
                "inputPorts": [],
                "outputPorts": [],
                "showAdvanced": False,
                "isDisabled": False,
                "customDisplayName": self.type,
                "dynamicInputPorts": False,
                "dynamicOutputPorts": False
            }
        
        # convert the template to meet the operator type
        self.convert()

    # def format_parameter(self):
    #     params = self.input["operator"]["parameters"]
        

    def convert(self):
        method_mapping = {
            "Projection": self.convert_select_attribute,
            "CSVFileScan": self.convert_read_csv,
            "Aggregate": self.convert_aggregate
        }
        # if we can convert the operator type, we call the method
        if self.type in method_mapping:
            method_mapping[self.type]()


    def convert_select_attribute(self):
        self.temp["operatorVersion"] = "241993a4c41e2a402a0f06e5f6e91202ea3184ce"
        self.temp["operatorProperties"]["attributes"] = []
        attributes = self.temp["operatorProperties"]["attributes"]
        port = {
                    "portID": "",
                    "displayName": "",
                    "allowMultiInputs": False,
                    "isDynamicPort": False
                }
        params = self.input["parameter"]
        for param in params:
            if param["@key"] == "select_subset":
                attrs = param["@value"].split(",")
                for attr in attrs:
                    attributes.append({"alias": "", "originalAttribute": attr})
        input_port = port.copy()
        input_port["portID"] = "input-0"
        output_port = port.copy()
        output_port["portID"] = "output-0"
        self.temp["inputPorts"].append(input_port)
        self.temp["outputPorts"].append(output_port)        
        
    def convert_read_csv(self):
        port = {
                    "portID": "",
                    "displayName": "",
                    "allowMultiInputs": False,
                    "isDynamicPort": False
                }
        self.temp["operatorVersion"] = "c14deb143ea86b24f718654c929cfd618cbd4503"
        properties = self.temp["operatorProperties"]
        properties["fileEncoding"] = "UTF_8"
        properties["customDelimiter"] = ","
        params = self.input["parameter"]
        for param in params:
            if param["@key"] == "first_row_as_names":
                properties["hasHeader"] = True if param["@value"] == "true" else False
        properties["fileName"] = ""
        properties["limit"] = None
        properties["offset"] = None
        output_port = port.copy()
        output_port["portID"] = "output-0"
        self.temp["outputPorts"].append(output_port)
    
    def convert_aggregate(self):
        func_map = {"count": "count"}
        port = {
                    "portID": "",
                    "displayName": "",
                    "allowMultiInputs": False,
                    "isDynamicPort": False
                }
        self.temp["operatorVersion"] = "73d2ca7026c93ca7898b3e9c0ce148b99bbf2726"
        properties = self.temp["operatorProperties"]
        properties["aggregations"] = []
        properties["groupByKeys"] = []
        agg_func = func_map[self.input["list"]["parameter"]["@value"]]
        agg_attr = self.input["list"]["parameter"]["@key"]
        params = self.input["parameter"]
        key = ""
        for param in params:
            if param["@key"] == "group_by_attributes":
                key = param["@value"]
        agg_dict = {
            "result attribute": agg_func,
            "aggFunction": agg_func,
            "attribute": agg_attr
        }

        properties["aggregations"].append(agg_dict)
        properties["groupByKeys"].append(key)


        input_port = port.copy()
        input_port["portID"] = "input-0"
        output_port = port.copy()
        output_port["portID"] = "output-0"

    
    def get_temp(self):
        return self.temp
    
    def generate_id(self, operator_type):
        return operator_type + "-" + "operator" + "-" + str(uuid.uuid4())
    
    def get_id(self):
        return self.temp["operatorID"]
    
    def generate_pos(self):
        return {"x": float(self.input["@x"]), "y": float(self.input["@y"])}
    