class UserPrivilege:
    user_id = ''
    role = 0
    privileges =''
    all_privileges = {1:'Super Admin', 2:'Admin', 3:'Customer care', 4:'Sales Agent', 5:'User'}

    @classmethod
    def generate_user_role(cls, user_id):
        if user_id == 1:
            cls.user_id = user_id
            cls.role = 1
            cls.privileges = cls.all_privileges[cls.role]
        else:
            cls.user_id = user_id
            cls.role = 5
            cls.privileges = cls.all_privileges[cls.role]

    @classmethod
    def get_privileges(cls, user_id, role):
        cls.user_id = user_id
        cls.role = role
        cls.privileges = cls.all_privileges[cls.role]

    @classmethod
    def update_user_role(cls, user_id, role):
        try:
            cls.user_id = user_id
            cls.role = role
            cls.privileges = cls.all_privileges[cls.role]
        except:
            cls.user_id = user_id
            cls.role = 5
            cls.privileges = cls.all_privileges[cls.role]
