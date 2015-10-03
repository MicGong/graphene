import json

from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings

from graphql.core.error import GraphQLError, format_error


def form_error(error):
    if isinstance(error, GraphQLError):
        return format_error(error)
    return error


class GraphQLView(View):
    schema = None

    @staticmethod
    def format_result(result):
        data = {'data': result.data}
        if result.errors:
            data['errors'] = map(form_error, result.errors)

        return data

    def execute_query(self, request, query):
        if not query:
            data = {
                "errors": [{
                    "message": "Must provide query string."
                }]
            }
        else:
            try:
                result = self.schema.execute(query, root=object())
                data = self.format_result(result)
            except Exception, e:
                if settings.DEBUG:
                    raise e
                data = {
                    "errors": [{"message": str(e)}]
                }

        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        return self.execute_query(request, query or '')

    def post(self, request, *args, **kwargs):
        if request.body:
            received_json_data = json.loads(request.body)
            query = received_json_data.get('query')
        else:
            query = request.POST.get('query') or request.GET.get('query')
        raise Exception(query)
        return self.execute_query(request, query or '')
