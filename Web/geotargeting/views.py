from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Point
from .serializers import PointSerializer


class GeoView(APIView):
    @staticmethod
    def get(request):
        points = Point.objects.all()
        points_serialize = PointSerializer(points, many=True)
        return Response(
            {
                "points": points_serialize.data,
            })
