import asyncio
from django.http import JsonResponse
from django.views import View


class AsyncHealthCheckView(View):
    async def get(self, request):
        await asyncio.sleep(1)  # simulate async work

        return JsonResponse({
            "status": "ok",
            "message": "Async view working",
        })
