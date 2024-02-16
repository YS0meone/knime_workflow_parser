root=$(pwd)
config="$root/mapping_config.yaml"
workflows=("workflow_1" "workflow_2" "workflow_3")

for workflow in "${workflows[@]}"; do
    input="$root/examples/${workflow}"
    output="$root/output/converted_${workflow}.json"
    
    if python "$root/src/main.py" --input "$input" --output "$output" --config "$config"; then
        echo "${workflow} completed successfully."
    else
        echo "${workflow} quit unexpectedly!"
        exit 1
    fi
done

echo "All workflows completed successfully."