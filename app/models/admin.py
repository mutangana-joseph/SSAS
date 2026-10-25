
class Admin:
    def __init__(self, admin_id, name, email, phone, password_hash):
        self.admin_id = admin_id
        self.name = name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
