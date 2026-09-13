"""
Core package initialization.
Includes runtime compatibility patches for Django template context copying across Python versions (including Python 3.14+).
"""
import copy
from django.template import context as django_template_context


def _safe_basecontext_copy(self):
    """
    Python 3.14 changed copy(super()) semantics which breaks Django 4.2's
    BaseContext.__copy__. Creating the instance via object.__new__ and
    copying dicts restores compatibility across all Python versions.
    """
    duplicate = object.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    return duplicate


django_template_context.BaseContext.__copy__ = _safe_basecontext_copy
