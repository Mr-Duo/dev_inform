#!/bin/bash

# Check if the JSON file path is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_json_file>"
    exit 1
fi

# Extract the commit hashes from the JSON file
json_file=$1
commit_hashes=$(jq -r '.[]' "$json_file")

# Check if jq extraction succeeded
if [ -z "$commit_hashes" ]; then
    echo "Error: No commit hashes found in the JSON file."
    exit 1
fi

cd ../linux
# Loop through each commit hash and fetch it
for commit_hash in $commit_hashes; do
    echo "Fetching commit $commit_hash..."
    git fetch origin $commit_hash:refs/remotes/origin/orphaned-commit

    # Check if the fetch was successful
    if [ $? -eq 0 ]; then
        echo "Successfully fetched $commit_hash into refs/remotes/origin/orphaned-commit"
    else
        echo "Failed to fetch $commit_hash."
    fi
done
