from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import validators
from django.db import models
from django.utils import timezone
import re

class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser,
                     **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username,
                          email=email,
                          is_staff=is_staff,
                          is_active=True,
                          is_superuser=is_superuser,
                          last_login=now,
                          date_joined=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True,
                                 **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('username',
                                max_length=20,
                                unique=True,
                                help_text="Required. 15 characters or fewer." +
                                "Letters, numbers and @/./+/-/_ characters",
                                validators=[
                                    validators.RegexValidator(
                                        re.compile(r'^[\w.@+-]+$'),
                                        'Enter a valid username.', 'invalid')])

    first_name = models.CharField('Nome', max_length=35)
    last_name = models.CharField('Sobrenome', max_length=30)
    email = models.EmailField('Endereço de email', max_length=255, unique=True)

    is_staff = models.BooleanField('staff status', default=False, help_text=
        'Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True, help_text=
        'Designates whether this user should be treated as active. ' + 
        'Unselect this instead of deleting accounts.')

    date_joined = models.DateTimeField('date joined', default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

class Administrador(models.Model):
    """
    Child class of User, called Administrador. The Administrator team is
    responsable for the administration of lanterna-verde app.
    """
    DIRETOR = 'DR'
    GERENTE = 'GR'
    ROLE_CHOICES = [
        (DIRETOR, 'Diretor'),
        (GERENTE, 'Gerente')
    ]
    role = models.CharField(
        max_length=2,
        choices=ROLE_CHOICES,
        default=GERENTE
    )
    user = models.OneToOneField(Usuario,
                                primary_key=True,
                                on_delete=models.CASCADE)

    class Meta:
        """database metadata"""
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

class Analista(models.Model):
    available = models.BooleanField('Disponivel', default=True)
    cpf = models.CharField('CPF', max_length=11)
    specialty = models.CharField('Especialidade', max_length=255)
    analysis = models.PositiveIntegerField('Analises', default=0)

    user = models.OneToOneField(Usuario,
                                primary_key=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'analista'
        verbose_name_plural = 'analistas'
    def __str__(self):
        return self.user.username

class Empresa(models.Model):
    NOPACK = 'P1'
    MONTHLY = 'P2'
    BIANNUAL = 'P3'
    YEARLY = 'P4'

    T1 ='Primeiro Setor'
    T2 = 'Segundo Setor'
    T3 = 'Terceiro Setor'

    TYPE = [
        (T1, 'Primeiro Setor'),
        (T2, 'Segundo Setor'),
        (T3, 'Terceiro Setor')
    ]
    PACKAGE = [
        (NOPACK, 'Nenhum pacote assinado')
        (MONTHLY, 'Mensal'),
        (BIANNUAL, 'Semestral'),
        (YEARLY, 'Anual')
    ]

    tradeName = models.CharField('Nome Fantasia', max_length=100)
    corporateName = models.CharField('Razão Social', max_length=100)
    stateRegistration = models.CharField('Inscrição Estadual', max_length=9)
    cnpj = models.CharField('CNPJ', max_length=14, unique=True)
    tipo = models.CharField(choices=TYPE, max_length=100)
    phoneNumber = models.CharField('Telefone', max_length=12)
    package = models.CharField(choices=PACKAGE, max_length=100, default=NOPACK)

    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'
    def __str__(self):
        return self.tradeName

class Pergunta(models.Model):
    """
    Pergunta are questions about the GAS questionary used by Analists to review
    a greenwashing performance of a Company/Product.
    """
    D1 = 'D1'
    D2 = 'D2'
    D3 = 'D3'
    D4 = 'D4'
    DIMENSIONS_CHOICES = [
        (D1, 'D1'),
        (D2, 'D2'),
        (D3, 'D3'),
        (D4, 'D4')
    ]
    dimension = models.CharField(
        max_length=2,
        choices=DIMENSIONS_CHOICES,
        default=D1
    )
    body = models.CharField(max_length=255)

    class Meta:
        """database metadata"""
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        
    def __str__(self):
        return self.body

class SolicitacaoAnalise(models.Model):
    """
    SolicitacaoAnalise is when a company requisits to lanterna verde a
    professional analysis from a team of Analists. Administrators will evaluate
    each `SolicitacaoAnalise` in order to create a new Analysis.
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    date = models.DateTimeField('Data de solicitação', default=timezone.now)
    reanalysis = models.BooleanField(default=True)

    class Meta:
        """SolicitacaoeAnalise metadata"""
        verbose_name = "Solicitação de Análise"
        verbose_name_plural = "Solicitações de Analise"

class SolicitacaoReanalise(models.Model):
    analysisRequest = models.OneToOneField(SolicitacaoAnalise, primary_key=True, on_delete=models.CASCADE)
    reanalysis = models.BooleanField(default=False, editable=False)
    
    class Meta:
        verbose_name = "Solicitação de Reanálise"
        verbose_name_plural = "Solicitações de Reanalise"

class AvaliacaoAnalista(models.Model):
    analyst = models.ForeignKey(Analista, related_name='analises', on_delete=models.CASCADE)
    company = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    comment = models.TextField(blank=True)
    finished = models.BooleanField(default=False)
    requirement_date = models.DateTimeField("Data da Solicitação de Análise",
                                            default=timezone.now)
    update_date = models.DateTimeField(auto_now=True)
    reanalyzed = models.BooleanField(default=False)

    def __str__(self):
        return self.analyst.user.username + ' -> ' + self.company.tradeName


class Questao(models.Model):
    question = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    answer = models.BooleanField(default=False)
    questionnaire = models.ForeignKey(AvaliacaoAnalista, on_delete=models.CASCADE)

    class Meta:
        """database metadata"""
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

