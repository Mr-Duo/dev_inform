import json
import re
import os
from git import Repo, GitCommandError

# Regex to extract "Fixes: {commit_id}" pattern
FIXES_REGEX = re.compile(r"(Fixes:) ([0-9a-z]{7,40})",flags=re.IGNORECASE)
UPSTREAM_REGEX = re.compile(r"commit\s*([0-9a-z]{7,40})\s*upstream",flags=re.IGNORECASE)
UPSTREAM_REGEX2 = re.compile(r"Upstream\s+commit\s+([a-z0-9]{7,40})",flags=re.IGNORECASE)
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
        return partial_commit_id, None

def extract_fixes_ids(message):
    """Extracts all commit IDs from the 'Fixes:' pattern in the message."""
    match = FIXES_REGEX.findall(message if message else "")
    if match:
        return [id for _, id in match] 
    else:
        return None

def check_upstream(message):
    """Extracts all commit IDs from the 'Fixes:' pattern in the message."""
    match1 = UPSTREAM_REGEX.search(message if message else "")
    match2 = UPSTREAM_REGEX2.search(message if message else "")

    if match1:
        return match1.group(1)
    if match2:
        return match2.group(1)
    return None

def main(input_json, output_json):
    # Load partial commit IDs from the input JSON file
    commit_ids = load_commit_ids(input_json)

    if not commit_ids:
        print("No commit IDs found in the input JSON file.")
        return

    results = []  # List to store output data
    side = []
    fetch = []
    # Process each commit ID
    for partial_commit_id in commit_ids:
        print(partial_commit_id)
        result = get_full_commit_info(partial_commit_id)
        if result:
            full_commit_id, commit_message = result
            if commit_message is None:
                fetch.append(full_commit_id)   
                continue 
            fixes_ids = extract_fixes_ids(commit_message)
            if fixes_ids:
                fixes = []
                for fix in fixes_ids:
                    if len(fix) == 40:
                        fixes.append(fix)
                        continue
                    else:
                        try:
                            fix, commit_message = get_full_commit_info(fix)
                            fixes.append(fix)
                        except Exception as e:
                            pass
                fixes_ids = fixes
                
            upstream_id = check_upstream(commit_message)
            print(upstream_id)
            if upstream_id:
                full_commit_id = None
                full_commit_id, commit_message = get_full_commit_info(upstream_id)
            results.append({"VFC": full_commit_id if full_commit_id else partial_commit_id, "VIC": fixes_ids if fixes_ids else [""]})
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
        with open("fetch.json", 'w') as f:
            json.dump(fetch, f, indent=4)
        print(f"Results saved to {output_json}")
    except Exception as e:
        print(f"Error writing to output JSON: {e}")

# Example usage
  # Replace with your local repo path
input_json = "linux_dump.json"  # Input JSON file containing partial commit IDs
output_json = "output.json"  # Output JSON file to save the results

main(input_json, output_json)
