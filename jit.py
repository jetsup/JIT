import sys
from function import init, add, commit, log, checkout, diff


if __name__ == "__main__":
    str_usage = "Usage: python jit.py <command>\n\n\
Commands:\n\
init:\t\tInitialize a new JIT repository\n\
add:\t\tAdd file contents to the index\n\
commit:\t\tRecord changes to the repository\n\
"
    if len(sys.argv) < 2:
        print(str_usage)

        sys.exit(0)

    # read the first argument
    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "add":
        # check if the filename is provided
        if len(sys.argv) < 3:
            print("Please provide a file name")
            sys.exit(0)
        add(sys.argv[2])
    elif command == "commit":
        # check if the commit message is provided
        if len(sys.argv) < 3:
            print("Please provide a commit message")
            sys.exit(0)
        commit(sys.argv[2])
    elif command == "log":
        log()
    elif command == "checkout":
        # check if the commit_id is provided
        if len(sys.argv) < 3:
            print("Please provide a commit id")
            sys.exit(0)
        checkout(int(sys.argv[2]))
    elif command == "diff":
        # check what to a commit_id is provided
        if len(sys.argv) < 3:
            print("Please provide a commit id")
            sys.exit(0)
        diff(int(sys.argv[2]))
    else:
        print("Unknown command")
        sys.exit(0)
