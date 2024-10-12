import json
import re
import os
from git import Repo, GitCommandError

# Regex to extract "Fixes: {commit_id}" pattern
FIXES_REGEX = re.compile(r"Fixes: ([0-9a-z]{7,40})")
UPSTREAM_REGEX = re.compile(r"commit ([0-9a-z]{7,40}) upstream\.")
repo_path = "../linux"
repo = Repo(repo_path)

def load_commit_ids(json_file):
    """Load the list of commit IDs from a JSON file."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading JSON file: {e}")
        exit()

def get_full_commit_info(partial_commit_id):
    """
    Extract the full commit ID and message from a local repository 
    using a partial commit ID (at least 9 characters).
    """
    try:
        commit = repo.commit(partial_commit_id)
        return commit.hexsha, commit.message
    except Exception as e:
        try:
            for remote in repo.remotes:
                remote.fetch(f'origin {commit_hash}:refs/remotes/origin/orphaned-commit')
            commit = repo.commit(partial_commit_id)
            return commit.hexsha, commit.message
        except Exception as e:
            return None

def extract_fixes_ids(message):
    """Extracts all commit IDs from the 'Fixes:' pattern in the message."""
    match = FIXES_REGEX.search(message)
    if match:
        return match.group(1)
    else:
        return None

def check_upstream(message):
    """Extracts all commit IDs from the 'Fixes:' pattern in the message."""
    match = UPSTREAM_REGEX.search(message)
    if match:
        return match.group(1)
    else:
        return None

def main(input_json, output_json):
    # Load partial commit IDs from the input JSON file
    commit_ids = load_commit_ids(input_json)

    if not commit_ids:
        print("No commit IDs found in the input JSON file.")
        return

    results = []  # List to store output data
    side = []

    # Process each commit ID
    for partial_commit_id in commit_ids:
        print(partial_commit_id)
        result = get_full_commit_info(partial_commit_id)
        if result:
            full_commit_id, commit_message = result
            fixes_ids = extract_fixes_ids(commit_message)
            if fixes_ids:
                if len(fixes_ids) == 40:
                    continue
                else:
                    try:
                        fixes_ids, commit_message = get_full_commit_info(fixes_ids)
                    except Exception as e:
                        pass
                
            upstream_id = check_upstream(commit_message)
            if upstream_id:
                full_commit_id, commit_message = get_full_commit_info(upstream_id)
            results.append({"VFC": full_commit_id if full_commit_id else partial_commit_id, "VIC": [fixes_ids] if fixes_ids else [""]})
            print(f"upstream {full_commit_id} fixes {fixes_ids}")
        else:
            print("not found")
            side.append(partial_commit_id)

    # Write results to the output JSON file
    try:
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=4)
        with open("side.json", 'w') as f:
            json.dump(side, f, indent=4)
        print(f"Results saved to {output_json}")
    except Exception as e:
        print(f"Error writing to output JSON: {e}")

# Example usage
  # Replace with your local repo path
input_json = "linux_dump.json"  # Input JSON file containing partial commit IDs
output_json = "output.json"  # Output JSON file to save the results

main(input_json, output_json)
