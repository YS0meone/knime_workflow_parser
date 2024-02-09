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