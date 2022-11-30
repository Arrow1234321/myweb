from django.forms import ModelForm
from .models import Room, Reserve
from django.contrib.auth.models import User

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host','participants']



class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ReserveForm(ModelForm):
    class Meta:
        model = Reserve
        fields = ['name', 'author', 'serialnumber', 'borrowername']

