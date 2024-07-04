import requests  
from bs4 import BeautifulSoup  
import re  
   
def fetch_douban_top250jpg():  
    headers = {  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'  
    }  
    base_url = "https://movie.douban.com/top250"  
    movies = []  
      
    for start in range(0, 250, 25): 
        url = f"{base_url}?start={start}"  
        response = requests.get(url, headers=headers)  
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')  
        movie_list = soup.select('.grid_view li')  
        for movie in movie_list: 
            title = movie.find('span', class_='title').text  
            rating_num = movie.find('span', class_='rating_num').text
            span_element = movie.find('span', class_='inq')  
            if span_element:  
                dyjs=span_element.text  
            else:  
                dyjs="无数据"
            #爬取电影评价人数
            evaluation_count = movie.find('span', text=lambda text: text and '人评价' in text)
            if evaluation_count:  
                number_part = evaluation_count.text.split('人评价')[0]
            #爬取电影导演
            p_tag1 = movie.find('p', class_='')
            if p_tag1:  
                text = p_tag1.get_text(strip=True)  
                parts = text.split('导演:', 1)  # 分割一次，以获取“导演:”之后的部分  
                if len(parts) > 1:    
                    director_name = parts[1].split(None, 1)[0].strip()  # 使用split(None, 1)分割第一个空白字符，然后去除首尾空格  
                else:  
                    director_name="未找到电影导演信息" 
            else:  
                director_name="未找到电影导演信息"
            #爬取电影类型
            p_tag2 = movie.find('p', class_='').text
            h1=p_tag2.replace(" ", "")
            match = re.search(r'/([^/]*)$', h1)  
            if match:  
                a=match.group(1)  # 输出捕获组中的内容，即最后一个/后面的文字
                a1 = re.sub(r'\s+', '',a) 
                movie_type = '/'.join(a1[i:i+2] for i in range(0, len(a1), 2))
            #爬取上映年份
            p_tag3 = movie.find('p', class_='').text
            l1=p_tag2.replace(" ", "")  
            year_match = re.search(r'\b\d{4}\b', l1)  
            if year_match:  
                year=year_match.group()
            #爬取电影图片超链接 
            pic_div = movie.find('div', class_='pic')
            if pic_div:
                a_tag = pic_div.find('a')
                if a_tag:
                    img_tag = a_tag.find('img')
                    if img_tag:
                        image_src = img_tag['src']
                        jpglj=image_src
            #爬取电影超链接
            a_tag = movie.find("a", href=True)
            if a_tag:  
                ahref = a_tag['href']
            movies.append({  
                '电影标题': title,  
                '电影评分': rating_num,
                "电影评价人数": number_part,
                "电影导演":director_name,
                "电影类型":movie_type,
                "电影上映年份":year,
                "电影简述":dyjs,
                "电影图片超链接":jpglj,
                "电影超链接":ahref
            })  
      
    return movies

if __name__ == "__main__": 
    movies = fetch_douban_top250jpg()
    for movie in movies:  
        print(f"电影标题: {movie['电影标题']}, 电影评分: {movie['电影评分']}, 电影评价人数: {movie['电影评价人数']}, 电影导演: {movie['电影导演']}, 电影类型: {movie['电影类型']}, 电影上映年份: {movie['电影上映年份']}, 电影简述: {movie['电影简述']}, 电影超图片链接: {movie['电影图片超链接']}, 电影超链接: {movie['电影超链接']}")