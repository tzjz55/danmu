import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from config import config


class TMDBAPIClient:
    """TMDB API客户端"""
    
    def __init__(self):
        self.base_url = config.TMDB_BASE_URL
        self.image_url = config.TMDB_IMAGE_URL
        self.api_key = config.TMDB_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整的API URL"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        separator = '&' if '?' in url else '?'
        url += f"{separator}api_key={self.api_key}&language=zh-CN"
        return url
    
    def get_image_url(self, path: str, size: str = 'w500') -> str:
        """获取图片完整URL"""
        if not path:
            return ""
        return f"{self.image_url}/t/p/{size}{path}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = self._build_url(endpoint)
        
        if params:
            # 将额外参数添加到URL
            param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
            url += f"&{param_str}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"TMDB API请求成功: {endpoint}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"TMDB API请求失败: {response.status} - {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )
        except aiohttp.ClientError as e:
            logger.error(f"TMDB网络请求错误: {e}")
            raise
        except Exception as e:
            logger.error(f"TMDB未知错误: {e}")
            raise
    
    async def search_movies(
        self, 
        query: str, 
        page: int = 1
    ) -> Dict[str, Any]:
        """搜索电影"""
        try:
            data = await self._make_request(
                '/search/movie',
                {'query': query, 'page': page}
            )
            
            # 处理搜索结果
            movies = []
            for movie in data.get('results', []):
                movies.append({
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'original_title': movie.get('original_title'),
                    'overview': movie.get('overview'),
                    'release_date': movie.get('release_date'),
                    'vote_average': movie.get('vote_average'),
                    'vote_count': movie.get('vote_count'),
                    'poster_path': movie.get('poster_path'),
                    'backdrop_path': movie.get('backdrop_path'),
                    'genre_ids': movie.get('genre_ids', []),
                    'poster_url': self.get_image_url(movie.get('poster_path')),
                    'backdrop_url': self.get_image_url(movie.get('backdrop_path'), 'w780')
                })
            
            return {
                'success': True,
                'data': {
                    'movies': movies,
                    'total_results': data.get('total_results', 0),
                    'total_pages': data.get('total_pages', 0),
                    'current_page': page
                },
                'message': f'找到 {len(movies)} 部电影'
            }
        except Exception as e:
            logger.error(f"电影搜索失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'电影搜索失败: {str(e)}'
            }
    
    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """获取电影详情"""
        try:
            data = await self._make_request(f'/movie/{movie_id}')
            
            # 处理电影详情
            movie = {
                'id': data.get('id'),
                'title': data.get('title'),
                'original_title': data.get('original_title'),
                'overview': data.get('overview'),
                'release_date': data.get('release_date'),
                'runtime': data.get('runtime'),
                'vote_average': data.get('vote_average'),
                'vote_count': data.get('vote_count'),
                'popularity': data.get('popularity'),
                'budget': data.get('budget'),
                'revenue': data.get('revenue'),
                'poster_path': data.get('poster_path'),
                'backdrop_path': data.get('backdrop_path'),
                'homepage': data.get('homepage'),
                'imdb_id': data.get('imdb_id'),
                'genres': [genre['name'] for genre in data.get('genres', [])],
                'production_companies': [
                    company['name'] for company in data.get('production_companies', [])
                ],
                'production_countries': [
                    country['name'] for country in data.get('production_countries', [])
                ],
                'spoken_languages': [
                    lang['name'] for lang in data.get('spoken_languages', [])
                ],
                'poster_url': self.get_image_url(data.get('poster_path')),
                'backdrop_url': self.get_image_url(data.get('backdrop_path'), 'w780')
            }
            
            return {
                'success': True,
                'data': movie,
                'message': '电影详情获取成功'
            }
        except Exception as e:
            logger.error(f"获取电影详情失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'获取电影详情失败: {str(e)}'
            }
    
    async def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """获取热门电影"""
        try:
            data = await self._make_request('/movie/popular', {'page': page})
            
            # 处理热门电影
            movies = []
            for movie in data.get('results', []):
                movies.append({
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'overview': movie.get('overview'),
                    'release_date': movie.get('release_date'),
                    'vote_average': movie.get('vote_average'),
                    'poster_url': self.get_image_url(movie.get('poster_path'))
                })
            
            return {
                'success': True,
                'data': {
                    'movies': movies,
                    'total_pages': data.get('total_pages', 0),
                    'current_page': page
                },
                'message': f'获取到 {len(movies)} 部热门电影'
            }
        except Exception as e:
            logger.error(f"获取热门电影失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'获取热门电影失败: {str(e)}'
            }
    
    async def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """获取电影演职员表"""
        try:
            data = await self._make_request(f'/movie/{movie_id}/credits')
            
            # 处理演职员表
            cast = []
            for person in data.get('cast', [])[:10]:  # 只取前10个演员
                cast.append({
                    'id': person.get('id'),
                    'name': person.get('name'),
                    'character': person.get('character'),
                    'profile_path': person.get('profile_path'),
                    'profile_url': self.get_image_url(person.get('profile_path'))
                })
            
            crew = []
            for person in data.get('crew', []):
                if person.get('job') in ['Director', 'Producer', 'Writer']:
                    crew.append({
                        'id': person.get('id'),
                        'name': person.get('name'),
                        'job': person.get('job'),
                        'profile_path': person.get('profile_path'),
                        'profile_url': self.get_image_url(person.get('profile_path'))
                    })
            
            return {
                'success': True,
                'data': {
                    'cast': cast,
                    'crew': crew
                },
                'message': '演职员表获取成功'
            }
        except Exception as e:
            logger.error(f"获取演职员表失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'获取演职员表失败: {str(e)}'
            }


# 全局客户端实例
tmdb_client = TMDBAPIClient()