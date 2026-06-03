# PDF Merge Tool

여러 개의 PDF 파일을 입력한 순서대로 하나의 PDF로 합치는 간단한 Python 스크립트입니다.

Windows 경로(`C:\Users\...`)와 Git Bash 경로(`/c/Users/...`)를 모두 지원합니다.

## Requirements

- Python 3.10+
- `pypdf`

## Install

프로젝트 폴더에서 가상환경을 만든 뒤, 그 가상환경의 Python으로 의존성을 설치하는 것을 권장합니다.

```powershell
cd merge_pdf
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt`에는 이미 `pypdf>=4.0.0`이 포함되어 있습니다.

## Run

가상환경의 Python으로 직접 실행하면 인터프리터 혼선을 피할 수 있습니다.

```powershell
.\venv\Scripts\python.exe .\merge_pdfs.py
```

명령줄 인자로 바로 넘길 수도 있습니다.

```powershell
.\venv\Scripts\python.exe .\merge_pdfs.py .\a.pdf .\b.pdf -o final_report
```

출력 파일은 항상 `result/` 폴더 아래에 저장됩니다.

## Interactive Input

스크립트는 아래 형식들을 지원합니다.

```text
["./a.pdf", "./b.pdf", "/c/Users/SSAFY/Desktop/c.pdf"]
```

```text
./a.pdf, ./b.pdf, /c/Users/SSAFY/Desktop/c.pdf
```

```text
"./file with spaces.pdf" "./next file.pdf"
```

출력 파일 이름을 비워두면 기본값은 `merged.pdf`입니다.

## If You See "pypdf is not installed"

이 경우는 대체로 `requirements.txt` 누락이 아니라, 다른 Python 인터프리터로 실행한 경우입니다.

아래 두 명령으로 확인하면 됩니다.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe .\merge_pdfs.py
```

## Git Notes

로컬 가상환경, 생성된 PDF, 캐시 파일은 `.gitignore`에 포함되어 있습니다.
