"""
Data models cho IQDB API responses
"""
from dataclasses import dataclass
from typing import List, Optional
from .enums import MatchType, Rating, Source


@dataclass
class Resolution:
    """Độ phân giải hình ảnh"""
    width: int
    height: int
    
    def __str__(self) -> str:
        return f"{self.width}×{self.height}"


@dataclass
class YourImage:
    """Thông tin về hình ảnh đầu vào của user"""
    name: Optional[str] = None
    resolution: Optional[Resolution] = None
    preview_url: Optional[str] = None
    size: Optional[str] = None


@dataclass 
class Match:
    """Kết quả tìm kiếm - một hình ảnh tương tự được tìm thấy"""
    match_type: MatchType
    url: str
    preview_url: Optional[str] = None
    rating: Optional[Rating] = None
    score: Optional[int] = None
    tags: Optional[List[str]] = None
    source: Optional[Source] = None
    resolution: Optional[Resolution] = None
    similarity: Optional[float] = None
    
    @property
    def is_best_match(self) -> bool:
        """Kiểm tra xem có phải là kết quả tốt nhất"""
        return self.match_type == MatchType.BEST


@dataclass
class QueueStatus:
    """Thông tin hàng đợi/overload IQDB"""
    queue_position: int = -1
    estimated_wait: float = 0.0  # giây
    stream_html: str = ""
    message: str = ""


@dataclass
class SearchResult:
    """Kết quả tìm kiếm hoàn chỉnh"""
    searched_images_count: int
    searched_in_seconds: float
    matches: List[Match]
    your_image: Optional[YourImage] = None
    queue_status: Optional[QueueStatus] = None
    
    @property
    def is_found(self) -> bool:
        """Kiểm tra xem có tìm thấy kết quả nào với độ tương tự cao"""
        return any(match.match_type == MatchType.BEST for match in self.matches)
    
    @property
    def best_matches(self) -> List[Match]:
        """Lấy danh sách kết quả tốt nhất"""
        return [match for match in self.matches if match.match_type == MatchType.BEST]
    
    @property
    def additional_matches(self) -> List[Match]:
        """Lấy danh sách kết quả bổ sung"""
        return [match for match in self.matches if match.match_type == MatchType.ADDITIONAL]
    
    @property
    def possible_matches(self) -> List[Match]:
        """Lấy danh sách kết quả có thể"""
        return [match for match in self.matches if match.match_type == MatchType.POSSIBLE]
