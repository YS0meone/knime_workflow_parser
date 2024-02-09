# Workflow Parser
## About the project
The project parses workflow metadata from other ML platform into a read-only Texera workflow. Currently the code can only handle the Knime workflow metadata. The parser is capable of perserving the topological structure of the workflow and converting each operator's property between two platforms if such mapping relationship exists.

![Before Parsing](https://drive.google.com/uc?export=view&id=1LPGWyVk0HHzF9yG-acMJyXJtPyxtbu5N)

![After Parsing](https://drive.google.com/uc?export=view&id=1LYn-x7qhNj8nblvipJN2CJKepyNWFjbU)

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


