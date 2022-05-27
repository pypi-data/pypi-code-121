# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class ProjectException(Exception):
    status_code = 500
    error_msg = ""

    def __init__(self, status_code=None, error_msg=None):
        if status_code:
            self.status_code = status_code
        if error_msg:
            self.error_msg = error_msg
        self.content = {
            "code": self.status_code,
            "error_msg": self.error_msg,
            "result": "",
        }

    def __str__(self):
        return self.error_msg

class ProjectNotFoundException(ProjectException):
    status_code = 404
    error_msg = "Project not found"
