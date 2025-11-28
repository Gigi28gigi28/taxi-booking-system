from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# REGISTER SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(read_only=True, default='passager')  # enforce passager

    class Meta:
        model = User
        fields = ('id', 'email', 'nom', 'prenom', 'password', 'password2', 'role')
        read_only_fields = ('id', 'role')

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        pw = attrs.get('password')
        pw2 = attrs.pop('password2', None)

        if pw != pw2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        validate_password(pw, user=User)
        return attrs

    def create(self, validated_data):
        validated_data['role'] = 'passager'  # default for registration flow
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nom=validated_data.get('nom', ''),
            prenom=validated_data.get('prenom', ''),
            role=validated_data['role']
        )
        return user


# CUSTOM JWT SERIALIZER
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Override SimpleJWT serializer to add custom claims: role, email
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["role"] = user.role
        token["email"] = user.email

        return token


# LOGIN SERIALIZER
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is deactivated.")

        attrs['user'] = user
        return attrs


# LOGOUT SERIALIZER
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")


# USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "nom", "prenom", "role")
        read_only_fields = fields


# CHAUFFEUR LOGIN SERIALIZER
class ChauffeurLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if user.role != "chauffeur":
            raise serializers.ValidationError("You are not a chauffeur.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is suspended.")

        attrs["user"] = user
        return attrs


# UPDATE PROFILE SERIALIZER
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nom', 'prenom']
        read_only_fields = ['email', 'role']

    def update(self, instance, validated_data):
        instance.nom = validated_data.get("nom", instance.nom)
        instance.prenom = validated_data.get("prenom", instance.prenom)
        instance.save()
        return instance


# CHANGE PASSWORD SERIALIZER
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
