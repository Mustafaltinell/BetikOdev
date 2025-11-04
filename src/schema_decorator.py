# src/schema_decorator.py
# Zorunlu sütun kontrolü için dekoratör (ayrı modül)

from functools import wraps

class SchemaError(Exception):
    pass

def ensure_schema(required_columns):
    required = tuple(required_columns)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # `headers` anahtar parametre olarak beklenir
            headers = kwargs.get("headers")
            if headers is None:
                # headers positional olabilir, parametre adlarına bak
                for arg in args:
                    if isinstance(arg, (list, tuple)) and all(isinstance(x, str) for x in arg):
                        headers = arg
                        break
            if headers is None:
                raise SchemaError("Şema kontrolü için başlıklar (headers) sağlanmadı.")
            missing = [c for c in required if c not in headers]
            if missing:
                raise SchemaError(f"Zorunlu sütun(lar) eksik: {', '.join(missing)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
