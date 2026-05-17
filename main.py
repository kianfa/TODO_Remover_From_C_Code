import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QVBoxLayout,
    QMessageBox,
    QListWidget,
)


TODO_KEY = "TODO"


def remove_todo_kf_comments(code: str) -> str:
    result = []

    i = 0
    n = len(code)

    in_string = False
    in_char = False

    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""

        # Inside string literal
        if in_string:
            result.append(ch)

            if ch == "\\" and i + 1 < n:
                result.append(code[i + 1])
                i += 2
                continue

            if ch == '"':
                in_string = False

            i += 1
            continue

        # Inside char literal
        if in_char:
            result.append(ch)

            if ch == "\\" and i + 1 < n:
                result.append(code[i + 1])
                i += 2
                continue

            if ch == "'":
                in_char = False

            i += 1
            continue

        # Start of string
        if ch == '"':
            result.append(ch)
            in_string = True
            i += 1
            continue

        # Start of char
        if ch == "'":
            result.append(ch)
            in_char = True
            i += 1
            continue

        # Handle // comment
        if ch == "/" and nxt == "/":
            start = i
            i += 2

            while i < n and code[i] != "\n":
                i += 1

            comment = code[start:i]

            if TODO_KEY not in comment:
                result.append(comment)

            if i < n and code[i] == "\n":
                result.append("\n")
                i += 1

            continue

        # Handle /* */ comment
        if ch == "/" and nxt == "*":
            start = i
            i += 2

            while i + 1 < n and not (code[i] == "*" and code[i + 1] == "/"):
                i += 1

            if i + 1 < n:
                i += 2

            comment = code[start:i]

            if TODO_KEY not in comment:
                result.append(comment)
            else:
                # Keep line count stable for multi-line comments
                result.append("\n" * comment.count("\n"))

            continue

        result.append(ch)
        i += 1

    return "".join(result)


class TodoCommentRemoverUI(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_files: list[Path] = []

        self.setWindowTitle("Remove TODO(KF) Comments")
        self.setMinimumWidth(650)
        self.setMinimumHeight(350)

        self.label = QLabel("No files selected")

        self.file_list = QListWidget()

        self.select_button = QPushButton("Select .c / .h Files")
        self.select_button.clicked.connect(self.select_files)

        self.clean_button = QPushButton("Remove TODO(KF) Comments From Selected Files")
        self.clean_button.clicked.connect(self.clean_files)
        self.clean_button.setEnabled(False)

        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.clear_selection)
        self.clear_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.file_list)
        layout.addWidget(self.select_button)
        layout.addWidget(self.clean_button)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def select_files(self):
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Select C / Header Files",
            "",
            "C / Header Files (*.c *.h);;All Files (*)",
        )

        if not file_names:
            return

        for file_name in file_names:
            path = Path(file_name)

            if path not in self.selected_files:
                self.selected_files.append(path)
                self.file_list.addItem(str(path))

        self.update_ui_state()

    def clear_selection(self):
        self.selected_files.clear()
        self.file_list.clear()
        self.update_ui_state()

    def update_ui_state(self):
        count = len(self.selected_files)

        if count == 0:
            self.label.setText("No files selected")
            self.clean_button.setEnabled(False)
            self.clear_button.setEnabled(False)
        elif count == 1:
            self.label.setText("1 file selected")
            self.clean_button.setEnabled(True)
            self.clear_button.setEnabled(True)
        else:
            self.label.setText(f"{count} files selected")
            self.clean_button.setEnabled(True)
            self.clear_button.setEnabled(True)

    def clean_files(self):
        if not self.selected_files:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Edit",
            (
                "This will modify the selected files directly.\n\n"
                f"Number of files: {len(self.selected_files)}\n\n"
                "Continue?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        success_count = 0
        changed_count = 0
        failed_files = []

        for file_path in self.selected_files:
            try:
                original_code = file_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                cleaned_code = remove_todo_kf_comments(original_code)

                if cleaned_code != original_code:
                    file_path.write_text(cleaned_code, encoding="utf-8")
                    changed_count += 1

                success_count += 1

            except Exception as e:
                failed_files.append(f"{file_path}\nReason: {e}")

        message = (
            f"Finished.\n\n"
            f"Files processed: {success_count}\n"
            f"Files changed: {changed_count}\n"
            f"Files failed: {len(failed_files)}"
        )

        if failed_files:
            message += "\n\nFailed files:\n\n" + "\n\n".join(failed_files)

        QMessageBox.information(
            self,
            "Done",
            message,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TodoCommentRemoverUI()
    window.show()

    sys.exit(app.exec())