import json

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from search.models import JobboleEsModel, ZhihuAnswerEsModel, ZhihuQuestionEsModel, LagouEsModel


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