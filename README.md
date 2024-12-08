# JIT

## Description

JIT, `not related to _(Just In Time)_`, is a project that aims to provide a learning environment for how GIT works. It is a simple project that allows you to create repositories, add files, and commit changes.

## Usage

This project uses GIT similar commands to create repositories, add files, and commit changes. The commands are:

-   `init`: Create a new repository
-   `add`: Add a file to the repository
-   `commit`: Commit changes to the repository
-   `log`: Show the commit history
-   `checkout`: Change the current commit
-   `diff`: Show the differences between commits
-   `branch`: Create a new branch
-   `merge`: Merge branches

## Installation

To install the project, you need to clone the repository and install the dependencies. The commands are:

```bash
git clone https://github.com/jetsup/JIT.git
```

```bash
cd JIT
```

## Running

To run the project, you need to execute the following command:

```bash
python jit.py <command> <args>
```

i.e.:

```bash
python jit.py init # Create a new `repository`
```

```bash
python jit.py add README.md # Add a file to the `repository`
```

```bash
python jit.py commit "Initial commit" # Commit changes to the `repository`
```
