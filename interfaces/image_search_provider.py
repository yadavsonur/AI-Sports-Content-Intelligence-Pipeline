from abc import ABC
from abc import abstractmethod


class ImageSearchProvider(ABC):

    @abstractmethod
    def search(
        self,
        query
    ):
        pass