# @Author:WY
# @Time:2020/2/1116:07

from wtforms import Form


class BaseForm(Form):
    def get_error(self):
        # print("type(self.errors):",type(self.errors))
        # print("self.errors:", self.errors)
        message = self.errors.popitem()[1][0]
        return message
