import re
from typing import Match, Pattern, Dict
from twisted.web.http import Request
from twisted.web.resource import NoResource, Resource
from twisted.web.server import Site

class Router(Site):
    def __init__(self, *args, **kwargs):
        super().__init__(NoResource(), *args, **kwargs)
        self._registry: Dict[Pattern[str], Resource] = {}
        
    def register(self, route: str, resource: Resource):
        route_regex: Pattern[str] = re.compile(route)
        self._registry[route_regex] = resource

    def getResourceFor(self, request: Request) -> Resource:
        request.site = self

        for route_regex, resource in self._registry.items():
            path: str = request.path.decode("utf-8")
            match: Match[str] = route_regex.match(path)
            if match:
                request.path_args = match.groupdict() or match.groups()
                return resource

        # path를 찾지 못했을때 twisted NoResource()로 리다이렉트
        return super().getResourceFor(request)



