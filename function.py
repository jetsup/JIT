import os
import hashlib
import pickle
from difflib import unified_diff

"""
This file has all the `git` similar functions from creating a new repository 
to adding files to the repository to committing the changes.
"""


def init():
    # check if the .jit directory already exists
    if os.path.exists(".jit"):
        print("JIT repository already initialized.")
        return
    os.makedirs(".jit", exist_ok=True)
    with open(".jit/index", "wb") as f:
        pickle.dump({}, f)
    with open(".jit/commits", "wb") as f:
        pickle.dump([], f)
    with open(".jit/branches", "wb") as f:
        pickle.dump({"main": 0}, f)
    with open(".jit/HEAD", "w") as f:
        f.write("main")
    print("Initialized empty JIT repository in", os.path.abspath(".jit"))


def has_changes(file: str):
    if not os.path.exists(".jit/index"):
        return True

    with open(file, "rb") as f:
        content = f.read()
        sha256_digest = hashlib.sha256(content).hexdigest()

    with open(".jit/index", "rb") as f:
        index = pickle.load(f)

    return index.get(file) != sha256_digest


def parse_jitignore():
    """
    Parses the .jitignore file and returns a set of patterns to ignore.
    """
    patterns = set()
    if os.path.exists(".jitignore"):
        with open(".jitignore", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore comments and blank lines
                    patterns.add(line)
    return patterns


def should_ignore(file: str, patterns: set):
    """
    Checks if a file should be ignored based on the patterns.
    """
    for pattern in patterns:
        if pattern in file:
            return True
    return False


def add(file: str):
    """
    This function adds the file to the index. If the file is `.`, then it adds all the files in the current directory.
    """
    if file == ".":
        files = [f for f in os.listdir(".") if os.path.isfile(f)]
    else:
        files = [file]

    if not os.path.exists(".jit/index"):
        with open(".jit/index", "wb") as f:
            pickle.dump({}, f)

    patterns = parse_jitignore()

    with open(".jit/index", "rb") as f:
        index = pickle.load(f)

    for file in files:
        if not os.path.exists(file):
            print("File", file, "does not exist")
            continue

        if should_ignore(file, patterns):
            print(f"Ignored {file} (matched .jitignore)")
            continue

        if has_changes(file):
            with open(file, "rb") as f:
                content = f.read()
                index[file] = hashlib.sha256(content).hexdigest()
        else:
            print("No changes to", file)
            return

    with open(".jit/index", "wb") as f:
        pickle.dump(index, f)
    print("Added files to the index.")


def merge(branch_name: str):
    """
    Merges the given branch into the current branch, handling conflicts if they occur.
    """
    with open(".jit/branches", "rb") as f:
        branches = pickle.load(f)

    if branch_name not in branches:
        print(f"Branch '{branch_name}' does not exist.")
        return

    with open(".jit/HEAD", "r") as f:
        current_branch = f.read().strip()

    if branch_name == current_branch:
        print("Cannot merge a branch into itself.")
        return

    # load all commits
    with open(".jit/commits", "rb") as f:
        commits = pickle.load(f)

    current_commit_id = branches[current_branch]
    branch_commit_id = branches[branch_name]

    current_index = commits[current_commit_id]["index"]
    branch_index = commits[branch_commit_id]["index"]

    merged_index = current_index.copy()
    conflict_files = []

    for file, branch_hash in branch_index.items():
        current_hash = current_index.get(file)

        # file exists in both branches but differs
        if current_hash and current_hash != branch_hash:
            conflict_files.append(file)
            with open(file, "r") as f:
                current_content = f.read()
            with open(file, "r") as f:
                branch_content = f.read()

            # Write conflict markers into the file
            with open(file, "w") as f:
                f.write(
                    f"<<<<<<< HEAD\n{current_content}\n=======\n{branch_content}\n>>>>>>> {branch_name}"
                )
            print(f"Conflict in {file}: manual resolution required.")

        # file only exists in the branch being merged
        elif not current_hash:
            merged_index[file] = branch_hash
            with open(file, "rb") as f:
                content = f.read()
            with open(file, "wb") as f:
                f.write(content)
            print(f"Added {file} from branch '{branch_name}'.")

    # Update the current branch's commit history if no conflicts remain
    if not conflict_files:
        new_commit = {
            "message": f"Merge branch '{branch_name}' into '{current_branch}'",
            "index": merged_index,
        }
        commits.append(new_commit)
        branches[current_branch] = len(commits) - 1

        with open(".jit/commits", "wb") as f:
            pickle.dump(commits, f)
        with open(".jit/branches", "wb") as f:
            pickle.dump(branches, f)

        print(f"Branch '{branch_name}' successfully merged into '{current_branch}'.")
    else:
        print(
            "Merge conflicts encountered. Resolve them manually and commit the changes."
        )


def commit(message: str):
    """
    This function commits the changes to the repository.
    """
    if not os.path.exists(".jit/index"):
        print("Index not initialized. Run `jit init` first.")
        return

    with open(".jit/index", "rb") as f:
        index = pickle.load(f)

    if not index:
        print("No changes to commit.")
        return

    commits_path = ".jit/commits"
    if not os.path.exists(commits_path):
        with open(commits_path, "wb") as f:
            pickle.dump([], f)

    with open(commits_path, "rb") as f:
        commits = pickle.load(f)

    commit = {"message": message, "index": index}
    for file in index:
        commit_file_path = f".jit/{file.replace('/', '_')}_{len(commits)}"
        with open(file, "rb") as f:
            with open(commit_file_path, "wb") as commit_file:
                commit_file.write(f.read())

    commits.append(commit)
    with open(commits_path, "wb") as f:
        pickle.dump(commits, f)

    with open(".jit/index", "wb") as f:
        pickle.dump({}, f)

    print("Committed changes:", message)


def diff(commit_id: int):
    commits_path = ".jit/commits"
    if not os.path.exists(commits_path):
        print("No commits found.")
        return

    with open(commits_path, "rb") as f:
        commits = pickle.load(f)

    if commit_id >= len(commits):
        print(f"Commit {commit_id} does not exist.")
        return

    commit = commits[commit_id]
    for file, digest in commit["index"].items():
        commit_file_path = f".jit/{file.replace('/', '_')}_{commit_id}"
        if not os.path.exists(file):
            print(f"File {file} is missing in working directory.")
            continue

        with open(file, "r") as current_file, open(
            commit_file_path, "r"
        ) as committed_file:
            diff = unified_diff(
                committed_file.readlines(), current_file.readlines(), lineterm=""
            )
            print("\n".join(diff))


def log():
    """
    Shows the commit history in reverse chronological order.
    """
    commits_path = ".jit/commits"
    if not os.path.exists(commits_path):
        print("No commits found.")
        return

    with open(commits_path, "rb") as f:
        commits = pickle.load(f)

    for i in range(len(commits) - 1, -1, -1):  # Reverse chronological order
        commit = commits[i]
        print(f"Commit {i}")
        print(f"Message:\t{commit['message']}")
        print("Files:")
        for file, sha256_digest in commit["index"].items():
            print(f"  {file}:\t{sha256_digest}")
        print("-" * 80)


def create_branch(branch_name: str):
    """
    Creates a new branch from the current commit.
    """
    if not os.path.exists(".jit/branches"):
        branches = {"main": 0}  # Default branch
        with open(".jit/branches", "wb") as f:
            pickle.dump(branches, f)

    with open(".jit/branches", "rb") as f:
        branches = pickle.load(f)

    if branch_name in branches:
        print(f"Branch '{branch_name}' already exists.")
        return

    # check if the .jit/HEAD file exists
    if not os.path.exists(".jit/HEAD"):
        print("HEAD not found. Run `jit init` first.")
        return

    # Read the current HEAD
    with open(".jit/HEAD", "r") as f:
        current_branch = f.read().strip()

    branches[branch_name] = branches[current_branch]

    with open(".jit/branches", "wb") as f:
        pickle.dump(branches, f)

    print(f"Branch '{branch_name}' created.")


def checkout(branch_name: str):
    """
    Switches to the given branch.
    """
    with open(".jit/branches", "rb") as f:
        branches = pickle.load(f)

    if branch_name not in branches:
        print(f"Branch '{branch_name}' does not exist.")
        return

    with open(".jit/HEAD", "w") as f:
        f.write(branch_name)

    print(f"Switched to branch '{branch_name}'.")


def clone(repo_path: str, dest_path: str):
    """
    Clones a repository into the destination path.
    """
    if not os.path.exists(repo_path):
        print(f"Repository at {repo_path} does not exist.")
        return

    if os.path.exists(dest_path):
        print(f"Destination path {dest_path} already exists.")
        return

    os.makedirs(dest_path, exist_ok=True)

    # Copy the .jit directory
    os.system(f"cp -r {os.path.join(repo_path, '.jit')} {dest_path}")

    print(f"Cloned repository from {repo_path} to {dest_path}.")
