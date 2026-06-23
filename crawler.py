import os
import sys
import requests
from bs4 import BeautifulSoup

def get_yahoo_finance_news(url, category_name, count=3):
    """
    야후 파이낸스 특정 카테고리 URL에서 뉴스 제목과 링크를 가져옵니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # 제외하고 싶은 제목 키워드 및 문구 (시황 정보 등 뉴스 기사가 아닌 것들)
    ignore_headlines = [
        "u.s. markets closed",
        "us markets closed",
        "u.s. markets open",
        "us markets open",
        "stock market today",
        "markets closed"
    ]
    
    news_list = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[{category_name}] 페이지 로드 실패 (Status: {response.status_code})")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        h3_tags = soup.find_all('h3')
        
        for h3 in h3_tags:
            title = h3.get_text().strip()
            if not title:
                continue
                
            # 노이즈 필터링
            title_lower = title.lower()
            if any(ignore in title_lower for ignore in ignore_headlines):
                continue
                
            # 링크 찾기 (h3 태그 내부 혹은 상위 a 태그)
            a_tag = h3.find('a') or h3.find_parent('a')
            if not a_tag:
                continue
                
            link = a_tag.get('href', '').strip()
            if not link:
                continue
                
            # 상대 경로인 경우 절대 경로로 변경
            if link.startswith('/'):
                link = f"https://finance.yahoo.com{link}"
            elif not link.startswith('http'):
                # 혹시 다른 형식의 상대 경로일 경우를 대비
                link = f"https://finance.yahoo.com/{link}"
                
            # 중복 기사 제거
            if any(item['link'] == link for item in news_list):
                continue
                
            news_list.append({
                'title': title,
                'link': link
            })
            
            # 목표 개수에 도달하면 정지
            if len(news_list) >= count:
                break
                
    except Exception as e:
        print(f"[{category_name}] 크롤링 중 오류 발생: {e}")
        
    return news_list

def get_yahoo_rss_news(url, category_name, count=3):
    """
    야후 뉴스 RSS 피드에서 뉴스 제목과 링크를 가져옵니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    from bs4 import XMLParsedAsHTMLWarning
    import warnings
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
    
    news_list = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[{category_name}] RSS 로드 실패 (Status: {response.status_code})")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('item')
        
        for item in items:
            title_tag = item.find('title')
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            if not title:
                continue
                
            link_tag = item.find('link')
            link = ''
            if link_tag and link_tag.next_sibling:
                link = link_tag.next_sibling.strip()
                
            if not link:
                guid_tag = item.find('guid')
                if guid_tag:
                    link = guid_tag.get_text().strip()
                    
            if not link:
                continue
                
            if link.startswith('/'):
                link = f"https://finance.yahoo.com{link}"
            elif not link.startswith('http'):
                link = f"https://finance.yahoo.com/{link}"
                
            if any(elem['link'] == link for elem in news_list):
                continue
                
            news_list.append({
                'title': title,
                'link': link
            })
            
            if len(news_list) >= count:
                break
                
    except Exception as e:
        print(f"[{category_name}] RSS 크롤링 중 오류 발생: {e}")
        
    return news_list

def send_to_slack(webhook_url, economy_news, tech_news):
    """
    정리된 뉴스를 슬랙 웹훅으로 전송합니다.
    """
    if not economy_news and not tech_news:
        print("전송할 뉴스 데이터가 없습니다.")
        return False
        
    # 슬랙 마크다운 형식 메시지 구성
    message_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Yahoo Finance 최신 뉴스 브리핑 📢",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 1. 매크로 경제 뉴스 추가
    economy_text = ""
    if economy_news:
        for idx, news in enumerate(economy_news, 1):
            economy_text += f"{idx}. *{news['title']}*\n   • 링크: {news['link']}\n"
    else:
        economy_text = "가져온 경제 뉴스가 없습니다."
        
    message_blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📈 미국 매크로 경제 최신 뉴스*\n{economy_text}"
        }
    })
    
    message_blocks.append({
        "type": "divider"
    })
    
    # 2. AI/테크 뉴스 추가
    tech_text = ""
    if tech_news:
        for idx, news in enumerate(tech_news, 1):
            tech_text += f"{idx}. *{news['title']}*\n   • 링크: {news['link']}\n"
    else:
        tech_text = "가져온 테크 뉴스가 없습니다."
        
    message_blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*🤖 AI 테크 기업 최신 뉴스*\n{tech_text}"
        }
    })
    
    payload = {
        "blocks": message_blocks
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("슬랙 메시지 전송 성공!")
            return True
        else:
            print(f"슬랙 메시지 전송 실패 (Status: {response.status_code}, Res: {response.text})")
            return False
    except Exception as e:
        print(f"슬랙 메시지 전송 중 오류 발생: {e}")
        return False

def main():
    # 환경변수에서 슬랙 웹훅 URL 가져오기
    slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("오류: 환경변수 SLACK_WEBHOOK_URL이 설정되어 있지 않습니다.", file=sys.stderr)
        print("스크립트를 실행하기 전에 SLACK_WEBHOOK_URL 환경변수를 설정해주세요.", file=sys.stderr)
        sys.exit(1)
        
    print("야후 파이낸스 뉴스 크롤링 시작...")
    
    # 1. 미국 매크로 경제 뉴스 3개 가져오기
    economy_url = "https://finance.yahoo.com/topic/economic-news/"
    economy_news = get_yahoo_finance_news(economy_url, "미국 경제", count=3)
    
    # 2. AI 및 테크 뉴스 3개 가져오기 (실시간 갱신을 위해 RSS 피드 사용)
    tech_url = "https://news.yahoo.com/rss/tech"
    tech_news = get_yahoo_rss_news(tech_url, "AI/테크", count=3)
    
    # 결과 출력
    print(f"\n[미국 매크로 경제 뉴스 ({len(economy_news)}개)]")
    for news in economy_news:
        print(f"- {news['title']}\n  ({news['link']})")
        
    print(f"\n[AI 테크 기업 뉴스 ({len(tech_news)}개)]")
    for news in tech_news:
        print(f"- {news['title']}\n  ({news['link']})")
        
    # 3. 슬랙 전송
    print("\n슬랙으로 메시지 전송 중...")
    send_to_slack(slack_webhook_url, economy_news, tech_news)

if __name__ == "__main__":
    main()
