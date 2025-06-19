"""
Các exception được sử dụng trong IQDB API
"""


class IqdbApiException(Exception):
    """Base exception cho tất cả IQDB API errors"""
    pass


class ImageTooLargeException(IqdbApiException):
    """Exception khi hình ảnh quá lớn (>8MB)"""
    def __init__(self, message: str = "Hình ảnh quá lớn. Kích thước tối đa là 8MB.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class HttpRequestFailedException(IqdbApiException):
    """Exception khi HTTP request thất bại"""
    def __init__(self, message: str = "HTTP request thất bại.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class NotImageException(IqdbApiException):
    """Exception khi file không phải là hình ảnh hợp lệ"""
    def __init__(self, message: str = "File không phải là hình ảnh hợp lệ.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class InvalidFileFormatException(IqdbApiException):
    """Exception khi format file không được hỗ trợ"""
    def __init__(self, message: str = "Format file không được hỗ trợ.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class ParseException(IqdbApiException):
    """Exception khi không thể parse HTML response"""
    def __init__(self, message: str = "Không thể phân tích kết quả HTML.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception


class NoMatchFoundException(IqdbApiException):
    """Không tìm thấy bất kỳ match nào trong kết quả IQDB"""
    pass


class InvalidIqdbHtmlException(IqdbApiException):
    """HTML IQDB trả về không đúng định dạng mong đợi"""
    pass


class UserCancelledException(IqdbApiException):
    """Exception khi người dùng hủy thao tác (Ctrl+C hoặc task bị hủy)"""
    def __init__(self, message: str = "Tác vụ bị hủy bởi người dùng.", inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception
