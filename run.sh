root=$(pwd)
config="$root/mapping_config.yaml"
workflow="Finding Association Rules for Market Basket Analysis"

input="$root/examples/${workflow}"
output="$root/output/converted_${workflow}.json"
    
if python "$root/src/main.py" --input "$input" --output "$output" --config "$config"; then
    echo "${workflow} completed successfully."
else
    echo "${workflow} quit unexpectedly!"
    exit 1
fi

echo "All workflows completed successfully."