import json

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from search.models import JobboleEsModel, ZhihuAnswerEsModel, ZhihuQuestionEsModel, LagouEsModel
from elasticsearch import Elasticsearch

client = Elasticsearch(hosts=['localhost'])


class SuggestView(View):
    """生成搜索建议并返回ajax响应"""

    def get(self, request):
        keywords = request.GET.get('s', '')
        rv = []
        if keywords:
            s = JobboleEsModel.search()
            s = s.suggest('my_suggest', keywords, completion={
                'field': 'suggest',
                'fuzzy': {'fuzziness': 2},  # 编辑距离
                'size': 10  # 返回搜索建议数量
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                rv.append(match._source['title'])

        return HttpResponse(json.dumps(rv), content_type='application/json')


class SearchView(View):
    """搜索"""

    def get(self, request):
        keywords = request.GET.get('q', '')
        response = client.search(
            index='jobbole',
            body={
                "query": {
                    "multi_match": {
                        "query": keywords,
                        "fields": ["tags", "title", "content"]}},
                "from": 0,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ["</span>"],
                    "fields": {
                        "title": {},
                        "content": {}}}})

        total_nums = response['hits']['total']
        all_hits = []
        for hit in response['hits']['hits']:
            one_hit = dict()
            one_hit['title'] = ''.join(hit['highlight']['title']) if 'title' in hit['highlight'] \
                else hit['_source']['title']
            one_hit['content'] = ''.join(hit['highlight']['content'][:500]) if 'content' in hit['highlight'] \
                else hit['_source']['content'][:500]

            one_hit['create_date'] = hit['_source']['create_date']
            one_hit['url'] = hit['_source']['url']
            one_hit['score'] = hit['_score']
            all_hits.append(one_hit)

        return render(request, 'result.html', {'all_hits': all_hits, 'key_words': keywords})
