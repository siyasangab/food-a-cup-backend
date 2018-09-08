from django.core.paginator import Paginator, PageNotAnInteger
from django.db.models import Q

PAGE_SIZE = 10

class Pager():
    def __init__(self, items, page_number = 1, page_size = PAGE_SIZE):
        self.items = items
        self.page_number = int(page_number if page_number else 1)
        if not page_size or int(page_size) not in [10, 15, 20]:
            self.page_size = PAGE_SIZE
        else: 
            self.page_size = int(page_size)


class PagedCollection():
    def __init__(self, total_pages = 0, page_size = 0, page_number = 0, total_count = 0, next_page = None, data = []):
        self.total_pages = total_pages
        self.page_size = page_size
        self.page_number = page_number
        self.total_count = total_count
        self.next_page = next_page
        self.data = data

    def __iter__(self):
        yield 'total_pages', self.total_pages
        yield 'page_number', self.page_number
        yield 'total_count', self.total_count
        yield 'next_page', self.next_page
        yield 'data', self.data

    def serialize_data(self, serializer):
        self.data = serializer(self.data, many = True).data
        return dict(self)
        

class PaginationService():

    def paginate(self, pager: Pager, filter: Q):
        paginator = Paginator(pager.items.filter(filter) if filter else pager.items, pager.page_size)
        if paginator.count == 0:
            return PagedCollection()

        data = list(paginator.get_page(pager.page_number))
        next_page = None if pager.page_number + 1 > paginator.num_pages else pager.page_number + 1

        paged_collection = PagedCollection(paginator.num_pages, pager.page_size, pager.page_number, paginator.count, next_page, data)
        return paged_collection
