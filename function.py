import os
import hashlib
import pickle

"""
This file has all the `git` similar functions from creating a new repository 
to adding files to the repository to committing the changes.
"""


def init():
    os.makedirs(".jit", exist_ok=True)
    print("Initialized empty JIT repository in", os.path.abspath(".jit"))


# a function to check if there are any changes to a file
def has_changes(file: str):
    """
    This function checks if the file has any changes.
    """
    with open(file, "rb") as f:
        content = f.read()
        sha256_digest = hashlib.sha256(content).hexdigest()

    with open(".jit/index", "rb") as f:
        index = pickle.load(f)

    if file not in index:
        return True

    return index[file] != sha256_digest


# print changes that were made to a commit
def diff(commit_id: int):
    """
    This function shows the changes made to a commit.
    """
    with open(".jit/commits", "rb") as f:
        commits = pickle.load(f)

    if commit_id >= len(commits):
        print("Commit", commit_id, "does not exist")
        return

    commit = commits[commit_id]
    for file, sha256_digest in commit["index"].items():
        with open(file, "rb") as f:
            content = f.read()
        with open(file, "rb") as f:
            old_content = f.read()

        if content != old_content:
            print("Changes made to", file)
            print("Old content:", old_content)
            print("New content:", content)
        else:
            print("No changes made to", file)

def add(file: str):
    """
    This function adds the file to the index. If the file is `.`, then it adds all the files in the current directory.
    """
    if file == ".":
        files = [f for f in os.listdir(".") if os.path.isfile(f)]
    else:
        files = [file]

    # check if the file exists
    for file in files:
        if not os.path.exists(file):
            print("File", file, "does not exist")
            return

    # check if there are any changes made to the file or if the file is new
    with open(".jit/index", "rb") as f:
        index = pickle.load(f)

    for file in files:
        if has_changes(file):
            with open(file, "rb") as f:
                content = f.read()
                sha256_digest = hashlib.sha256(content).hexdigest()
            index[file] = sha256_digest
        else:
            print("No changes made to", file)
            return

    with open(".jit/index", "wb") as f:
        pickle.dump(index, f)

    print("Added files to the index")


def commit(message: str):
    """
    This function commits the changes to the repository.
    """
    with open(".jit/index", "rb") as f:
        index = pickle.load(f)

    # check if there are any changes to commit
    if not index:
        print("No changes to commit")
        return

    # check if the file exists
    if not os.path.exists(".jit/commits"):
        with open(".jit/commits", "wb") as f:
            pickle.dump([], f)

    with open(".jit/commits", "rb") as f:
        commits = pickle.load(f)

    commit = {"message": message, "index": index}
    commits.append(commit)

    with open(".jit/commits", "wb") as f:
        pickle.dump(commits, f)

    with open(".jit/index", "wb") as f:
        pickle.dump({}, f)

    print("Committed changes to the repository")


def log():
    """
    This function shows the commit history.
    """
    with open(".jit/commits", "rb") as f:
        commits = pickle.load(f)

    for i, commit in enumerate(commits):
        print("Commit", i + 1)
        print("Message:", commit["message"])
        print("Files:")
        for file, sha256_digest in commit["index"].items():
            print(file, sha256_digest)
        print()


def checkout(commit_id: int):
    """
    This function checks out the commit with the given commit_id.
    """
    with open(".jit/commits", "rb") as f:
        commits = pickle.load(f)

    if commit_id >= len(commits):
        print("Commit", commit_id, "does not exist")
        return

    commit = commits[commit_id]
    for file, sha256_digest in commit["index"].items():
        with open(file, "rb") as f:
            content = f.read()
        with open(file, "wb") as f:
            f.write(content)

    print("Checked out commit", commit_id)
