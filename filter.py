import json

with open("output.json", "r") as f:
    all = json.load(f)
    

unique_data = {d["VFC"]: d for d in all}.values()
all = list(unique_data)

yes, no = [], []
for line in all:
    if len(line["VIC"]) == 0:
        no.append(line)
    else:
        yes.append(line)
        
with open("no.jsonl", "w") as f:
    for line in no:
        f.write(json.dumps(line) + "\n")

with open("yes.jsonl", "w") as f:
    for line in yes:
        f.write(json.dumps(line) + "\n")

