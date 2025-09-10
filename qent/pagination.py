from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.urls import remove_query_param, replace_query_param
from rest_framework.response import Response
from urllib.parse import urlencode


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            "data": data,
            "links": {
                "first": self.get_first_link(),
                "last": self.get_last_link(),
                "prev": self.get_previous_link(),
                "next": self.get_next_link(),
            },
            "meta": {
                "current_page": self.page.number,
                "from": self.page.start_index() if data else None,
                "last_page": self.page.paginator.num_pages,
                "links": self.get_page_links(),
                "path": self.request.build_absolute_uri(self.request.path),
                "per_page": self.get_page_size(self.request),
                "to": self.page.end_index() if data else None,
                "total": self.page.paginator.count
            }
        })

    def get_first_link(self):
        if self.page.number == 1:
            return None
        return replace_query_param(self.request.build_absolute_uri(), self.page_query_param, 1)

    def get_last_link(self):
        if self.page.number == self.page.paginator.num_pages:
            return None
        return replace_query_param(self.request.build_absolute_uri(), self.page_query_param,
                                        self.page.paginator.num_pages)

    def get_page_links(self):
        current = self.page.number
        total = self.page.paginator.num_pages
        links = []

        # Previous link
        links.append({
            "url": self.get_previous_link(),
            "label": "« السابق",
            "active": False
        })

        # Page numbers
        for i in range(1, total + 1):
            links.append({
                "url": replace_query_param(self.request.build_absolute_uri(), self.page_query_param, i),
                "label": str(i),
                "active": (i == current)
            })

        # Next link
        links.append({
            "url": self.get_next_link(),
            "label": "التالي »",
            "active": False
        })

        return links
