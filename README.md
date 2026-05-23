# Anytools

일상적인 파일 작업을 빠르게 처리하기 위한 작은 유틸리티 모음입니다.

## 도구 목록

### PDF 병합기

위치: `merge_pdf/`

여러 개의 PDF 파일을 터미널에서 입력한 순서대로 하나의 PDF로 병합합니다.

지원하는 입력:

- Windows 경로
- Git Bash 경로(`/c/Users/...`)
- 한글 파일명
- 공백이 포함된 파일명

실행 방법:

```bash
cd merge_pdf
pip install -r requirements.txt
python merge_pdfs.py
```

PDF 경로 입력 예시:

```text
["./a.pdf", "./b.pdf", "/c/Users/SSAFY/Desktop/c.pdf"]
```

또는:

```text
./a.pdf, ./b.pdf, /c/Users/SSAFY/Desktop/c.pdf
```

병합된 PDF는 항상 아래 폴더에 저장됩니다.

```text
merge_pdf/result/
```

자세한 사용법은 `merge_pdf/README.md`를 참고하세요.
