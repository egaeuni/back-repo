from rest_framework import serializers
from .models import *
from datetime import date

class ClubRecruitSerializer(serializers.ModelSerializer):
    is_scrapped = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    club_code = serializers.CharField()
    club_field = serializers.CharField(required=False)

    class Meta:
        model = ClubRecruit
        fields = '__all__'
        read_only_fields = ('likes_count', 'created_at', 'updated_at', 'is_scrapped', 'is_applied', 'club', 'club_code')
    
    def create(self, validated_data):
        user = self.context["request"].user
        is_manager = user.is_manager
        club_code = validated_data.get('club_code')
        club_field = validated_data.get('club_field', '').strip()

        if not is_manager:
            raise serializers.ValidationError("모집 공고를 생성할 권한이 없습니다.")

        try:
            club = Club.objects.get(code=club_code)
            validated_data['club'] = club
        except Club.DoesNotExist:
            raise serializers.ValidationError("해당 동아리 정보를 먼저 등록해야 합니다.")

        if club_field:
            club_field = [field.strip() for field in club_field.split(',') if field.strip()]
            if len(club_field) > 5:
                raise serializers.ValidationError("활동분야는 최대 5개까지 입력 가능합니다.")
            validated_data['club_field'] = ', '.join(club_field)

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        if instance.club.code != user.is_manager:
            raise serializers.ValidationError("해당 공고를 수정할 권한이 없습니다.")
        validated_data.pop('club_code', None)
        return super().update(instance, validated_data)
    
    def delete(self, instance, validated_data):
        user = self.context['request'].user
        if instance.club.code != user.is_manager:
            raise serializers.ValidationError("해당 공고를 삭제할 권한이 없습니다.")
        validated_data.pop('club_code', None)
        return super().delete(instance, validated_data)
    
    def get_is_scrapped(self, obj): # 스크랩 눌렀는지
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return RecruitScrap.objects.filter(
                recruit = obj,
                user = request.user
            ).exists()
        return False

    def get_is_applied(self, obj): # 지원했는지
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return RecruitApply.objects.filter(
                recruit = obj,
                user = request.user
            ).exists()
        return False
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if 'club_field' in representation and representation['club_field']:
            club_field = representation['club_field']
            representation['club_field'] = [field.strip() for field in club_field.split(',') if field.strip()]
        else:
            representation['club_field'] = []

        return representation

class ClubRecruitListSerializer(serializers.ModelSerializer):
    d_day = serializers.SerializerMethodField()
    category = serializers.CharField(source='club.category')
    frequency = serializers.CharField(source='club.frequency')
    name = serializers.CharField(source='club.full_name')

    class Meta:
        model = ClubRecruit
        fields = ['image','name', 'title', 'category', 'style', 'frequency', 'created_at', 'updated_at', 'end_doc', 'd_day']

    def get_d_day(self, obj):
        d_day = (obj.end_doc - date.today()).days
        return d_day if d_day >=0 else "마감"
    
class RecruitScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitScrap
        fields = ['id', 'user', 'recruit', 'created_at']

class RecruitApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitScrap
        fields = ['id', 'user', 'recruit', 'created_at']