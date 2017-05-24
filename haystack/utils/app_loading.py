# encoding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import importlib
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from haystack.constants import HAYSTACK_ADDITIONAL_MODELS

__all__ = ['haystack_get_models', 'haystack_load_apps']

APP = 'app'
MODEL = 'model'


def haystack_get_app_modules():
    """Return the Python module for each installed app"""
    retval = [i.module for i in apps.get_app_configs()]
    # Append the fake apps.
    if HAYSTACK_ADDITIONAL_MODELS:
        for module in HAYSTACK_ADDITIONAL_MODELS.keys():
            retval.append(importlib.import_module(module))
    return retval

def haystack_load_apps():
    """Return a list of app labels for all installed applications which have models"""
    retval = [i.label for i in apps.get_app_configs() if i.models_module is not None]
    if HAYSTACK_ADDITIONAL_MODELS:
        for module in HAYSTACK_ADDITIONAL_MODELS.keys():
            retval.append(module)
    return retval

def haystack_get_models(label):
    if HAYSTACK_ADDITIONAL_MODELS and label in HAYSTACK_ADDITIONAL_MODELS:
        # Try finding all models related to the additional faked apps.
        module = importlib.import_module(label)
        model_names = HAYSTACK_ADDITIONAL_MODELS[label]
        return [getattr(module, model_name, None) for model_name in model_names]

    try:
        # Try finding all models related to a given app
        app_mod = apps.get_app_config(label)
        return app_mod.get_models()
    except LookupError:
        if '.' not in label:
            raise ImproperlyConfigured('Unknown application label {}'.format(label))
        app_label, model_name = label.rsplit('.', 1)
        return [apps.get_model(app_label, model_name)]

    except ImproperlyConfigured:
        pass

def haystack_get_model(app_label, model_name):
    if HAYSTACK_ADDITIONAL_MODELS and app_label in HAYSTACK_ADDITIONAL_MODELS:
        module = importlib.import_module(app_label)
        retval = getattr(module, model_name, None)
    else:
        retval = apps.get_model(app_label, model_name)
    return retval
