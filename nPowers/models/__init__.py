from datetime import datetime
from slugify import slugify

from nPowers import db, bcrypt


class User(db.Document):
    username = db.StringField(max_length=50)
    email = db.EmailField(max_length=50)
    password_hash = db.StringField(max_length=255)
    is_staff = db.BooleanField()
    activated = db.BooleanField()

    def hash_password(self, plaintext):
        self.password_hash = bcrypt.generate_password_hash(plaintext)

    def verify_password(self, plaintext):
        return bcrypt.check_password_hash(self.password_hash, plaintext)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


class Link(db.EmbeddedDocument):
    title = db.StringField(max_length=300)
    url = db.URLField()


class Comment(db.EmbeddedDocument):
    created = db.DateTimeField(default=datetime.now, required=True)
    content = db.StringField(max_length=500, required=True)
    author = db.ReferenceField(User)


class Tag(db.Document):
    name = db.StringField(max_length=50)
    slug = db.StringField(max_length=50)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        db.Document.save(self, *args, **kwargs)

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)


class Power(db.Document):
    name = db.StringField(max_length=50)
    url = db.URLField()
    slug = db.StringField(max_length=50)
    intro = db.StringField(max_length=500)
    img = db.StringField()
    links = db.ListField(db.EmbeddedDocumentField('Link'))
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))
    tags = db.ListField(db.ReferenceField(Tag))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        db.Document.save(self, *args, **kwargs)

    def __repr__(self):
        return '<Power: {}>'.format(self.name)


class Site(db.Document):
    name = db.StringField(max_length=50, required=True)
    url = db.URLField(required=True)
    intro = db.StringField(max_length=500)
    slug = db.StringField(max_length=50)
    img = db.StringField()
    last_edit = db.DateTimeField(default=datetime.now, required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))
    powers = db.ListField(db.ReferenceField(Power))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        db.Document.save(self, *args, **kwargs)

    def __repr__(self):
        return '<Site: {}>'.format(self.name)


class Feedback(db.Document):
    username = db.StringField(max_length=50)
    email = db.EmailField(max_length=50)
    content = db.StringField(max_length=500)
    created = db.DateTimeField(default=datetime.now, required=True)

    def __repr__(self):
        return '<Feedback: {}>'.format(self.username)
