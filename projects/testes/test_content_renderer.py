"""
Testes para o módulo content_renderer.

Testa a funcionalidade de renderização de conteúdo seguindo os princípios SOLID.
"""

import pytest

from projects.content_renderer import (
    ContentRenderer,
    ContentRendererFactory,
    MarkdownRenderer,
    PlainTextRenderer,
    render_content,
)


class TestMarkdownRenderer:
    """Testes para o MarkdownRenderer."""

    def test_render_basic_markdown(self):
        """Testa renderização básica de Markdown."""
        renderer = MarkdownRenderer()
        content = "# Título\n\nParagráfo com **negrito**."
        result = renderer.render(content)

        assert "<h1>Título</h1>" in result
        assert "<strong>negrito</strong>" in result

    def test_render_code_block(self):
        """Testa renderização de blocos de código."""
        renderer = MarkdownRenderer()
        content = "```python\nprint('Hello, World!')\n```"
        result = renderer.render(content)

        assert "<code" in result
        assert "print('Hello, World!')" in result

    def test_render_table(self):
        """Testa renderização de tabelas."""
        renderer = MarkdownRenderer()
        content = "| Col1 | Col2 |\n|------|------|\n| A    | B    |"
        result = renderer.render(content)

        assert "<table>" in result
        assert "<th>Col1</th>" in result
        assert "<td>A</td>" in result

    def test_render_empty_content(self):
        """Testa renderização de conteúdo vazio."""
        renderer = MarkdownRenderer()
        assert renderer.render("") == ""
        assert renderer.render(None) == ""

    def test_custom_extensions(self):
        """Testa renderizador com extensões customizadas."""
        renderer = MarkdownRenderer(extensions=["tables"])
        content = "| Col1 | Col2 |\n|------|------|\n| A    | B    |"
        result = renderer.render(content)

        assert "<table>" in result

    def test_error_handling(self):
        """Testa tratamento de erros no renderizador."""
        renderer = MarkdownRenderer()
        # Simula conteúdo que pode causar erro
        content = "<script>alert('xss')</script>"
        result = renderer.render(content)

        # Deve retornar algo (fallback ou conteúdo processado)
        assert isinstance(result, str)


class TestPlainTextRenderer:
    """Testes para o PlainTextRenderer."""

    def test_render_plain_text(self):
        """Testa renderização de texto simples."""
        renderer = PlainTextRenderer()
        content = "Linha 1\nLinha 2"
        result = renderer.render(content)

        assert "Linha 1<br>Linha 2" == result

    def test_render_html_escape(self):
        """Testa escape de HTML em texto simples."""
        renderer = PlainTextRenderer()
        content = "<script>alert('xss')</script>"
        result = renderer.render(content)

        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result

    def test_render_empty_content(self):
        """Testa renderização de conteúdo vazio."""
        renderer = PlainTextRenderer()
        assert renderer.render("") == ""
        assert renderer.render(None) == ""

    def test_render_ampersand_escape(self):
        """Testa escape de caracteres especiais."""
        renderer = PlainTextRenderer()
        content = "A & B < C > D"
        result = renderer.render(content)

        assert "A &amp; B &lt; C &gt; D" == result


class TestContentRendererFactory:
    """Testes para o ContentRendererFactory."""

    def test_get_markdown_renderer(self):
        """Testa obtenção do renderizador de Markdown."""
        renderer = ContentRendererFactory.get_renderer("markdown")
        assert isinstance(renderer, MarkdownRenderer)

    def test_get_plain_renderer(self):
        """Testa obtenção do renderizador de texto simples."""
        renderer = ContentRendererFactory.get_renderer("plain")
        assert isinstance(renderer, PlainTextRenderer)

    def test_get_unsupported_format(self):
        """Testa erro para formato não suportado."""
        with pytest.raises(ValueError, match="Formato 'unsupported' não suportado"):
            ContentRendererFactory.get_renderer("unsupported")

    def test_register_new_renderer(self):
        """Testa registro de novo renderizador."""

        class CustomRenderer(ContentRenderer):
            def render(self, content: str) -> str:
                return f"<custom>{content}</custom>"

        ContentRendererFactory.register_renderer("custom", CustomRenderer())
        renderer = ContentRendererFactory.get_renderer("custom")

        assert isinstance(renderer, CustomRenderer)
        assert renderer.render("test") == "<custom>test</custom>"

    def test_get_supported_formats(self):
        """Testa listagem de formatos suportados."""
        formats = ContentRendererFactory.get_supported_formats()

        assert "markdown" in formats
        assert "plain" in formats
        assert isinstance(formats, list)


class TestRenderContentFunction:
    """Testes para a função utilitária render_content."""

    def test_render_markdown_content(self):
        """Testa renderização de conteúdo Markdown."""
        content = "# Título"
        result = render_content(content, "markdown")

        assert "<h1>Título</h1>" in result

    def test_render_plain_content(self):
        """Testa renderização de conteúdo texto simples."""
        content = "Linha 1\nLinha 2"
        result = render_content(content, "plain")

        assert "Linha 1<br>Linha 2" == result

    def test_render_default_format(self):
        """Testa renderização com formato padrão (markdown)."""
        content = "**negrito**"
        result = render_content(content)

        assert "<strong>negrito</strong>" in result

    def test_render_unsupported_format_fallback(self):
        """Testa fallback para formato não suportado."""
        content = "Teste\ncom quebra"
        result = render_content(content, "unsupported")

        # Deve usar fallback para texto simples
        assert "Teste<br>com quebra" == result

    def test_render_empty_content(self):
        """Testa renderização de conteúdo vazio."""
        assert render_content("") == ""
        assert render_content("", "plain") == ""


class TestIntegration:
    """Testes de integração para o sistema de renderização."""

    def test_markdown_with_code_and_tables(self):
        """Testa renderização complexa com código e tabelas."""
        content = """
# Exemplo

| Comando | Descrição |
|---------|-----------|
| `ls`    | Lista arquivos |

```bash
$ ls -la
```
        """.strip()

        result = render_content(content, "markdown")

        assert "<h1>Exemplo</h1>" in result
        assert "<table>" in result
        assert "<code" in result
        assert "ls -la" in result

    def test_security_html_escape(self):
        """Testa segurança contra XSS em diferentes renderizadores."""
        malicious_content = "<script>alert('xss')</script>"

        # Markdown deve processar de forma segura
        md_result = render_content(malicious_content, "markdown")
        assert "<script>" not in md_result or "&lt;script&gt;" in md_result

        # Plain text deve fazer escape
        plain_result = render_content(malicious_content, "plain")
        assert "&lt;script&gt;" in plain_result
        assert "<script>" not in plain_result

    def test_performance_large_content(self):
        """Testa performance com conteúdo grande."""
        # Cria conteúdo grande
        large_content = "# Título\n\n" + "Parágrafo de teste. " * 1000

        # Deve processar sem erros
        result = render_content(large_content, "markdown")
        assert "<h1>Título</h1>" in result
        assert len(result) > len(large_content)  # HTML é maior que Markdown
