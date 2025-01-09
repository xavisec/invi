import os

# Define the project structure as a dictionary
project_structure = {
    "fraud-detection-osint-tool": [
        "config",
        "data/raw",
        "data/processed",
        "data/examples",
        "src/scraping",
        "src/analysis",
        "src/utils",
        "tests",
        "docs",
        "examples"
    ]
}

# Create directories
for root, subdirs in project_structure.items():
    for subdir in subdirs:
        dir_path = os.path.join(root, subdir)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

# Create essential files
essential_files = [
    "fraud-detection-osint-tool/README.md",
    "fraud-detection-osint-tool/LICENSE",
    "fraud-detection-osint-tool/requirements.txt",
    "fraud-detection-osint-tool/.gitignore",
    "fraud-detection-osint-tool/config/config.yaml"
]

for file in essential_files:
    with open(file, 'w') as f:
        f.write("")  # Create an empty file
        print(f"Created file: {file}")
