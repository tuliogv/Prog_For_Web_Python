from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.conf import settings


from .models import Post, Attachment

class PostForm(forms.ModelForm):
    """Formulário para criar/editar posts."""
    class Meta:
        """Forma e widgets do Post."""
        model = Post
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Escreva sua mensagem (até 500 caracteres)."})
        }

class SignUpForm(UserCreationForm):
    """Formulário de cadastro sem mensagens/validações de senha."""
    class Meta:
        """Define o modelo e campos do formulário de cadastro."""
        model = User
        fields = ("username", "password1", "password2")
        # Tira todos os help_texts padrão:
        help_texts = {field: "" for field in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Some com mensagens automáticas nos campos:
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        # Opcional: placeholders amigáveis
        self.fields["username"].widget.attrs.update({"placeholder": "Usuário"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Senha"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirme a senha"})

class AttachmentForm(forms.ModelForm):
    """Formulário para anexos de mídia (imagens, áudio, vídeo)."""
    class Meta:
        """Define o modelo, campos, widgets e validações do formulário de anexos."""
        model = Attachment
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"accept": "image/*,audio/*,video/*"})
        }

        def clean_file(self):
            """Valida tamanho e tipo do arquivo."""
            f = self.cleaned_data.get("file")
            if not f:
                return f
            if f.size > getattr(settings, "MAX_UPLOAD_SIZE_BYTES", 25 * 1024 * 1024):
                raise forms.ValidationError("Arquivo excede o tamanho máximo permitido.")
            content_type = getattr(f, "content_type", None)
            if content_type and content_type not in getattr(settings, "ALLOWED_MEDIA_CONTENT_TYPES", []):
                raise forms.ValidationError("Tipo de arquivo não permitido.")
            return f

# Formset: até 1 anexo por submissão (pode aumentar o 'extra')
AttachmentFormSet = inlineformset_factory(
    Post,
    Attachment,
    form=AttachmentForm,
    fields=["file"],
    extra=1,
    can_delete=True,
)