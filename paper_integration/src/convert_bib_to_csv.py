import pandas as pd
from datetime import datetime
import re
import os

def clean_bibtex_value(value):
    """BibTeX 값을 정제하는 함수"""
    if not value:
        return None
        
    # 중괄호와 따옴표 제거
    value = re.sub(r'^[{"]|[}"]$', '', str(value).strip())
    value = value.strip(',')
    
    # LaTeX 특수 문자 처리
    latex_chars = {
        r'\"a': 'ä', r'\"o': 'ö', r'\"u': 'ü',
        r"\'a": 'á', r"\'e": 'é', r"\'i": 'í',
        r"\'o": 'ó', r"\'u": 'ú', r'\ss': 'ß',
        r'\ae': 'æ', r'\o': 'ø', r'\aa': 'å',
        r'\"{o}': 'ö', r'\"{u}': 'ü', r'\"{a}': 'ä',
        r"\'{e}": 'é', r"\'{i}": 'í', r"\'{o}": 'ó',
        r"\'{u}": 'ú', r"\'{a}": 'á',
        r'\"o': 'ö', r'\"u': 'ü', r'\"a': 'ä',
        r'\"O': 'Ö', r'\"U': 'Ü', r'\"A': 'Ä'
    }
    
    # LaTeX 특수 문자를 정규표현식 패턴으로 변환
    for latex, char in latex_chars.items():
        pattern = re.escape(latex)
        value = re.sub(pattern, char, value)
    
    # 중괄호로 감싸진 LaTeX 명령어 처리
    value = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', value)
    value = re.sub(r'\\[a-zA-Z]+', '', value)
    
    # 남은 중괄호 제거
    value = re.sub(r'{|}', '', value)
    
    return value.strip() if value.strip() else None

def extract_field_value(content, field_name):
    """BibTeX 필드 값을 추출하는 함수"""
    pattern = rf'{field_name}\s*=\s*(?:{{((?:[^{{}}]|{{[^{{}}]*}})*?)}}|"([^"]*)"|((?:[^,}}]|}}(?!,))*)),?'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    if match:
        value = next(v for v in match.groups() if v is not None)
        return clean_bibtex_value(value)
    return None

def process_bibtex_file(file_path):
    """BibTeX 파일을 처리하는 함수"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return []

    # 주석 제거
    content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
    
    # 레코드 분리
    records = []
    entries = re.split(r'@(\w+)\s*{', content)[1:]  # 첫 번째 빈 문자열 제외
    
    for i in range(0, len(entries), 2):
        if i + 1 >= len(entries):
            break
            
        record_type = entries[i].lower()
        entry_content = entries[i + 1]
        
        # cite_key 추출
        cite_key = entry_content.split(',', 1)[0].strip()
        
        # 필드 파싱
        record = {
            'type': record_type,
            'cite_key': cite_key
        }
        
        # 중요 필드 먼저 추출
        important_fields = ['title', 'author', 'year', 'booktitle', 'journal', 
                          'publisher', 'address', 'pages', 'doi', 'url', 
                          'abstract', 'keywords', 'document_type']
        
        for field in important_fields:
            value = extract_field_value(entry_content, field)
            if value:
                record[field] = value
        
        # type 필드를 document_type으로 매핑
        if 'type' in record:
            record['document_type'] = record['type']
            del record['type']
        
        # 나머지 필드 추출
        other_fields = re.findall(r'(\w+)\s*=\s*({[^}]*}|"[^"]*"|[^,}]+),?', entry_content)
        for key, value in other_fields:
            key = key.strip().lower()
            if key not in important_fields and key not in record:
                value = clean_bibtex_value(value)
                if value:
                    record[key] = value
        
        records.append(record)
    
    return records

def main():
    try:
        # 현재 디렉토리에서 BibTeX 파일 찾기
        current_dir = os.getcwd()
        bib_file = os.path.join(current_dir, "acm (2).bib")
        
        if not os.path.exists(bib_file):
            print(f"오류: BibTeX 파일을 찾을 수 없습니다: {bib_file}")
            return
            
        print(f"BibTeX 파일 처리 중: {bib_file}")
        
        # BibTeX 파일 처리
        records = process_bibtex_file(bib_file)
        
        if records:
            # DataFrame으로 변환
            df = pd.DataFrame(records)
            
            # 중요 컬럼 순서 지정
            important_columns = ['type', 'cite_key', 'title', 'author', 'year', 
                               'booktitle', 'journal', 'publisher', 'address', 
                               'pages', 'doi', 'url', 'abstract', 'keywords']
            
            # 존재하는 컬럼만 선택
            existing_columns = [col for col in important_columns if col in df.columns]
            other_columns = [col for col in df.columns if col not in existing_columns]
            
            # 컬럼 재정렬
            df = df[existing_columns + other_columns]
            
            # 빈 값 처리
            df = df.replace('', pd.NA)
            
            # 타임스탬프를 추가한 출력 파일 경로
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv = os.path.join(current_dir, f"acm_converted_{timestamp}.csv")
            
            # CSV 저장
            df.to_csv(output_csv, index=False, encoding="utf-8-sig")
            print(f"\nBibTeX 파일이 CSV로 변환되었습니다: {output_csv}")
            print(f"처리된 레코드 수: {len(records)}")
            print("\n컬럼 목록:")
            print(df.columns.tolist())
            print("\n중요 필드 통계:")
            for col in existing_columns:
                if col in df.columns:
                    non_null = df[col].notna().sum()
                    print(f"{col}: {non_null}개 (총 {len(df)}개 중)")
        else:
            print("BibTeX 파일에서 처리된 레코드가 없습니다.")
            
    except Exception as e:
        print(f"처리 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
