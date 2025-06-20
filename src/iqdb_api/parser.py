"""
HTML parser cho IQDB responses
"""
import re
import os
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup, Tag

from .models import SearchResult, Match, YourImage, Resolution, QueueStatus
from .enums import MatchType, Rating, Source
from .exceptions import ParseException, ImageTooLargeException, HttpRequestFailedException, NotImageException, InvalidFileFormatException, NoMatchFoundException, InvalidIqdbHtmlException


class SearchResultParser:
    """Parser để phân tích kết quả HTML từ IQDB"""
    
    def __init__(self):
        self._searched_stats_regex = re.compile(r'[\d,.]+')
        self._score_regex = re.compile(r'Score:\s*([\d.]+)')
        self._similarity_regex = re.compile(r'(\d+)%\s*similarity')
        self._resolution_regex = re.compile(r'(\d+)×(\d+)')
        
        # Mapping từ tên source trong HTML sang enum
        self._source_mapping = {
            'Danbooru': Source.DANBOORU,
            'Anime-Pictures': Source.ANIME_PICTURES,
            'e-shuushuu': Source.ESHUUSHUU,
            'Gelbooru': Source.GELBOORU,
            'Konachan': Source.KONACHAN,
            'Sankaku Channel': Source.SANKAKU_CHANNEL,
            'The Anime Gallery': Source.THE_ANIME_GALLERY,
            'yande.re': Source.YANDERE,
            'Zerochan': Source.ZEROCHAN,
            '3dbooru': Source.THREEBOORU,
            'Idol Complex': Source.IDOL_COMPLEX,
        }
    
    def parse_result(self, html: str, debug: bool = False, debug_params: dict = None) -> SearchResult:
        """Parse HTML response thành SearchResult object hoặc QueueStatus nếu đang trong hàng đợi
        Nếu debug=True hoặc IQDB_DEBUG=1 thì in ra toàn bộ HTML trả về và params nếu có."""
        if debug or os.environ.get("IQDB_DEBUG") == "1":
            print("\n========== [IQDB DEBUG HTML - START] ==========")
            if debug_params:
                print("[IQDB DEBUG PARAMS]", debug_params)
            print(html)
            print("========== [IQDB DEBUG HTML - END] ==========")
        soup = BeautifulSoup(html, 'lxml')
        
        # Check for errors first
        self._check_for_errors(soup)
        
        # TODO: Queue/overload check
        # Khi IQDB quá tải, nó sẽ hiển thị thông báo và cập nhật HTML liên tục:
        # "IQDB is currently under high load, your query has been queued. Place in queue: X"
        queue_status = self._parse_queue_status(soup, html)
        if queue_status:
            return SearchResult(
                searched_images_count=0,
                searched_in_seconds=0.0,
                matches=[],
                your_image=None,
                queue_status=queue_status
            )
        
        try:
            # Parse search statistics
            searched_count, searched_seconds = self._parse_search_stats(soup)
            
            # Parse matches
            matches, your_image = self._parse_matches(soup, debug=debug or os.environ.get("IQDB_DEBUG") == "1")
            if not matches:
                raise NoMatchFoundException("Không tìm thấy bất kỳ match nào trong kết quả IQDB.")
            
            return SearchResult(
                searched_images_count=searched_count,
                searched_in_seconds=searched_seconds,
                matches=matches,
                your_image=your_image
            )
            
        except NoMatchFoundException:
            raise
        except Exception as e:
            raise InvalidIqdbHtmlException(f"Không thể phân tích HTML IQDB: {str(e)}") from e
    
    def _check_for_errors(self, soup: BeautifulSoup) -> None:
        """Kiểm tra lỗi trong HTML response"""
        error_element = soup.select_one('.err')
        if not error_element:
            return
            
        error_text = error_element.get_text().strip()
        if not error_text:
            return
            
        if 'too large' in error_text.lower():
            raise ImageTooLargeException(error_text)
        elif 'http request failed' in error_text.lower():
            raise HttpRequestFailedException(error_text)
        elif 'not an image' in error_text.lower():
            raise NotImageException(error_text)
        else:
            raise InvalidFileFormatException(f"Lỗi không xác định: {error_text}")
    
    def _parse_search_stats(self, soup: BeautifulSoup) -> Tuple[int, float]:
        """Parse thống kê tìm kiếm"""
        # Tìm text chứa thống kê tìm kiếm
        stats_text = ""
        for element in soup.find_all(text=True):
            if 'searched' in element.lower() and 'seconds' in element.lower():
                stats_text = element
                break
        
        if not stats_text:
            return 0, 0.0
            
        # Extract numbers từ text
        numbers = self._searched_stats_regex.findall(stats_text)
        if len(numbers) >= 2:
            # Thường format: "Searched X images in Y.Z seconds"
            try:
                searched_count = int(numbers[0].replace(',', ''))
                searched_seconds = float(numbers[1].replace(',', ''))
                return searched_count, searched_seconds
            except (ValueError, IndexError):
                pass
                
        return 0, 0.0
    
    def _parse_matches(self, soup: BeautifulSoup, debug: bool = False) -> Tuple[List[Match], Optional[YourImage]]:
        """Parse các kết quả match: best, additional, possible từ #pages; other từ #more1 nếu có."""
        matches = []
        best_match = None
        additional_matches = []
        possible_matches = []
        your_image = None

        # Parse main results in #pages (Best/Additional/Possible)
        pages_div = soup.select_one('#pages')
        if pages_div:
            # IQDB bọc mỗi kết quả trong 1 <div>, trong đó có <table>
            for div in pages_div.find_all('div', recursive=False):
                table = div.find('table')
                if not table:
                    continue
                th = table.find('th')
                if not th:
                    continue
                title = th.get_text(strip=True).lower()
                if 'your image' in title:
                    your_image = self._parse_your_image(table)
                elif 'best match' in title:
                    match = self._parse_match(table, MatchType.BEST, debug=debug)
                    if match:
                        best_match = match
                elif 'additional match' in title:
                    match = self._parse_match(table, MatchType.ADDITIONAL, debug=debug)
                    if match:
                        additional_matches.append(match)
                elif 'possible match' in title:
                    match = self._parse_match(table, MatchType.POSSIBLE, debug=debug)
                    if match:
                        possible_matches.append(match)

        # Parse Other results in #more1 (search_more=True hoặc khi user bấm See more)
        more1_div = soup.select_one('#more1 .pages')
        if more1_div:
            for div in more1_div.find_all('div', recursive=False):
                table = div.find('table')
                if not table:
                    continue
                match = self._parse_match(table, MatchType.OTHER, debug=debug)
                if match:
                    possible_matches.append(match)

        # Đảm bảo best match (nếu có) luôn ở đầu
        matches = []
        if best_match:
            matches.append(best_match)
        matches.extend(additional_matches)
        matches.extend(possible_matches)
        return matches, your_image
    
    def _parse_your_image(self, table: Tag) -> Optional[YourImage]:
        """Parse thông tin Your Image từ table"""
        try:
            img = table.find('img')
            preview_url = img.get('src') if img else None
            text = table.get_text()
            resolution = self._parse_resolution_from_text(text)
            return YourImage(
                preview_url=preview_url,
                resolution=resolution
            )
        except Exception:
            return YourImage()
    
    def _parse_match(self, table: Tag, match_type: MatchType, debug: bool = False) -> Optional[Match]:
        """Parse một kết quả match từ table, in debug nếu cần"""
        try:
            # Main link
            main_link = table.find('a')
            url = main_link.get('href', '') if main_link else ''
            # Thêm http: nếu url bắt đầu bằng //
            if url.startswith('//'):
                url = 'https:' + url if 'iqdb.org' in url or 'danbooru' in url or 'gelbooru' in url or 'yande.re' in url or 'konachan' in url or 'zerochan' in url or 'sankaku' in url else 'http:' + url
            # Preview image
            img = table.find('img')
            preview_url = img.get('src') if img else None
            if preview_url and preview_url.startswith('//'):
                preview_url = 'https:' + preview_url if 'iqdb.org' in preview_url or 'danbooru' in preview_url or 'gelbooru' in preview_url or 'yande.re' in preview_url or 'konachan' in preview_url or 'zerochan' in preview_url or 'sankaku' in preview_url else 'http:' + preview_url
            # Alt/title
            alt_text = img.get('alt', '') if img else ''
            title_text = img.get('title', '') if img else ''
            text = table.get_text()
            # Parse similarity
            similarity = self._parse_similarity_from_text(text + alt_text + title_text)
            # Parse resolution
            resolution = self._parse_resolution_from_text(text + alt_text + title_text)
            # Parse source
            source = self._parse_source_from_text(text + alt_text + title_text)
            # Parse tags
            tags = []
            for t in [alt_text, title_text, text]:
                if 'Tags:' in t:
                    tags_str = t.split('Tags:')[-1].strip()
                    tags += [tag.strip(',') for tag in tags_str.split(' ') if tag.strip(',')]
            tags = list(set(tags)) if tags else None
            # Parse rating
            rating = None
            for t in [alt_text, title_text, text]:
                if 'Rating:' in t:
                    val = t.split('Rating:')[-1].split()[0].strip().lower()
                    rating = val
                    break
            # Parse score
            score = None
            for t in [alt_text, title_text, text]:
                if 'Score:' in t:
                    try:
                        score = int(t.split('Score:')[-1].split()[0].strip())
                        break
                    except Exception:
                        pass
            match = Match(
                match_type=match_type,
                url=url,
                preview_url=preview_url,
                similarity=similarity,
                resolution=resolution,
                source=source,
                tags=tags,
                rating=rating,
                score=score
            )
            if debug or os.environ.get("IQDB_DEBUG") == "1":
                print("[IQDB DEBUG MATCH]", {
                    'type': match_type,
                    'url': url,
                    'preview_url': preview_url,
                    'similarity': similarity,
                    'resolution': resolution,
                    'source': source,
                    'tags': tags,
                    'rating': rating,
                    'score': score
                })
            return match
        except Exception as e:
            if debug or os.environ.get("IQDB_DEBUG") == "1":
                print(f"[IQDB DEBUG MATCH ERROR] {e}")
            return None
    
    def _parse_similarity_from_text(self, text: str) -> Optional[float]:
        """Parse similarity percentage từ text"""
        match = self._similarity_regex.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None
    
    def _parse_resolution_from_text(self, text: str) -> Optional[Resolution]:
        """Parse resolution từ text"""
        match = self._resolution_regex.search(text)
        if match:
            try:
                width = int(match.group(1))
                height = int(match.group(2))
                return Resolution(width=width, height=height)
            except ValueError:
                pass
        return None
    
    def _parse_source_from_text(self, text: str) -> Optional[Source]:
        """Parse source từ text"""
        for source_name, source_enum in self._source_mapping.items():
            if source_name.lower() in text.lower():
                return source_enum
        return None
    
    def _parse_queue_status(self, soup: BeautifulSoup, html: str):
        """Parse queue/overload/stream nếu IQDB đang quá tải"""
        # Chỉ nhận queue nếu có thông báo đặc trưng
        queue_strings = [
            'Place in queue:',
            'your query'
        ]
        found = None
        for s in queue_strings:
            found = soup.find(string=lambda t: t and s in t.lower())
            if found:
                break
        if found:
            import re
            queue_position = -1
            estimated_wait = 0.0    # TODO
            message = found.strip()
            m = re.search(r'Place in queue[:\s]*([0-9]+)', html, re.I)
            if m:
                queue_position = int(m.group(1))
            return QueueStatus(
                queue_position=queue_position,
                estimated_wait=estimated_wait,
                stream_html=html,
                message=message
            )
        return None
