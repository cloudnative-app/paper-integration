import os
import pandas as pd
import re
from datetime import datetime
from PyPDF2 import PdfReader
import difflib
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging

def setup_logging():
    """로깅 설정을 초기화합니다."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'rename_papers_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def sanitize_filename(filename):
    # 윈도우에서 사용할 수 없는 문자들을 '-'로 변경
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '-', filename)

def is_already_renamed(filename, papers_info):
    """파일명이 이미 논문 정보 형식으로 변경되었는지 확인합니다."""
    # 파일명에서 확장자 제거
    base_name = os.path.splitext(filename)[0]
    
    # 논문 정보의 파일명과 비교
    for info in papers_info.values():
        if base_name == info['filename']:
            return True
    return False

def extract_title_from_pdf(pdf_path):
    """PDF 파일의 첫 페이지에서 제목을 추출합니다."""
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text()
            lines = text.split('\n')
            
            # 제목 후보들
            candidates = []
            
            for line in lines:
                line = line.strip()
                # 빈 줄이나 특수 문자로만 이루어진 줄은 건너뛰기
                if not line or all(c in '_-=*' for c in line):
                    continue
                
                # DOI나 URL이 포함된 줄은 건너뛰기
                if 'doi.org' in line.lower() or 'http' in line.lower():
                    continue
                
                # 페이지 번호나 날짜 형식은 건너뛰기
                if re.match(r'^\d+$', line) or re.match(r'^\d{4}$', line):
                    continue
                
                # 제목으로 보일 수 있는 조건:
                # 1. 첫 줄이거나
                # 2. 이전 줄이 빈 줄이거나
                # 3. 이전 줄이 특수 문자로만 이루어진 경우
                if not candidates or not lines[lines.index(line)-1].strip() or all(c in '_-=*' for c in lines[lines.index(line)-1]):
                    candidates.append(line)
            
            # 후보들 중 가장 긴 것을 선택 (보통 제목이 가장 긴 경우가 많음)
            if candidates:
                return max(candidates, key=len)
            return ""
        return ""
    except Exception as e:
        logging.error(f"PDF 읽기 오류 ({pdf_path}): {str(e)}")
        return ""

def find_best_match(title, papers_info):
    """가장 유사한 논문 제목을 찾습니다."""
    titles = list(papers_info.keys())
    matches = difflib.get_close_matches(title, titles, n=1, cutoff=0.5)
    return matches[0] if matches else None

def get_papers_info():
    # output 디렉토리에서 최신 papers 파일 찾기
    output_dir = 'output'
    papers_files = [f for f in os.listdir(output_dir) if f.startswith('papers_') and f.endswith('.csv')]
    if not papers_files:
        raise FileNotFoundError('papers 파일을 찾을 수 없습니다.')
    
    latest_papers_file = max(papers_files)
    input_file = os.path.join(output_dir, latest_papers_file)
    
    # CSV 파일 읽기
    df = pd.read_csv(input_file)
    
    # 논문 정보 딕셔너리 생성
    papers_info = {}
    
    for _, row in df.iterrows():
        title = row['title']
        year = str(row.get('year', ''))
        source = row.get('source', '')
        
        # 파일명 생성
        filename = f"{title}-{year}-{source}"
        filename = sanitize_filename(filename)
        
        papers_info[title] = {
            'year': year,
            'source': source,
            'filename': filename
        }
    
    return papers_info

def process_pdf_file(args):
    """단일 PDF 파일을 처리합니다."""
    pdf_file, pdf_path, papers_info = args
    
    # 이미 수정된 파일인지 확인
    if is_already_renamed(pdf_file, papers_info):
        return f"이미 수정된 파일 건너뛰기: {pdf_file}"
    
    # PDF에서 제목 추출
    title = extract_title_from_pdf(pdf_path)
    if not title:
        return f"제목 추출 실패: {pdf_file}"
    
    # 가장 유사한 논문 제목 찾기
    matched_title = find_best_match(title, papers_info)
    
    if matched_title:
        info = papers_info[matched_title]
        new_filename = f"{info['filename']}.pdf"
        new_path = os.path.join(os.path.dirname(pdf_path), new_filename)
        
        try:
            os.rename(pdf_path, new_path)
            return f"변경 완료: {pdf_file} -> {new_filename}"
        except Exception as e:
            return f"변경 실패: {pdf_file} - 오류: {str(e)}"
    else:
        return f"매칭 실패: {pdf_file}"

def rename_pdf_files():
    # 로깅 설정
    setup_logging()
    logging.info("파일명 변경 작업 시작")
    
    # 논문 정보 가져오기
    papers_info = get_papers_info()
    
    # downloads 디렉토리 경로
    download_dir = 'downloads'
    
    # PDF 파일 목록 가져오기
    pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
    logging.info(f"처리할 PDF 파일 수: {len(pdf_files)}")
    
    # 처리할 파일 목록 생성
    process_args = [(f, os.path.join(download_dir, f), papers_info) for f in pdf_files]
    
    # 병렬 처리로 파일 이름 변경
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(tqdm(executor.map(process_pdf_file, process_args), 
                          total=len(pdf_files),
                          desc="파일 처리 중"))
    
    # 결과 출력 및 로깅
    for result in results:
        logging.info(result)
    
    logging.info("파일명 변경 작업 완료")

if __name__ == "__main__":
    rename_pdf_files() 