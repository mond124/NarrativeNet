import os

def list_files_and_folders(current_directory, indent=""):
    # Iterate over all items in the current directory using os.walk
    for root, dirs, files in os.walk(current_directory):
        # Calculate the relative path from the current_directory
        relative_path = os.path.relpath(root, current_directory)
        if relative_path == '.':
            relative_path = ''
        
        # Print the current directory
        print(f"{indent}{os.path.basename(root)}/")

        # Print all directories
        for directory in dirs:
            print(f"{indent}  {directory}/")

        # Print all files
        for file in files:
            print(f"{indent}  {file}")

        # Increase indentation for the next level
        indent += "  "

if __name__ == "__main__":
    current_directory = os.getcwd()
    print(f"Directory structure for: {current_directory}\n")
    list_files_and_folders(current_directory)

