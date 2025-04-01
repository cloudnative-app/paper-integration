# Paper Integration System (논문 통합 관리 시스템)

이 프로젝트는 학술 데이터베이스(ACM, Scopus, Web of Science)에서 수집한 논문들을 효율적으로 관리하고 분석하는 시스템입니다.

## 프로젝트 구조

```
.
├── src/                    # 소스 코드
│   ├── paper_downloader.py    # 논문 PDF 자동 다운로드
│   ├── rename_papers.py       # 논문 파일명 자동 정리
│   ├── convert_bib_to_csv.py  # BibTeX to CSV 변환
│   ├── papers_urls.py         # 논문 URL 관리
│   ├── visualize_papers.py    # 논문 데이터 시각화
│   └── config.json           # 설정 파일
├── data/                   # 원본 데이터
│   ├── acm/               # ACM 데이터
│   ├── scopus/            # Scopus 데이터
│   └── wos/               # Web of Science 데이터
├── downloads/             # 다운로드된 PDF 파일
└── output/                # 처리된 결과물
    ├── logs/              # 로그 파일
    └── visualization/     # 시각화 결과
```

## 주요 기능

1. **논문 메타데이터 관리**
   - BibTeX 파일을 CSV 형식으로 변환
   - 논문 메타데이터 통합 및 정리

2. **PDF 파일 관리**
   - 논문 PDF 자동 다운로드
   - 파일명 자동 정리 (제목, 연도, 출처 기반)

3. **데이터 분석 및 시각화**
   - 연도별 논문 수 추이
   - 키워드 분석
   - 인용 네트워크 분석

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

1. BibTeX 파일을 CSV로 변환:
```bash
python src/convert_bib_to_csv.py
```

2. 논문 PDF 다운로드:
```bash
python src/paper_downloader.py
```

3. 논문 파일명 정리:
```bash
python src/rename_papers.py
```

4. 논문 데이터 시각화:
```bash
python src/visualize_papers.py
```

## 디렉토리 설명

- `src/`: 소스 코드 파일들이 위치
- `data/`: 원본 BibTeX 파일들이 위치 (acm, scopus, wos 하위 디렉토리로 구분)
- `downloads/`: 다운로드된 PDF 파일들이 저장
- `output/`: 처리된 CSV 파일들과 시각화 결과물이 저장

## 라이선스

MIT License 