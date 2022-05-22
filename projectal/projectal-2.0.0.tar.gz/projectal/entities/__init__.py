"""
Implementations of all Projectal entities.

All classes here inherit from `projectal.entity.Entity`.
"""

from projectal.entities.project import Project
from projectal.entities.task import Task
from projectal.entities.access_policy import AccessPolicy
from projectal.entities.calendar import Calendar
from projectal.entities.company import Company
from projectal.entities.contact import Contact
from projectal.entities.customer import Customer
from projectal.entities.department import Department
from projectal.entities.file import File
from projectal.entities.folder import Folder
from projectal.entities.location import Location
from projectal.entities.note import Note
from projectal.entities.project_template import ProjectTemplate
from projectal.entities.rebate import Rebate
from projectal.entities.resource import Resource
from projectal.entities.skill import Skill
from projectal.entities.staff import Staff
from projectal.entities.stage import Stage
from projectal.entities.task_template import TaskTemplate
from projectal.entities.user import User
from projectal.entities.webhook import Webhook
