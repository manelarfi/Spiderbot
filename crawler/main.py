import os

# each website is stored in a separate project folder
def create_project_dir(directory):
    if not os.path.exists(directory):
        print(f"Creating project directory: {directory}")
        os.makedirs(directory)
    else:
        print(f"Project directory already exists: {directory}")

create_project_dir("websites")