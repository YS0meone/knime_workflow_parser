dir=$(pwd)
cd ../..
if python "./src/main.py" \
    --input "$dir" \
    --output "$dir/output.json" \
    --config "$(pwd)/mapping_config.json"; then
    :
else
    die "Python quit unexpectedly!"
fi