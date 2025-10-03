from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

from .models import Post
from .forms import PostForm, SignUpForm, AttachmentFormSet

# ---------------------------
# Timeline pública (somente leitura)
# ---------------------------
class PostListView(ListView):
    """Lista todos os posts na timeline, com paginação de 20 itens."""
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 20

class PostDetailView(DetailView):
    """Exibe detalhes de um post específico."""
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

# ---------------------------
# CRUD (somente autenticado)
# ---------------------------
class PostCreateView(LoginRequiredMixin, CreateView):
    """Cria novo post com anexos. Requer login."""
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("posts:list")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = AttachmentFormSet(self.request.POST, self.request.FILES)
        else:
            ctx["formset"] = AttachmentFormSet()
        return ctx

    def form_valid(self, form):
        form.instance.author = self.request.user
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class OwnerRequiredMixin(UserPassesTestMixin):
    """Permite acesso apenas ao autor do post."""
    def test_func(self):
        obj = self.get_object()
        return obj.author_id == self.request.user.id

class OwnerOrStaffRequiredMixin(UserPassesTestMixin):
    """Permite acesso apenas ao autor do post ou staff."""
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_staff or obj.author_id == self.request.user.id

class PostUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Edita post existente com anexos. Requer ser autor ou staff."""
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("posts:list")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            ctx["formset"] = AttachmentFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class PostDeleteView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, DeleteView):
    """Deleta post existente. Requer ser autor ou staff."""
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("posts:list")

# ---------------------------
# Login com timeline pública na mesma página
# ---------------------------
class PublicLoginView(LoginView):
    """Exibe posts recentes na página de login."""
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_posts"] = Post.objects.select_related("author").all()[:10]
        return ctx

# ---------------------------
# Cadastro (signup) sem mensagens/validações de senha "chatas"
# ---------------------------
class SignUpView(FormView):
    """Lida com o cadastro de usuários."""
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()  # cria o usuário
        return super().form_valid(form)
