from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

from .models import Post
from .forms import PostForm, SignUpForm

# ---------------------------
# Timeline pública (somente leitura)
# ---------------------------
class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 20

class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

# ---------------------------
# CRUD (somente autenticado)
# ---------------------------
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("posts:list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class OwnerOrStaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_staff or obj.author_id == self.request.user.id

class PostUpdateView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("posts:list")

class PostDeleteView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("posts:list")

# ---------------------------
# Login com timeline pública na mesma página
# ---------------------------
class PublicLoginView(LoginView):
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_posts"] = Post.objects.select_related("author").all()[:10]
        return ctx

# ---------------------------
# Cadastro (signup) sem mensagens/validações de senha chatas
# ---------------------------
class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()  # cria o usuário
        return super().form_valid(form)
