from database.vkinder_db import add_favorite_to_db, add_photo_to_db, get_favorites, add_user_to_blacklist


class VkUser:
    user_dict = {}

    def __init__(self, user_id, gender, city):
        """
        :param user_id: user id
        :param gender: gender
        :param city: city
        """
        self.user_id = user_id
        self.gender = gender
        self.city = city
        self.age_from = None
        self.age_to = None
        self.option_list = []
        self.current_option = None 
        self.current_user_foto = []
        self.offset = 0

    def extend_option_list(self, options: list):
        """
        Adds more options to self.option_list
        :param options: list of new options
        :return:
        """   
        self.option_list.extend(options) 

    def next_option(self) -> list:
        """
        Gives next option.
        :return: option
        """
        self.current_option = self.option_list.pop()
        return self.current_option

    def add_favorite(self):
        """
        Adds option to favorites
        """
        add_favorite_to_db(self.current_option.id, self.user_id, self.current_option.first_name, self.current_option.last_name)
        add_photo_to_db(self.current_user_foto, self.current_option.id) 

    def show_favorites(self) -> str:
        """
        Shows list of favorites options
        """
        favorites = get_favorites(self.user_id)
        favorites = '\n'.join(['vk.com/id' + str(favorite[0]) + ' ' + favorite[1] + ' ' + favorite[2] for favorite in favorites])
        return favorites

    def block_option(self):
        """
        Adds option to blacklist.
        """
        add_user_to_blacklist(self.current_option.id, self.user_id)
