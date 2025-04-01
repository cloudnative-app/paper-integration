import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

def visualize_papers_by_year():
    # output 디렉토리에서 최신 papers 파일 찾기
    output_dir = 'output'
    papers_files = [f for f in os.listdir(output_dir) if f.startswith('papers_') and f.endswith('.csv')]
    if not papers_files:
        raise FileNotFoundError('papers 파일을 찾을 수 없습니다.')
    
    latest_papers_file = max(papers_files)
    input_file = os.path.join(output_dir, latest_papers_file)
    
    # CSV 파일 읽기
    df = pd.read_csv(input_file)
    
    # 연도별 논문 수 계산
    year_counts = df['year'].value_counts().sort_index()
    
    # 시각화 설정
    plt.figure(figsize=(12, 6))
    
    # 막대 그래프 생성
    bars = plt.bar(year_counts.index, year_counts.values)
    
    # 막대 위에 값 표시
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # 그래프 스타일 설정
    plt.title('연도별 논문 수', fontsize=14, pad=20)
    plt.xlabel('연도', fontsize=12)
    plt.ylabel('논문 수', fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # x축 레이블 회전
    plt.xticks(rotation=45)
    
    # 여백 조정
    plt.tight_layout()
    
    # 그래프 저장
    plt.savefig('output/visualization/papers_by_year.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("시각화가 완료되었습니다. output/visualization/papers_by_year.png 파일을 확인해주세요.")

if __name__ == "__main__":
    visualize_papers_by_year() 