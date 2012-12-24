from datetime import datetime
import logging

class DataSource:
    def __init__(self):
        self.fields = ['trailText', 'headline', 'liveBloggingNow', 'standfirst', 'commentable', 'thumbnail', 'byline']
        self.tags = []
        self.content_type = 'article'
        self.page_size = 10
        self.show_media = None
        self.lead_content = None
        self.sections = []
        self.from_date = None
        self.show_most_viewed = False

    def fetch_data(self, client):
        criteria = self._build_criteria()
        data = self._do_call(client, **criteria)
        return list(data)

    def _build_criteria(self):
        criteria = {}

        if self.fields:
            criteria['show-fields'] = ','.join(self.fields)

        if self.sections:
            criteria['section'] = '|'.join(self.sections)

        if self.content_type:
            self.tags.append('type/%s' % self.content_type)

        if self.tags:
            criteria['tag'] = ','.join(self.tags)

        if self.show_most_viewed:
            criteria['show-most-viewed'] = 'true'

        if self.lead_content:
            criteria['lead-content'] = self.lead_content

        if self.page_size:
            criteria['page-size'] = self.page_size

        if self.show_media:
            criteria['show-media'] = self.show_media

        if self.from_date:
            criteria['from-date'] = self.from_date

        return criteria


class SearchDataSource(DataSource):
    def _do_call(self, client, **criteria):
        return client.search(**criteria)


class EditorsPicksDataSource(DataSource):
    def _do_call(self, client, **criteria):
        return client.editors_picks(**criteria)


class CultureDataSource(SearchDataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.sections = ['culture']


class SportDataSource(SearchDataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.sections = ['sport']


class PicOfDayDataSource(SearchDataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.content_type = 'picture'
        self.tags = ['artanddesign/series/picture-of-the-day']
        self.page_size = 1
        self.show_media = 'picture'


class EyeWitnessDataSource(SearchDataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.content_type = 'picture'
        self.tags = ['world/series/eyewitness']
        self.page_size = 1
        self.show_media = 'picture'


class MostViewedDataSource(SearchDataSource):
    def __init__(self):
        DataSource.__init__(self)
        #today = str(datetime.now().date())
        #self.from_date = today
        self.show_most_viewed = True


class TopStoriesDataSource(EditorsPicksDataSource):
    def __init__(self):
        DataSource.__init__(self)
        #self.sections = ['uk', 'world']


def take_unique_subsets(size, data, priority_list):
    """
    data is a map of type string->list
    list is a list of maps each of which contains the field 'id'.
    priority_list is a list of strings each of which appears as a key in the data map.
    """

    items_seen_so_far = set()
    unique_subsets = {}

    for data_set_name in priority_list:
        unique_subset = []
        unique_subsets[data_set_name] = unique_subset
        source_data = data[data_set_name]
        for item in source_data:
            if item['id'] not in items_seen_so_far and len(unique_subset) < size:
                unique_subset.append(item)
                items_seen_so_far.add(item['id'])

    return unique_subsets


def fetch_all(client, data_sources):
    """
    data is a map of type string->data_source.
    return a map with same keys as data, and retrieved data as values
    """
    retrieved_data_map = {}
    for key in data_sources.keys():
        retrieved_data = data_sources[key].fetch_data(client)
        retrieved_data_map[key] = retrieved_data

    return retrieved_data_map