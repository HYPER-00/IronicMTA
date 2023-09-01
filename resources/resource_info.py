"""Resource Info"""


class ResourceInfo(object):
    """
        Resource Information\n
        * Author
        * Description
        * Version
        * OOP
    """

    def __init__(
        self,
        name: str = "IronicMTA Resource",
        author: str = "<unknown>",
        description: str = "",
        version: str = "V1.0",
        oop: bool = False,
    ) -> None:
        self._name = name
        self._author = author
        self._description = description
        self._version = version
        self._oop = oop

    def get_name(self) -> str:
        """Resource name"""
        return self._name

    def get_author(self) -> str:
        """Resource Author"""
        return self._author

    def get_description(self) -> str:
        """Resource Description"""
        return self._description

    def get_version(self) -> str:
        """Resource version"""
        return self._version

    def is_oop_enabled(self) -> bool:
        """Returns True if OOP is enables else False"""
        return self._oop
