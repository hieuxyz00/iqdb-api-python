import os
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from .enums import MatchType, Rating, Source
from .exceptions import (HttpRequestFailedException, ImageTooLargeException, InvalidFileFormatException, NoMatchFoundException, NotImageException, ParseException, ReadQueryResultException)
from .models import *


class SearchResultParser:
    """Parser để phân tích kết quả HTML từ IQDB."""

    def __init__(self):
        self._searched_stats_regex = re.compile(r'Searched ([\d,.]+) images in ([\d,.]+) seconds')
        self._similarity_regex = re.compile(r'(\d+)% similarity')
        self._resolution_regex = re.compile(r'(\d+)×(\d+)')
        self._score_regex = re.compile(r'Score:\s*([\d]+)')
        self._tags_regex = re.compile(r'Tags:\s*(.+)')
        self._source_mapping = {
            'Danbooru': Source.DANBOORU, 'Konachan': Source.KONACHAN,
            'yande.re': Source.YANDERE, 'Gelbooru': Source.GELBOORU,
            'Sankaku Channel': Source.SANKAKU_CHANNEL, 'e-shuushuu': Source.ESHUUSHUU,
            'The Anime Gallery': Source.THE_ANIME_GALLERY, 'Zerochan': Source.ZEROCHAN,
            'Anime-Pictures': Source.ANIME_PICTURES, '3dbooru': Source.THREEBOORU,
            'Idol Complex': Source.IDOL_COMPLEX,
        }

    def parse_result(self, html: str, debug: bool = False) -> SearchResult:
        if debug:
            print(f"--- IQDB HTML RESPONSE ---\n{html}\n--- END IQDB HTML RESPONSE ---")
        try:
            soup = BeautifulSoup(html, 'lxml')
            self._check_for_errors(soup, html)
            stats_text = soup.find(string=lambda t: 'searched' in t.lower() and 'seconds' in t.lower())
            searched_count, searched_seconds = self._parse_search_stats(stats_text)
            matches, your_image = self._parse_matches(soup)
            search_more_info = self._parse_search_more_info(soup)
            
            if not matches and "No relevant matches" not in html:
                raise NoMatchFoundException("Không tìm thấy thẻ kết quả nào.")

            return SearchResult(
                searched_images_count=searched_count, searched_in_seconds=searched_seconds,
                matches=matches, your_image=your_image, search_more_info=search_more_info
            )
        except Exception as e:
            if isinstance(e, IqdbApiException): raise
            raise ParseException("Không thể phân tích HTML từ IQDB.", inner_exception=e) from e

    def _check_for_errors(self, soup: BeautifulSoup, html: str):
        html_lower = html.lower()
        if "can't read query result!" in html_lower or "waiting for your other query to complete" in html_lower:
            raise ReadQueryResultException()
        
        if not (error_element := soup.select_one('.err')): return
        error_text = error_element.get_text(strip=True)
        if 'too large' in error_text.lower(): raise ImageTooLargeException(error_text)
        elif 'http request failed' in error_text.lower(): raise HttpRequestFailedException(error_text)
        elif 'not an image' in error_text.lower(): raise NotImageException(error_text)
        else: raise InvalidFileFormatException(f"Lỗi không xác định từ IQDB: {error_text}")
        
    def _parse_search_more_info(self, soup: BeautifulSoup) -> Optional[SearchMoreInfo]:
        if (node := soup.select_one("#yetmore")) and (href := node.get('href')):
            return SearchMoreInfo(href=href)
        return None

    def _parse_search_stats(self, stats_text: Optional[str]) -> Tuple[int, float]:
        if not stats_text or not (match := self._searched_stats_regex.search(stats_text)): return 0, 0.0
        return int(match.group(1).replace(',', '')), float(match.group(2))

    def _parse_matches(self, soup: BeautifulSoup) -> Tuple[List[Match], Optional[YourImage]]:
        matches, your_image = [], None
        if not (pages_div := soup.select_one('#pages')): return [], None
        all_divs = pages_div.find_all('div', recursive=False)
        if more_div := soup.select_one('#more1 .pages'):
            all_divs.extend(more_div.find_all('div', recursive=False))
        
        for div in all_divs:
            if not (table := div.find('table')): continue
            header_text = (th.get_text(strip=True).lower() if (th := table.find('th')) else "")
            if 'your image' in header_text: your_image = self._parse_your_image(table)
            elif 'no relevant matches' in header_text: continue
            else:
                match_type_map = {'best match': MatchType.BEST, 'additional match': MatchType.ADDITIONAL, 'possible match': MatchType.POSSIBLE}
                match_type = match_type_map.get(header_text, MatchType.OTHER)
                if parsed_match := self._parse_match(table, match_type):
                    matches.append(parsed_match)
        return matches, your_image

    def _parse_your_image(self, table: Tag) -> Optional[YourImage]:
        img_tag = table.find('img')
        preview_url = None
        if img_tag and (src := img_tag.get('src')):
            preview_url = f"https://iqdb.org{src}" if src.startswith('/') else src
        size_text = table.find(string=self._resolution_regex)
        name = (span['title'] if (span := table.select_one("span[title]")) else None)
        return YourImage(name=name, preview_url=preview_url, resolution=self._parse_resolution_from_text(size_text) if size_text else None)

    def _parse_match(self, table: Tag, match_type: MatchType) -> Optional[Match]:
        if not (main_link := table.find('a')) or not (url := main_link.get('href')): return None
        if url.startswith('//'): url = f'https:{url}'
        img_tag = table.find('img')
        preview_url = None
        if img_tag and (src := img_tag.get('src')):
            preview_url = f"https://iqdb.org{src}" if src.startswith('/') else src
        alt_text = img_tag.get('alt', '') if img_tag else ''
        text_content = table.get_text()
        return Match(
            match_type=match_type, url=url, preview_url=preview_url,
            similarity=self._parse_similarity_from_text(text_content),
            resolution=self._parse_resolution_from_text(text_content),
            source=self._parse_source_from_text(text_content),
            rating=self._parse_rating(text_content),
            score=self._parse_score_from_alt(alt_text),
            tags=self._parse_tags_from_alt(alt_text)
        )

    def _parse_similarity_from_text(self, text: str) -> Optional[float]:
        if match := self._similarity_regex.search(text): return float(match.group(1))
        return None

    def _parse_resolution_from_text(self, text: str) -> Optional[Resolution]:
        if match := self._resolution_regex.search(text): return Resolution(width=int(match.group(1)), height=int(match.group(2)))
        return None

    def _parse_source_from_text(self, text: str) -> Optional[Source]:
        for name, enum_val in self._source_mapping.items():
            if name in text: return enum_val
        return None

    def _parse_rating(self, text: str) -> Rating:
        text_lower = text.lower()
        if '[safe]' in text_lower: return Rating.SAFE
        if '[ero]' in text_lower or '[questionable]' in text_lower: return Rating.QUESTIONABLE
        if '[explicit]' in text_lower: return Rating.EXPLICIT
        return Rating.UNRATED

    def _parse_score_from_alt(self, alt_text: str) -> Optional[int]:
        if match := self._score_regex.search(alt_text): return int(match.group(1))
        return None
        
    def _parse_tags_from_alt(self, alt_text: str) -> Optional[List[str]]:
        if match := self._tags_regex.search(alt_text): return match.group(1).strip().split(' ')
        return None