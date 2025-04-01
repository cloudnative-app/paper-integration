import pandas as pd
import os
from datetime import datetime
import json
from pathlib import Path
import requests
import time
import re
from urllib.parse import urljoin
import logging

class PaperDownloader:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
    def setup_logging(self):
        """로깅 설정"""
        log_dir = Path(self.config['output_dir']) / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self, config_path):
        """설정 파일 로드"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # download_dir이 없으면 추가
                if 'download_dir' not in config:
                    config['download_dir'] = 'downloads'
                if 'timeout' not in config:
                    config['timeout'] = 30
                if 'retry_count' not in config:
                    config['retry_count'] = 3
                if 'delay' not in config:
                    config['delay'] = 2
                return config
        else:
            # 기본 설정
            default_config = {
                "source_dir": "source",
                "output_dir": "output",
                "download_dir": "downloads",
                "file_patterns": {
                    "acm": ["acm_converted_*.csv"],
                    "scopus": ["scopus*.csv"],
                    "wos": ["wos*.xls", "wos*.xlsx"],
                    "bib": ["*.bib"]
                },
                "timeout": 30,
                "retry_count": 3,
                "delay": 2
            }
            # 기본 설정 파일 생성
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config

    def _clean_filename(self, title):
        """파일명 정리"""
        # 특수문자 제거 및 공백을 언더스코어로 변경
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        return clean_title[:100]  # 파일명 길이 제한

    def _download_file(self, url, output_path, retry_count=0):
        """파일 다운로드"""
        try:
            response = requests.get(
                url,
                timeout=self.config['timeout']
            )
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            if retry_count < self.config['retry_count']:
                logging.warning(f"다운로드 재시도 중... ({retry_count + 1}/{self.config['retry_count']})")
                time.sleep(self.config['delay'])
                return self._download_file(url, output_path, retry_count + 1)
            else:
                logging.error(f"다운로드 실패: {url} - {str(e)}")
                return False

    def _get_paper_url(self, paper):
        """논문 URL 생성"""
        if pd.notna(paper['doi']):
            # DOI를 통한 URL 생성
            return f"https://doi.org/{paper['doi']}"
        elif pd.notna(paper['url']):
            # 기존 URL 사용
            return paper['url']
        return None

    def download_papers(self, papers_file):
        """논문 다운로드 실행"""
        # 결과 파일 읽기
        papers_df = pd.read_csv(papers_file)
        
        # 다운로드 디렉토리 생성
        download_dir = Path(self.config['download_dir'])
        download_dir.mkdir(exist_ok=True)
        
        # 다운로드 통계
        stats = {
            'total': len(papers_df),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for _, paper in papers_df.iterrows():
            # 파일명 생성
            filename = f"{paper['year']}_{self._clean_filename(paper['title'])}.pdf"
            output_path = download_dir / filename
            
            # 이미 다운로드된 파일 건너뛰기
            if output_path.exists():
                logging.info(f"이미 존재하는 파일 건너뛰기: {filename}")
                stats['skipped'] += 1
                continue
            
            # 논문 URL 가져오기
            url = self._get_paper_url(paper)
            if not url:
                logging.warning(f"URL 없음: {paper['title']}")
                stats['failed'] += 1
                continue
            
            # 다운로드 시도
            if self._download_file(url, output_path):
                logging.info(f"다운로드 성공: {filename}")
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            # API 제한 준수를 위한 대기
            time.sleep(self.config['delay'])
        
        # 결과 보고서 생성
        self._generate_report(stats, download_dir)
        
    def _generate_report(self, stats, download_dir):
        """다운로드 결과 보고서 생성"""
        report = f"""
다운로드 결과 보고서
====================
총 논문 수: {stats['total']}
다운로드 성공: {stats['success']}
다운로드 실패: {stats['failed']}
건너뛴 파일: {stats['skipped']}
다운로드 위치: {download_dir}
생성 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        report_path = download_dir / 'download_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logging.info(f"다운로드 보고서가 생성되었습니다: {report_path}")

    def generate_url_list(self, input_file):
        # CSV 파일 읽기
        df = pd.read_csv(input_file)
        
        # 마크다운 파일 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        downloads_dir = 'downloads'
        os.makedirs(downloads_dir, exist_ok=True)
        md_filename = os.path.join(downloads_dir, f'paper_urls_{timestamp}.md')
        
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write('# 논문 URL 리스트\n\n')
            
            for _, row in df.iterrows():
                title = row['title']
                year = row['year']
                source = row['source']
                doi = row.get('doi', '')
                url = row.get('url', '')
                
                # URL이 있거나 DOI가 있는 경우만 포함
                if url or doi:
                    f.write(f'## {title} ({year})\n')
                    f.write(f'- 출처: {source}\n')
                    
                    # DOI가 있는 경우 DOI URL 생성
                    if doi:
                        if doi.startswith('10.5555'):  # ACM 테스트 DOI도 포함
                            f.write(f'- DOI: {doi}\n')
                        else:
                            f.write(f'- URL: https://doi.org/{doi}\n')
                    # DOI가 없고 URL이 있는 경우 URL 사용
                    elif url:
                        f.write(f'- URL: {url}\n')
                    
                    f.write('\n')
        
        logging.info(f'URL 리스트가 생성되었습니다:')
        logging.info(f'- 마크다운 파일: {md_filename}')
        
        return md_filename

def main():
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 최신 papers 파일 찾기
    output_dir = 'output'
    papers_files = [f for f in os.listdir(output_dir) if f.startswith('papers_') and f.endswith('.csv')]
    if not papers_files:
        logging.error('papers 파일을 찾을 수 없습니다.')
        return
    
    latest_papers_file = max(papers_files)
    input_file = os.path.join(output_dir, latest_papers_file)
    
    # downloads 디렉토리 생성
    downloads_dir = 'downloads'
    os.makedirs(downloads_dir, exist_ok=True)
    
    logging.info(f'URL 리스트 생성 시작: {input_file}')
    downloader = PaperDownloader()
    downloader.generate_url_list(input_file)

if __name__ == "__main__":
    main() 