import re

with open("backend/app/schemas/case.py", "r") as f:
    lines = f.readlines()

out = []
in_schema = False
for line in lines:
    if line.startswith("class AnamnesisSchema") or line.startswith("class PhysicalExam") or line.startswith("class Lab") or line.startswith("class Morph"):
        in_schema = True
    elif line.startswith("class CaseCreate"):
        in_schema = False

    if in_schema and "Optional[str] = None" in line:
        line = line.replace("Optional[str] = None", "Optional[str] = Field(default=None, max_length=5000)")
    
    if "title: str\n" in line and not in_schema:
        line = line.replace("title: str\n", "title: str = Field(..., max_length=200)\n")
    if "title: Optional[str] = None" in line:
        line = line.replace("title: Optional[str] = None", "title: Optional[str] = Field(default=None, max_length=200)")
    if "notes: Optional[str] = None" in line:
        line = line.replace("notes: Optional[str] = None", "notes: Optional[str] = Field(default=None, max_length=10000)")
    
    out.append(line)

with open("backend/app/schemas/case.py", "w") as f:
    f.writelines(out)

