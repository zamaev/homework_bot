class InvalidApiResponseException(Exception):
    """Некорректный ответ API."""


class InvalidApiResponseHomeworkException(Exception):
    """Некорректный homework в ответе API."""


class InvalidVerdictException(Exception):
    """Некорректный вердикт проверки домашнего задания."""
