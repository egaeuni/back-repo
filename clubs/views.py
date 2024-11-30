from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from news.permissions import IsManagerOrReadOnly
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    # permission_classes = [AllowAny] # 테스트용
    permission_classes = [IsManagerOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        is_manager_club = user.is_manager
        club_name = self.request.data.get("name")

        print(user)
        print(is_manager_club)
        print(club_name)

        if club_name != is_manager_club:
            raise serializers.ValidationError("해당 동아리에 대해 동아리 탐험 글을 생성할 권한이 없습니다.")

        if Club.objects.filter(is_manager_club=club_name).exists():
            raise serializers.ValidationError("이미 해당 동아리의 탐험 글이 존재합니다.")

    def perform_update(self, serializer):
        user = self.request.user
        club = self.get_object()

        if club.name != user.is_manager:
            raise serializers.ValidationError("해당 동아리에 대해 동아리 탐험 글을 생성할 권한이 없습니다.")
        
        serializer.save()

    def list(self, request, pk=None):
        queryset = self.get_queryset()
        serializer = ClubListSerializer(queryset, many=True)
        return Response({"message":"동아리 정보 조회에 성공하였습니다.", "result":serializer.data}, status=status.HTTP_200_OK)

class ClubLikeViewSet(viewsets.ModelViewSet):
    queryset = ClubLike.objects.all()
    serializer_class = ClubLikeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        club = get_object_or_404(Club, pk=pk)
        user = request.user

        try:
            existing_like = ClubLike.objects.get(user=user, club=club)
            existing_like.delete()
            message = "좋아요가 취소되었습니다."
            status_code = status.HTTP_200_OK
        except ClubLike.DoesNotExist:
            ClubLike.objects.create(user=user, club=club)
            message = "좋아요가 추가되었습니다."
            status_code = status.HTTP_201_CREATED

        club.refresh_from_db()
        return Response({"message": message, "likes_count": club.likes_count}, status=status_code)