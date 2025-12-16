"""
Módulo para renderização de conteúdo em diferentes formatos.

Este módulo implementa o padrão Strategy para renderização de conteúdo,
seguindo os princípios SOLID:
- Single Responsibility: Cada renderer tem uma responsabilidade específica
- Open/Closed: Fácil extensão para novos formatos sem modificar código existente
- Dependency Inversion: Depende de abstrações, não de implementações concretas
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

import markdown

logger = logging.getLogger(__name__)


class ContentRenderer(ABC):
    """Interface abstrata para renderizadores de conteúdo."""

    @abstractmethod
    def render(self, content: str) -> str:
        """Renderiza o conteúdo para HTML."""
        pass


class MarkdownRenderer(ContentRenderer):
    """Renderizador de Markdown para HTML."""

    def __init__(self, extensions: Optional[list] = None):
        """
        Inicializa o renderizador de Markdown.

        Args:
            extensions: Lista de extensões do Markdown a serem habilitadas
        """
        self.extensions = extensions or ["codehilite", "fenced_code", "tables", "toc"]

    def render(self, content: str) -> str:
        """
        Renderiza Markdown para HTML.

        Args:
            content: Conteúdo em Markdown

        Returns:
            HTML renderizado

        Raises:
            ValueError: Se o conteúdo for inválido
        """
        if not content:
            return ""

        try:
            return markdown.markdown(content, extensions=self.extensions)
        except Exception as e:
            logger.error(f"Erro ao renderizar Markdown: {e}")
            # Fallback: retorna o conteúdo original com escape HTML básico
            return content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class PlainTextRenderer(ContentRenderer):
    """Renderizador de texto simples para HTML."""

    def render(self, content: str) -> str:
        """
        Renderiza texto simples para HTML com quebras de linha preservadas.

        Args:
            content: Conteúdo em texto simples

        Returns:
            HTML renderizado
        """
        if not content:
            return ""

        # Escape HTML e preserva quebras de linha
        escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return escaped.replace("\n", "<br>")


class ContentRendererFactory:
    """Factory para criar renderizadores de conteúdo."""

    _renderers: Dict[str, ContentRenderer] = {}

    @classmethod
    def register_renderer(cls, format_type: str, renderer: ContentRenderer) -> None:
        """
        Registra um novo renderizador.

        Args:
            format_type: Tipo do formato (ex: 'markdown', 'plain')
            renderer: Instância do renderizador
        """
        cls._renderers[format_type] = renderer

    @classmethod
    def get_renderer(cls, format_type: str) -> ContentRenderer:
        """
        Obtém um renderizador pelo tipo.

        Args:
            format_type: Tipo do formato

        Returns:
            Renderizador correspondente

        Raises:
            ValueError: Se o tipo não for suportado
        """
        if format_type not in cls._renderers:
            raise ValueError(f"Formato '{format_type}' não suportado")
        return cls._renderers[format_type]

    @classmethod
    def get_supported_formats(cls) -> list:
        """Retorna lista de formatos suportados."""
        return list(cls._renderers.keys())


# Registrar renderizadores padrão
ContentRendererFactory.register_renderer("markdown", MarkdownRenderer())
ContentRendererFactory.register_renderer("plain", PlainTextRenderer())


def render_content(content: str, format_type: str = "markdown") -> str:
    """
    Função utilitária para renderizar conteúdo.

    Args:
        content: Conteúdo a ser renderizado
        format_type: Tipo do formato (padrão: markdown)

    Returns:
        HTML renderizado
    """
    try:
        renderer = ContentRendererFactory.get_renderer(format_type)
        return renderer.render(content)
    except ValueError as e:
        logger.warning(f"Formato não suportado, usando fallback: {e}")
        # Fallback para texto simples
        fallback_renderer = ContentRendererFactory.get_renderer("plain")
        return fallback_renderer.render(content)
