from wtforms.validators import ValidationError


class Unique(object):
    def __init__(self, model, field, message='This element already exist.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        query = {self.field.name: field.data}
        check = self.model.objects.filter(**query).first()
        if check and not check.is_anonymous():
            raise ValidationError(self.message)
