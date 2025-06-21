"""
Các data model cho response từ IQDB API.
"""
from dataclasses import dataclass
from typing import List, Optional

from .enums import *


@dataclass
class Resolution:
    """Đại diện cho độ phân giải của một hình ảnh."""
    width: int
    height: int

    def __str__(self) -> str:
        return f"{self.width}×{self.height}"


@dataclass
class YourImage:
    """Thông tin về hình ảnh đầu vào của người dùng."""
    name: Optional[str] = None
    resolution: Optional[Resolution] = None
    preview_url: Optional[str] = None
    size: Optional[str] = None


@dataclass
class Match:
    """Đại diện cho một kết quả tìm kiếm tương tự được tìm thấy."""
    match_type: MatchType
    url: str
    preview_url: Optional[str] = None
    rating: Rating = Rating.UNRATED
    score: Optional[int] = None
    tags: Optional[List[str]] = None
    source: Optional[Source] = None
    resolution: Optional[Resolution] = None
    similarity: Optional[float] = None

    @property
    def is_best_match(self) -> bool:
        """Trả về True nếu đây là kết quả tốt nhất (`best match`)."""
        return self.match_type == MatchType.BEST


@dataclass
class SearchMoreInfo:
    """Thông tin cần thiết để thực hiện tìm kiếm 'more'."""
    href: str


@dataclass
class SearchResult:
    """Đối tượng kết quả tìm kiếm hoàn chỉnh."""
    searched_images_count: int
    searched_in_seconds: float
    matches: List[Match]
    your_image: Optional[YourImage] = None
    search_more_info: Optional[SearchMoreInfo] = None

    @property
    def is_found(self) -> bool:
        """Kiểm tra xem có tìm thấy kết quả nào là 'best match' không."""
        return any(match.match_type == MatchType.BEST for match in self.matches)

    @property
    def best_matches(self) -> List[Match]:
        """Lấy danh sách các kết quả tốt nhất (`best match`)."""
        return [match for match in self.matches if match.match_type == MatchType.BEST]

    @property
    def additional_matches(self) -> List[Match]:
        """Lấy danh sách các kết quả bổ sung (`additional match`)."""
        return [match for match in self.matches if match.match_type == MatchType.ADDITIONAL]

    @property
    def possible_matches(self) -> List[Match]:
        """Lấy danh sách các kết quả có thể (`possible match`)."""
        return [match for match in self.matches if match.match_type == MatchType.POSSIBLE]