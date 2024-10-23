import json

with open("all_commit.json", "r") as f:
    all_commit = json.load(f)
    
with open("linux_dump.json", "r") as f:
    complete = json.load(f)
    
out = []
for x in all_commit:
    if x not in complete:
        out.append(x)
        
print(len(out))
with open("all_filtered.json", "w") as f:
    json.dump(out, f, indent=4)