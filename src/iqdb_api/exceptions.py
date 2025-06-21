"""
Các exception được sử dụng trong IQDB API
"""

class IqdbApiException(Exception):
    """Base exception cho tất cả các lỗi của IQDB API."""
    pass


class ImageTooLargeException(IqdbApiException):
    """Exception khi hình ảnh quá lớn (>8MB)."""
    def __init__(self, message: str = "Hình ảnh quá lớn. Kích thước tối đa là 8MB.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class HttpRequestFailedException(IqdbApiException):
    """Exception khi HTTP request thất bại."""
    def __init__(self, message: str = "HTTP request thất bại.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class NotImageException(IqdbApiException):
    """Exception khi file không phải là hình ảnh hợp lệ."""
    def __init__(self, message: str = "File không phải là hình ảnh hợp lệ.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class InvalidFileFormatException(IqdbApiException):
    """Exception khi định dạng file không được hỗ trợ hoặc không thể xử lý."""
    def __init__(self, message: str = "Định dạng file không được hỗ trợ hoặc không thể xử lý.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class ParseException(IqdbApiException):
    """Base exception cho các lỗi khi phân tích HTML."""
    def __init__(self, message: str = "Không thể phân tích kết quả HTML.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class ReadQueryResultException(ParseException):
    """
    Exception đặc biệt cho các trạng thái lỗi có thể thử lại từ server.
    Bao gồm lỗi "Can't read query result" hoặc khi phải chờ một query khác hoàn thành.
    """
    def __init__(self, message: str = "Gặp lỗi có thể thử lại từ server (hàng đợi hoặc đang chờ query khác).", inner_exception: Exception = None):
        super().__init__(message, inner_exception)


class NoMatchFoundException(IqdbApiException):
    """Exception khi không tìm thấy bất kỳ kết quả phù hợp nào."""
    pass


class InvalidIqdbHtmlException(IqdbApiException):
    """Exception khi HTML từ IQDB trả về không đúng định dạng mong đợi."""
    pass


class UserCancelledException(IqdbApiException):
    """Exception khi người dùng hủy thao tác (Ctrl+C hoặc task bị hủy)."""
    def __init__(self, message: str = "Tác vụ bị hủy bởi người dùng.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception