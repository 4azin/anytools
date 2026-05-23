# PDF 병합기

여러 개의 PDF 파일을 터미널에서 입력한 순서대로 하나의 PDF로 병합하는 Python 스크립트입니다.

Windows 경로, Git Bash 경로(`/c/Users/...`), 한글 파일명, 공백이 포함된 파일명을 지원합니다. 공백이 포함된 경로는 따옴표로 감싸서 입력하는 것을 권장합니다.

## 요구 사항

- Python 3.10 이상
- `pypdf`

의존성 설치:

```bash
pip install -r requirements.txt
```

## 사용 방법

스크립트를 실행합니다.

```bash
python merge_pdfs.py
```

프롬프트가 나오면 병합할 PDF 경로를 입력합니다. 입력한 순서대로 PDF가 합쳐집니다.

Python 리스트 형식:

```text
["./a.pdf", "./b.pdf", "/c/Users/SSAFY/Desktop/c.pdf"]
```

쉼표 구분 형식:

```text
./a.pdf, ./b.pdf, /c/Users/SSAFY/Desktop/c.pdf
```

공백 또는 한글이 포함된 경로:

```text
"/c/Users/SSAFY/Desktop/대학 증명서.pdf", "/c/Users/SSAFY/Desktop/성적 증명서.pdf"
```

그다음 저장할 PDF 파일 이름을 입력합니다.

```text
Output PDF file name [default: merged.pdf]: final_report
```

병합된 PDF는 항상 `result/` 폴더에 저장됩니다.

```text
result/final_report.pdf
```

파일 이름을 입력하지 않고 Enter를 누르면 기본 파일명으로 저장됩니다.

```text
result/merged.pdf
```

## 명령줄 인자 사용

PDF 경로를 실행 명령에 바로 넣을 수도 있습니다.

```bash
python merge_pdfs.py ./a.pdf ./b.pdf -o final_report
```

저장 위치:

```text
result/final_report.pdf
```

## Git 관리

생성된 PDF, 가상환경, Python 캐시 파일은 `.gitignore`로 제외됩니다.

제외되는 주요 항목:

- `venv/`
- `__pycache__/`
- `result/`
- `results/`
- `*.pdf`
