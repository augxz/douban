from flask import Flask, render_template, request
import requests  
from bs4 import BeautifulSoup  
import re  
from fetch_douban_top250jpg import fetch_douban_top250jpg  # 从同一目录下的 fetch_douban_top250.py 中导入函数

app = Flask(__name__)

# 定义电影类型选项
MOVIE_TYPES = [
    "犯罪", "剧情", "爱情", "同性", "灾难", "动画", "奇幻", "冒险", 
    "动作", "科幻", "悬疑", "惊悚", "传记", "历史", "战争", "音乐", 
    "喜剧", "歌舞", "古装", "家庭", "儿童", "西部", "纪录", "运动", 
    "情色", "武侠"
]

# 定义排序选项
SORT_OPTIONS = {
    "综合": "综合",
    "电影评分": "电影评分",
    "电影评价人数": "电影评价人数",
    "电影上映年份": "电影上映年份"
}

# 应用 CSS 样式的路由
@app.route('/static/css/styles.css')
def serve_css():
    """
    处理 CSS 样式文件的请求
    """
    return app.send_static_file('css/styles.css')

@app.route('/')
def index():
    """
    首页路由，获取电影数据并进行分页处理
    """
    movies = fetch_douban_top250jpg()  # 直接调用函数
    # 每页显示 10 条数据
    page = 1
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    paginated_movies = movies[start:end]
    total_pages = len(movies) // per_page + (1 if len(movies) % per_page else 0)

    # 为电影添加序号（1 - 250）
    start_index = (page - 1) * per_page + 1
    for i, movie in enumerate(paginated_movies, start=start_index):
        movie['index'] = f"{i}"

    return render_template('css版.html', movies=paginated_movies, page=page, total_pages=total_pages, sort_option="综合", sort_order="asc", SORT_OPTIONS=SORT_OPTIONS, MOVIE_TYPES=MOVIE_TYPES)

@app.route('/page/<int:page>')
def paginate(page):
    """
    分页路由，根据排序和筛选条件处理电影数据
    """
    sort_option = request.args.get('sort_option', '综合')
    sort_order = request.args.get('sort_order', 'asc')
    selected_types = request.args.getlist('movie_type')  # 获取选中的电影类型

    movies = fetch_douban_top250jpg()  # 直接调用函数

    # 根据选中的类型进行筛选
    if selected_types:
        filtered_movies = [movie for movie in movies if any(type_ in movie['电影类型'] for type_ in selected_types)]
    else:
        filtered_movies = movies

    if sort_option == "电影评分":
        if sort_order == "asc":
            filtered_movies.sort(key=lambda x: float(x['电影评分']))
        else:
            filtered_movies.sort(key=lambda x: float(x['电影评分']), reverse=True)
    elif sort_option == "电影评价人数":
        if sort_order == "asc":
            filtered_movies.sort(key=lambda x: int(x['电影评价人数'].replace(',', '')))
        else:
            filtered_movies.sort(key=lambda x: int(x['电影评价人数'].replace(',', '')), reverse=True)
    elif sort_option == "电影上映年份":
        if sort_order == "asc":
            filtered_movies.sort(key=lambda x: int(x['电影上映年份']))
        else:
            filtered_movies.sort(key=lambda x: int(x['电影上映年份']), reverse=True)
    else:  # 综合排序（默认）
        pass  # 无需特殊处理

    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    paginated_movies = filtered_movies[start:end]
    total_pages = len(filtered_movies) // per_page + (1 if len(filtered_movies) % per_page else 0)

    # 为电影添加序号（1 - 250）
    start_index = (page - 1) * per_page + 1
    for i, movie in enumerate(paginated_movies, start=start_index):
        movie['index'] = f"{i}"

    return render_template('css版.html', movies=paginated_movies, page=page, total_pages=total_pages, sort_option=sort_option, sort_order=sort_order, SORT_OPTIONS=SORT_OPTIONS, MOVIE_TYPES=MOVIE_TYPES, selected_types=selected_types)

@app.route('/search', methods=['GET'])
def search():
    """
    搜索路由，根据电影标题和导演进行搜索
    """
    query = request.args.get('query')  # 电影标题搜索
    director_query = request.args.get('director_query')  # 电影导演搜索

    movies = fetch_douban_top250jpg()

    filtered_movies_by_title = [movie for movie in movies if query.lower() in movie['电影标题'].lower()] if query else movies
    filtered_movies_by_director = [movie for movie in movies if director_query.lower() in movie['电影导演'].lower()] if director_query else movies

    # 取两个搜索结果的交集
    filtered_movies = [movie for movie in filtered_movies_by_title if movie in filtered_movies_by_director]

    per_page = 10
    total_pages = len(filtered_movies) // per_page + (1 if len(filtered_movies) % per_page else 0)
    page = 1  # 设置默认的页码
    return render_template('css版.html', movies=filtered_movies, page=page, total_pages=total_pages, SORT_OPTIONS=SORT_OPTIONS)

if __name__ == '__main__':
    app.run(debug=True)