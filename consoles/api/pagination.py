from rest_framework.pagination import LimitOffsetPagination

class CdbDefaultPagination(LimitOffsetPagination):
    default_limit = 8
    limit_query_param = 'lim'
    limit_query_description = ('Number of results to return per page.')
    offset_query_param = 'offset'
    offset_query_description = ('The initial index from which to return the results.')

