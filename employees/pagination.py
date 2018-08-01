#import paginations
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    
    def get_paginated_response(self, data):
        print(vars(self.page))
        return Response({
                'count': self.page.paginator.count,
                'current_page_count':len(self.page.object_list),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
        })

    '''def get_paginated_response(self,data):
        print("Paginated",vars(self._paginator.page.paginator))
        print("Page",vars(self._paginator.page) )
        return Response({
                        'count' : self._paginator.page.paginator.count,
                        'current_page_count':len(self._paginator.page.object_list),
                        'next': '',
                        'previous': '',
                        'results': data
                        })'''
