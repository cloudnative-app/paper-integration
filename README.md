# Paper Integration System

A system for managing and analyzing academic papers collected from various academic databases (ACM, Scopus, Web of Science).

논문 데이터베이스에서 수집한 논문들을 효율적으로 관리하고 분석하는 시스템입니다.

## Project Structure

```
.
├── src/                    # Source code
│   ├── paper_downloader.py    # Automatic PDF paper downloader
│   ├── rename_papers.py       # Automatic paper filename organizer
│   ├── convert_bib_to_csv.py  # BibTeX to CSV converter
│   ├── papers_urls.py         # Paper URL manager
│   ├── visualize_papers.py    # Paper data visualizer
│   └── config.json           # Configuration file
├── data/                   # Original data
│   ├── acm/               # ACM database files
│   ├── scopus/            # Scopus database files
│   └── wos/               # Web of Science database files
├── downloads/             # Downloaded PDF files
└── output/                # Processed results
    ├── logs/              # Log files
    └── visualization/     # Visualization results
```

## Features

1. **Paper Metadata Management**
   - Convert BibTeX files to CSV format
   - Integrate and organize paper metadata
   - BibTeX 파일을 CSV 형식으로 변환
   - 논문 메타데이터 통합 및 정리

2. **PDF File Management**
   - Automatic paper PDF download
   - Automatic filename organization (based on title, year, source)
   - 논문 PDF 자동 다운로드
   - 파일명 자동 정리 (제목, 연도, 출처 기반)

3. **Data Analysis and Visualization**
   - Paper count trends by year
   - Keyword analysis
   - Citation network analysis
   - 연도별 논문 수 추이
   - 키워드 분석
   - 인용 네트워크 분석

## Installation

1. Clone the repository:
```bash
git clone https://github.com/[username]/paper-integration.git
cd paper-integration
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Convert BibTeX files to CSV:
```bash
python src/convert_bib_to_csv.py
```

2. Download paper PDFs:
```bash
python src/paper_downloader.py
```

3. Organize paper filenames:
```bash
python src/rename_papers.py
```

4. Visualize paper data:
```bash
python src/visualize_papers.py
```

## Directory Description

- `src/`: Contains source code files
  - 소스 코드 파일들이 위치
- `data/`: Contains original BibTeX files (subdivided into acm, scopus, wos directories)
  - 원본 BibTeX 파일들이 위치 (acm, scopus, wos 하위 디렉토리로 구분)
- `downloads/`: Stores downloaded PDF files
  - 다운로드된 PDF 파일들이 저장
- `output/`: Stores processed CSV files and visualization results
  - 처리된 CSV 파일들과 시각화 결과물이 저장

## Requirements

- Python 3.8 or higher
- See `requirements.txt` for required packages

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- Email: cloud-native-app@outlook.com
- GitHub: [@cloudnative-app](https://github.com/cloudnative-app) 