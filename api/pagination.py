from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size=50
    page_size_query_param= 'size'
    max_page_size=1000
    def get_paginated_response(self,data,query):
        response={"query":query,
                  "count":self.page.paginator.count,
                  "size":self.page.paginator.per_page,
                   query:data,
                }
        if self.get_next_link():
            response["next"]=self.get_next_link()
        if self.get_previous_link():
            response["previous"]=self.get_previous_link()
        return Response(response)

class CommentPagination(PageNumberPagination):
    page_size=5
    page_size_query_param = 'size'
    max_page_size = 50

    def get_paginated_response(self, data,query):
        response= {
            'query': query,
            'count': self.page.paginator.count,
            'size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'comments': data
        }
        return Response(response)
