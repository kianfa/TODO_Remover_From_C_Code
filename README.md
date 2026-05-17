# TODO(KF) Comment Remover

A simple PyQt6 desktop tool for removing only C/C++ comments that contain `TODO(KF)` from selected source files.

This tool is intended for Keil C projects, but it can also work with normal `.c` and `.h` files.

## What It Does

The application lets you select one or more files and edits them directly.

It removes comments that contain:

```text
TODO
```

It supports both single-line and multi-line comments.

### Removed Example

```c
int a = 5; // TODO(KF): remove this later
```

becomes:

```c
int a = 5;
```

### Kept Example

```c
int a = 5; // normal comment
```

stays unchanged.

### Multi-Line Example

```c
/*
 * TODO(KF): this whole comment should be removed
 */
```

This comment will be removed.

## Important Behavior

- Only comments containing `TODO(KF)` are removed.
- Normal comments are kept.
- The selected files are edited in place.
- No new output files are created.
- The parser avoids removing text inside string literals, for example:

```c
char *text = "// TODO(KF): this is not a real comment";
```

This line will not be modified.

## Requirements

- Python 3.10 or newer is recommended.
- PyQt6

Install PyQt6 with:

```bash
pip install PyQt6
```

## How to Run

Save the Python script as something like:

```text
todo_kf_comment_remover.py
```

Then run:

```bash
python todo_kf_comment_remover.py
```

## How to Use

1. Open the application.
2. Click **Select .c / .h Files**.
3. Choose one or more `.c` or `.h` files.
4. Click **Remove TODO(KF) Comments From Selected Files**.
5. Confirm the warning.
6. The selected files will be edited directly.

## Recommended Safety Step

Because the tool edits files directly, it is strongly recommended to commit your project to Git or make a backup before running it.

Example with Git:

```bash
git status
git add .
git commit -m "Backup before removing TODO(KF) comments"
```

Then run the tool.

After running, you can review the changes with:

```bash
git diff
```

## Supported File Types

The file picker is configured for:

```text
.c
.h
```

You can also choose **All Files** if needed.

## Notes

This is a lightweight source-cleanup utility. It is not a full C compiler or preprocessor, but it handles normal C comments, strings, and character literals safely for typical Keil C source files.
