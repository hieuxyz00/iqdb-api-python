"""
Test cases cho models
"""
import pytest
from iqdb_api.models import SearchResult, Match, YourImage, Resolution
from iqdb_api.enums import MatchType, Rating, Source


def test_resolution():
    """Test Resolution model"""
    res = Resolution(width=1920, height=1080)
    assert res.width == 1920
    assert res.height == 1080
    assert str(res) == "1920×1080"


def test_your_image():
    """Test YourImage model"""
    res = Resolution(800, 600)
    img = YourImage(
        name="test.jpg",
        resolution=res,
        preview_url="https://example.com/preview.jpg",
        size="100KB"
    )
    
    assert img.name == "test.jpg"
    assert img.resolution == res
    assert img.preview_url == "https://example.com/preview.jpg"
    assert img.size == "100KB"


def test_match():
    """Test Match model"""
    match = Match(
        match_type=MatchType.BEST,
        url="https://example.com/image.jpg",
        similarity=95.5,
        source=Source.DANBOORU
    )
    
    assert match.match_type == MatchType.BEST
    assert match.url == "https://example.com/image.jpg"
    assert match.similarity == 95.5
    assert match.source == Source.DANBOORU
    assert match.is_best_match is True
    
    # Test non-best match
    match2 = Match(
        match_type=MatchType.POSSIBLE,
        url="https://example.com/image2.jpg"
    )
    assert match2.is_best_match is False


def test_search_result():
    """Test SearchResult model"""
    best_match = Match(
        match_type=MatchType.BEST,
        url="https://example.com/best.jpg",
        similarity=95.0
    )
    
    additional_match = Match(
        match_type=MatchType.ADDITIONAL,
        url="https://example.com/additional.jpg",
        similarity=85.0
    )
    
    possible_match = Match(
        match_type=MatchType.POSSIBLE,
        url="https://example.com/possible.jpg",
        similarity=75.0
    )
    
    result = SearchResult(
        searched_images_count=1000,
        searched_in_seconds=2.5,
        matches=[best_match, additional_match, possible_match]
    )
    
    assert result.searched_images_count == 1000
    assert result.searched_in_seconds == 2.5
    assert len(result.matches) == 3
    
    # Test properties
    assert result.is_found is True
    assert len(result.best_matches) == 1
    assert len(result.additional_matches) == 1
    assert len(result.possible_matches) == 1
    
    # Test without best matches
    result_no_best = SearchResult(
        searched_images_count=1000,
        searched_in_seconds=2.5,
        matches=[additional_match, possible_match]
    )
    assert result_no_best.is_found is False
