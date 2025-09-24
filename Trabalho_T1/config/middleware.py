class DisableCSRFMiddleware:
    """
    Bypass global do CSRF APENAS para desenvolvimento.
    Ativado quando DISABLE_CSRF=1 no ambiente (ver settings.py).
    NÃO use em produção.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Flag interna que faz o CsrfViewMiddleware pular a validação
        setattr(request, "_dont_enforce_csrf_checks", True)
        return self.get_response(request)
