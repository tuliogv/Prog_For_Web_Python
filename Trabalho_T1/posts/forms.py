from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Escreva sua mensagem (até 500 caracteres)."})
        }

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
        # Remove todos os help_text padrão exibidos abaixo dos campos
        help_texts = {field: "" for field in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Some com mensagens automáticas nos campos
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        # Opcional: placeholders amigáveis
        self.fields["username"].widget.attrs.update({"placeholder": "Usuário"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Senha"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirme a senha"})
