"""领域异常（controller 边界翻译为 HTTP，不透底层异常）。"""


class DomainError(Exception):
    pass


class NotFound(DomainError):
    pass


class Forbidden(DomainError):
    pass


class Unauthorized(DomainError):
    pass


class BadRequest(DomainError):
    """请求语义错（旧密码不符等），controller 译 400。"""


class Conflict(DomainError):
    pass
