from django.db import models

from django.contrib.auth.models import AbstractUser, UserManager 
from django.utils.translation import gettext_lazy as _

from core.services.managers import ActiveManager





class User(AbstractUser):
    """
    Custom user model where email is not required.
    Username, password, first_name, last_name, and user_type are required.
    """
    
    class UserType(models.TextChoices):
        ADMIN = 'Manager', _('Manager')
        OPERATOR = 'Employee', _('Employee')
    email = models.EmailField(_('email address'), blank=True, unique=False)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    user_type = models.CharField(
        _("User Type"),
        max_length=15,
        choices=UserType.choices,
        default=UserType.ADMIN,
        help_text=_("Select the type of user."),
    )
    manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees',
        verbose_name=_("Manager"),
        limit_choices_to={'user_type': 'Manager'}, 
        help_text=_("The manager of this employee."))
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck this to 'freeze' or 'soft delete' the item. It will not be available for new operations.")
    )
    objects = UserManager()   
    active = ActiveManager() 


    REQUIRED_FIELDS = [ 'first_name', 'last_name']
    
    @property
    def full_name(self):
        "Returns the person's full name."
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.username

    class Meta: 
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['username']


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(blank=True, null=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck this to 'freeze' or 'soft delete' the item. It will not be available for new operations.")
    )
    objects = models.Manager() 
    active = ActiveManager()



    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        ordering = ['name']


class Beneficiary(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(blank=True, null=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck this to 'freeze' or 'soft delete' the item. It will not be available for new operations.")
    )
    objects = models.Manager() 
    active = ActiveManager()



    def __str__(self):
        return self.name

    class Meta: 
        verbose_name = _("Beneficiary")
        verbose_name_plural = _("Beneficiaries")
        ordering = ['name']
