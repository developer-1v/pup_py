from print_tricks import pt

def step_decorator(func):
    def wrapper(self, *args, **kwargs):
        self.steps_counter += 1
        step_name = func.__name__.replace('_', ' ').title()
        pt.c(f'\n------------------------{self.steps_counter} {step_name}------------------------')
        result = func(self, *args, **kwargs)
        print(f'\n - Success ({step_name} - ')
        return result
    return wrapper

def auto_decorate_methods(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__") and not attr_name.startswith("_"):
            setattr(cls, attr_name, step_decorator(attr_value))
    return cls