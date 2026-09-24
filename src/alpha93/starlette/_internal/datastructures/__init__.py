if __debug__ and __import__("typing").TYPE_CHECKING:
    from .headers import Headers, MutableHeaders
    from .multidict import CommaSeparatedStrings, ImmutableMultiDict, MultiDict
    from .params import QueryParams
    from .sessions import Secret
    from .state import State
    from .upload import FormData, UploadFile
    from .url import URL, Address, URLPath

    __all__ = (
        "URL",
        "Address",
        "CommaSeparatedStrings",
        "FormData",
        "Headers",
        "ImmutableMultiDict",
        "MultiDict",
        "MutableHeaders",
        "QueryParams",
        "Secret",
        "State",
        "URLPath",
        "UploadFile",
    )

def __getattr__(name: str, /):
    match name:
        case "URL":
            from .url import URL

            return URL
        case "Address":
            from .url import Address

            return Address
        case "CommaSeparatedStrings":
            from .multidict import CommaSeparatedStrings

            return CommaSeparatedStrings
        case "FormData":
            from .upload import FormData

            return FormData
        case "Headers":
            from .headers import Headers

            return Headers
        case "ImmutableMultiDict":
            from .multidict import ImmutableMultiDict

            return ImmutableMultiDict
        case "MultiDict":
            from .multidict import MultiDict

            return MultiDict
        case "MutableHeaders":
            from .headers import MutableHeaders

            return MutableHeaders
        case "QueryParams":
            from .params import QueryParams

            return QueryParams
        case "Secret":
            from .sessions import Secret

            return Secret
        case "State":
            from .state import State

            return State
        case "URLPath":
            from .url import URLPath

            return URLPath
        case "UploadFile":
            from .upload import UploadFile

            return UploadFile
        case _:
            raise ImportError
