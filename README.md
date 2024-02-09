# Workflow Parser
## About the project
The project parses workflow metadata from other ML platforms into a read-only Texera workflow. Currently the code can only handle the Knime workflow metadata. The parser is capable of perserving the topological structure of the workflow and converting each operator's property between two platforms if such mapping relationship exists.

The parser stores all of the mapping information in the `mapping_config.yaml`. So far only two operators in Knime are specified: CSV Reader and Row Aggregator. All other operators would be converted to a dummy operator. As a placeholder in the workflow. By modifying the `mapping_config.yaml`, we can add more mapping relationship between the operators.

![Before Parsing](https://drive.google.com/uc?export=view&id=1LPGWyVk0HHzF9yG-acMJyXJtPyxtbu5N "Before Parsing")

![After Parsing](https://drive.google.com/uc?export=view&id=1LYn-x7qhNj8nblvipJN2CJKepyNWFjbU "After Parsing")

## Setting Up Your Virtual Project Environment
1. Navigate to the project root directory
2. Create a virtual environment

```bash
python3 -m venv parserenv
```
3. Activate the virtual environment
* On macOS and Linux:
```bash
source parserenv/bin/activate
```
* On Windows:
```bash
.\parserenv\Scripts\activate
```
4. Install the required packages: `pip install -r requirements.txt`
To deactivate the virtual environment, type `deactivate`

## Steps to Run the Example
1. Navigate to the project root directory
2. Run the following command 
```bash
cd examples/basic_csv_read/ && ./run.sh
```
The result would be a json file called `workflow.json`. You can find it in the basic_csv_read folder. To view it, simply import the json file in Texera.

## Steps to Convert New Workflows
1. Store the Knime workflow folder inside the ./example/ directory (You can find the workflow folder in your Knime workspace directory)
2. Create a shell script in the workflow folder with the following content:
```bash
dir=$(pwd)
cd ../..
if python "./src/main.py" \
    --input "$dir" \
    --output "$dir/output.json" \
    --config "$(pwd)/mapping_config.yaml"; then
    :
else
    echo "Python quit unexpectedly!"
fi
```
3. Run the shell script from the workflow folder `./run.sh`

Again the `workflow.json` file would be generated in the workflow folder.

## Steps to Run Unit Tests
1. Navigate to the test foler
2. Run `python test_noderetriever.py`

## Steps to Add more Operator Mappings
The mapping relationship is stored in the `mapping_config.yaml` file. The following is an example of a mapping entity. Each entity starts with the name of the Knime's operator and has two foundamental parts: `operator_specs` and `property_mapping`.

`operator_specs`: Specifies the basic operator specifications of Texera operator. One can get the information from the Texera workflow json file.

`property_mapping`: Specifies the mapping relationship between the operator properties. Each mapping entity start with the name of a Texera operator's property and contains two part: `nodes` and `action`.
* `nodes`: Stores the node name and path information to retrieve the node value from a property tree. There can be multiple node name and path pairs since the mapping might not be one to one. The path is the path beginning from the root node to the target node. If the node name is unique in the Knime's property tree, a syntax sugar can be used. e.g. `/.../charset` `charset` is a unique Knime property name. You can ignore the internal nodes by using `...` to replace them. A BFS would be performed to search for the node in the tree. 

* `action`: A user defined Python function to manipulate the retrieved node values and convert it into the desired proprty value. To use the node value retrieved, simply add `$` before the node name in the function.  

```bash
CSV Reader:
  operator_specs:
    operatorType: CSVFileScan
    inputPorts: []
    outputPorts:
    - portID: output-0
      displayName: ''
      allowMultiInputs: false
      isDynamicPort: false
    showAdvanced: false
    isDisabled: false
    dynamicInputPorts: false
    dynamicOutputPorts: false
  property_mapping:
    fileEncoding:
      nodes:
        encoding: /.../charset
      action: |
        if $encoding in ["UTF-8", "UTF-16", "US-ASCII"]:
            ret = $encoding.replace("-","_")
        else:
            ret = "UTF_8"
    customDelimiter:
      nodes:
        delimiter: /.../column_delimiter
      action: ret = $delimiter
    hasHeader:
      nodes:
        has_header: /.../has_column_header
      action: |
        ret = True if $has_header == "true" else False
    fileName:
      nodes:
        file_name: /model/settings/file_selection/path/path
      action: ret = $file_name
    limit:
      nodes:
        limit_enabled: /.../limit_data_rows
        max_rows: /.../max_rows
      action: |
        if $limit_enabled == "true":
            ret = int($max_rows)
        else:
            ret = None
    offset:
      nodes:
        offset_enabled: /.../skip_data_rows
        num_rows: /.../number_of_rows_to_skip
      action: |
        if $offset_enabled == "true":
            ret = int($num_rows)
        else:
            ret = None
```
