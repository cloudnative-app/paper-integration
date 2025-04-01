import pandas as pd
import os
from datetime import datetime

def get_papers_urls():
    # output 디렉토리에서 최신 papers 파일 찾기
    output_dir = 'output'
    papers_files = [f for f in os.listdir(output_dir) if f.startswith('papers_') and f.endswith('.csv')]
    if not papers_files:
        raise FileNotFoundError('papers 파일을 찾을 수 없습니다.')
    
    latest_papers_file = max(papers_files)
    input_file = os.path.join(output_dir, latest_papers_file)
    
    # CSV 파일 읽기
    df = pd.read_csv(input_file)
    
    # 논문 URL 딕셔너리 생성
    papers_urls = {}
    
    for _, row in df.iterrows():
        title = row['title']
        doi = row.get('doi', '')
        url = row.get('url', '')
        
        # URL이 있거나 DOI가 있는 경우만 포함
        if url:
            papers_urls[title] = url
        elif doi:
            papers_urls[title] = f"https://doi.org/{doi}"
        else:
            papers_urls[title] = None
    
    return papers_urls

# URL 목록 생성
papers_urls = get_papers_urls() 