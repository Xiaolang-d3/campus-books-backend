"""
书籍数据获取工具
支持从多个公开API获取书籍信息
"""
import requests
import time
from typing import Dict, List, Optional


class BookDataFetcher:
    """书籍数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_from_openlibrary_isbn(self, isbn: str) -> Optional[Dict]:
        """
        从Open Library通过ISBN获取书籍信息
        API文档: https://openlibrary.org/dev/docs/api/books
        """
        try:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                key = f"ISBN:{isbn}"
                
                if key in data:
                    book_data = data[key]
                    return self._parse_openlibrary_data(book_data, isbn)
            
            return None
        except Exception as e:
            print(f"Open Library API错误 (ISBN: {isbn}): {str(e)}")
            return None
    
    def search_openlibrary(self, title: str = None, author: str = None, limit: int = 10) -> List[Dict]:
        """
        从Open Library搜索书籍
        API文档: https://openlibrary.org/dev/docs/api/search
        """
        try:
            params = {'limit': limit}
            if title:
                params['title'] = title
            if author:
                params['author'] = author
            
            url = "https://openlibrary.org/search.json"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                books = []
                
                for doc in data.get('docs', [])[:limit]:
                    book = self._parse_openlibrary_search_result(doc)
                    if book:
                        books.append(book)
                
                return books
            
            return []
        except Exception as e:
            print(f"Open Library搜索错误: {str(e)}")
            return []
    
    def _parse_openlibrary_data(self, data: Dict, isbn: str) -> Dict:
        """解析Open Library API返回的数据"""
        book = {
            'isbn': isbn,
            'title': data.get('title', ''),
            'subtitle': data.get('subtitle', ''),
            'authors': [author.get('name', '') for author in data.get('authors', [])],
            'author': ', '.join([author.get('name', '') for author in data.get('authors', [])]),
            'publishers': [pub.get('name', '') for pub in data.get('publishers', [])],
            'publisher': ', '.join([pub.get('name', '') for pub in data.get('publishers', [])]),
            'publish_date': data.get('publish_date', ''),
            'number_of_pages': data.get('number_of_pages'),
            'subjects': [subj.get('name', '') for subj in data.get('subjects', [])],
            'description': '',
            'cover_url': '',
            'url': data.get('url', '')
        }
        
        # 获取封面图片
        if 'cover' in data:
            cover = data['cover']
            book['cover_url'] = cover.get('large') or cover.get('medium') or cover.get('small', '')
        
        # 获取简介
        if 'excerpts' in data and len(data['excerpts']) > 0:
            book['description'] = data['excerpts'][0].get('text', '')
        
        return book
    
    def _parse_openlibrary_search_result(self, doc: Dict) -> Optional[Dict]:
        """解析Open Library搜索结果"""
        try:
            # 获取ISBN
            isbn = None
            if 'isbn' in doc and len(doc['isbn']) > 0:
                isbn = doc['isbn'][0]
            
            book = {
                'isbn': isbn or '',
                'title': doc.get('title', ''),
                'author': ', '.join(doc.get('author_name', [])),
                'authors': doc.get('author_name', []),
                'publisher': ', '.join(doc.get('publisher', []))[:100] if 'publisher' in doc else '',
                'publishers': doc.get('publisher', []),
                'publish_date': str(doc.get('first_publish_year', '')),
                'number_of_pages': doc.get('number_of_pages_median'),
                'subjects': doc.get('subject', [])[:10],  # 限制主题数量
                'description': '',
                'cover_url': '',
                'url': f"https://openlibrary.org{doc.get('key', '')}"
            }
            
            # 获取封面
            if 'cover_i' in doc:
                cover_id = doc['cover_i']
                book['cover_url'] = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            
            return book
        except Exception as e:
            print(f"解析搜索结果错误: {str(e)}")
            return None
    
    def fetch_book_info(self, isbn: str = None, title: str = None, author: str = None) -> Optional[Dict]:
        """
        获取书籍信息（优先使用ISBN，其次使用标题和作者搜索）
        """
        if isbn:
            # 先尝试Open Library ISBN API
            book = self.fetch_from_openlibrary_isbn(isbn)
            if book:
                return book
        
        if title or author:
            # 使用搜索API
            results = self.search_openlibrary(title=title, author=author, limit=1)
            if results:
                return results[0]
        
        return None


def test_fetcher():
    """测试书籍数据获取"""
    fetcher = BookDataFetcher()
    
    print("=== 测试1: 通过ISBN获取书籍信息 ===")
    book = fetcher.fetch_from_openlibrary_isbn("9780140328721")
    if book:
        print(f"书名: {book['title']}")
        print(f"作者: {book['author']}")
        print(f"出版社: {book['publisher']}")
        print(f"ISBN: {book['isbn']}")
        print(f"封面: {book['cover_url']}")
    else:
        print("未找到书籍信息")
    
    print("\n=== 测试2: 搜索书籍 ===")
    books = fetcher.search_openlibrary(title="Python", limit=5)
    print(f"找到 {len(books)} 本书:")
    for i, book in enumerate(books, 1):
        print(f"{i}. {book['title']} - {book['author']}")
    
    print("\n=== 测试3: 综合查询 ===")
    book = fetcher.fetch_book_info(title="The Great Gatsby", author="Fitzgerald")
    if book:
        print(f"书名: {book['title']}")
        print(f"作者: {book['author']}")


if __name__ == '__main__':
    test_fetcher()
