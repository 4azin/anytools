from __future__ import annotations

import argparse
import ast
import os
import shlex
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = BASE_DIR / "result"

try:
    from pypdf import PdfWriter
except ImportError:
    PdfWriter = None


def build_missing_dependency_message() -> str:
    venv_python = BASE_DIR / "venv" / "Scripts" / "python.exe"
    requirements_path = BASE_DIR / "requirements.txt"

    message_lines = [
        "pypdf could not be imported by the current Python interpreter.",
        f"Current interpreter: {sys.executable}",
    ]

    if venv_python.exists():
        message_lines.extend(
            [
                "Install dependencies into the project virtual environment with:",
                f'  "{venv_python}" -m pip install -r "{requirements_path}"',
                "Then run the script with:",
                f'  "{venv_python}" "{BASE_DIR / "merge_pdfs.py"}"',
            ]
        )
    else:
        message_lines.append(
            "Install it with: pip install -r requirements.txt"
        )

    return "\n".join(message_lines)


def merge_pdfs(input_paths: list[Path], output_path: Path) -> None:
    if PdfWriter is None:
        raise RuntimeError(build_missing_dependency_message())

    if not input_paths:
        raise ValueError("Enter at least one PDF file to merge.")

    writer = PdfWriter()

    for pdf_path in input_paths:
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Only PDF files can be merged: {pdf_path}")

        writer.append(str(pdf_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output_file:
        writer.write(output_file)


def normalize_path(path_text: str) -> Path:
    path_text = path_text.strip().strip("\"'")

    if os.name == "nt" and len(path_text) >= 3:
        drive_candidate = path_text[1]
        if path_text[0] == "/" and path_text[2] == "/" and drive_candidate.isalpha():
            path_text = f"{drive_candidate.upper()}:{path_text[2:]}"

    return Path(path_text).expanduser()


def build_output_path(file_name: str) -> Path:
    file_name = file_name.strip().strip("\"'")
    if not file_name:
        file_name = "merged.pdf"

    output_name = Path(file_name).name
    if Path(output_name).suffix.lower() != ".pdf":
        output_name = f"{output_name}.pdf"

    return RESULT_DIR / output_name


def read_pdf_list_from_terminal() -> list[Path]:
    print("Enter PDF paths in one of these formats:")
    print('  ["./a.pdf", "./b.pdf", "/c/Users/SSAFY/Desktop/c.pdf"]')
    print("  ./a.pdf, ./b.pdf, /c/Users/SSAFY/Desktop/c.pdf")
    print('  "./file with spaces.pdf" "./next file.pdf"')
    raw_input_text = input("PDF path list: ").strip()

    parsed_paths: list[str]
    try:
        parsed_paths = ast.literal_eval(raw_input_text)
    except (SyntaxError, ValueError) as exc:
        parsed_paths = parse_loose_path_list(raw_input_text)
        if not parsed_paths:
            raise ValueError(
                "Could not read paths. Use a list, comma-separated paths, or quoted paths."
            ) from exc

    if not isinstance(parsed_paths, list):
        raise ValueError("Input must be a list.")
    if not all(isinstance(path, str) for path in parsed_paths):
        raise ValueError("Each path in the list must be a string.")

    return [normalize_path(path) for path in parsed_paths]


def parse_loose_path_list(raw_input_text: str) -> list[str]:
    raw_input_text = raw_input_text.strip()
    if not raw_input_text:
        return []

    if raw_input_text.startswith("[") and raw_input_text.endswith("]"):
        raw_input_text = raw_input_text[1:-1]

    if "," in raw_input_text:
        return [
            path.strip().strip("\"'")
            for path in raw_input_text.split(",")
            if path.strip()
        ]

    return shlex.split(raw_input_text)


def read_output_file_name_from_terminal() -> Path:
    output_text = input("Output PDF file name [default: merged.pdf]: ").strip()
    return build_output_path(output_text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge multiple PDF files into one PDF."
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        type=Path,
        help="PDF file paths to merge. They are merged in the entered order.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("merged.pdf"),
        help="Output PDF file name. It is always saved in the result folder. Default: merged.pdf.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.pdfs:
        input_paths = read_pdf_list_from_terminal()
        output_path = read_output_file_name_from_terminal()
    else:
        input_paths = [normalize_path(str(path)) for path in args.pdfs]
        output_path = build_output_path(str(args.output))

    try:
        merge_pdfs(input_paths, output_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Done: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
