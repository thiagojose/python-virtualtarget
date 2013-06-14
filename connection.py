#!/usr/bin/env python
#-*- coding:utf-8 -*-

from settings import LOGIN, PASSWORD, URL, DEBUG
from suds.client import Client
import suds
from time import strftime
if DEBUG:
    import logging
    logging.basicConfig(level=logging.INFO)


class Connection(object):
    """
    Starts a connection to
    the virtual target soap
    """

    def __init__(self, login=None, password=None, url=None):
        """
        instantiantes the connection class to connect to the api,
        creating an Proxy class according with the given url
        params:
            login: str - the user login for the integration service
            password: str - the password for the integration service
            url: str - acess url, should be the wsdl url for the service
        """
        self.login = login if login else LOGIN
        self.password = password if password else PASSWORD
        self.url = url if url else URL
        self.client = Client(self.url)

    def add_contact(self, email, nome, listas, nascimento="?",
                    celular="?", campos_adicionais=None):
        """
        Add a new contact to some list(s) to send emails
        params:
            email: str - email to add, acts as a identification key
            nome: str - name from the user to be added to the list
            listas: complex type - id for the lists to add the contact
            of int with the ids to add the user
            nascimento: str - born date in the format XX/XX/XXXX
            celular: str - cellphone in the format XXXXXXXXXXXXX
            campos_adicionais: list - containing any extra fields
        """
        # extra fields, not required
        campos_adicionais = campos_adicionais if campos_adicionais else []
        lists = []
        for id_ in listas:
            complex_type = self.client\
                .factory.create("AdicionaAtualizaContatoListasDados")
            complex_type.listaId = id_
            lists.append(complex_type)
        return self.client.service\
            .AdicionaAtualizaContato(login=self.login,
                                     senha=self.password,
                                     email=email,
                                     nome=nome,
                                     nascimento=nascimento,
                                     celular=celular,
                                     listas=lists,
                                     camposadicionais=campos_adicionais)

    def add_contacts(self, dados):
        """
        Add many contacts(limit 15 per request)
            params:
                dados: list - in the format
                [{'manterLista': True,
                  'listas': [1,2,3],
                  'campos': {'email': 'email', 'nome': 'nome'}}, ]
        """
        lists = []
        for data in dados:
            # create type needed to call the method
            complex_type = self.client\
                .factory.create("AdicionaAtualizaContatosContatosDados")

            complex_type.manterLista = data.get("manter_lista", True)
            listas = []
            # add lists
            for lista in data.get("listas", []):            
                lista_ = self.client.factory.create("AdicionaAtualizaContatoListasDados")
                lista_.listaId = lista
                listas.append(lista_)            
            complex_type.listas = listas
            # add fields
            campos = []
            for key, value in data.get("campos", {}).items():
                campos_ = self.client.factory.create("AdicionaAtualizaContatoCamposDados")
                campos_.tag = key
                campos_.valor = value
                campos.append(campos_)
            complex_type.campos = campos
            lists.append(complex_type)
        return self.client.service\
            .AdicionaAtualizaContatos(self.login,
                                      self.password,
                                      lists)

    def add_list(self, nome, descricao):
        """Add a new list to group contacts"""
        return self.client.service.CriaNovaLista(login=self.login,
                                                 senha=self.password,
                                                 nome=nome,
                                                 descricao=descricao)

    def add_campaign(self, nome, descricao):
        """Add a new campaign"""
        return self.client.service.CriaNovaCampanha(login=self.login,
                                                    senha=self.password,
                                                    nome=nome,
                                                    descricao=descricao)

    def create_sendmail(self, remetente_nome, remetente_email,
                        remetente_reply, assunto, mensagem, campanha_id=None,
                        datahora_programada=None, filtro=None,
                        notificacao_email=False, notificacao_sms=False):
        """
            Create a new email sending
            params:
                remetente_nome: str - the sender name
                remetente_emai: str - the sender email
                remetente_reply: str - the sender reply
                assunto: str - the message subject
                campanhaId: str - the campaign id to associate the email
                datahora_programada: str - date time in the format
                                           dd/mm/YYYY HH:MM
                notificacao_email: bool - send an email if action
                                          was sucessful
                notificacao_sms: bool - send an sms if action was sucessful
                fitro: complex type used to send the emails, can be any type,
                but by now it is used just the listaId parameter
        """
        campanha_id = campanha_id if campanha_id else "?"
        filters = []
        for id_ in filtro:
            complex_type = self.client\
                .factory.create("CriaNovoEnvioFiltroDados")
            complex_type.id = id_
            complex_type.campo = "listas"
            filters.append(complex_type)
        if not datahora_programada:
            datahora_programada = strftime("%d/%m/%Y %H:%M")
        response = None
        try:
            response = self.client.service.CriaNovoEnvio(
                login=self.login,
                senha=self.password,
                remetente_nome=remetente_nome,
                remetente_email=remetente_email,
                remetente_replay=remetente_reply,
                assunto=assunto,
                mensagem=mensagem,
                campanhaId=campanha_id,
                datahora_programada=datahora_programada,
                notificacao_email=notificacao_email,
                notificacao_sms=notificacao_sms,
                filtro=filters)
        except suds.WebFault as exception:
            response = exception
        return response

    def cancel_mailsending(self, envio_id):
        """
        Cancel an email sending if it hasn't
        been sended yet
        params:
            envio_id: str - the sending id to cancel
        """
        return self.client.service\
            .CancelarEnvio(login=self.login,
                           senha=self.password,
                           envioId=envio_id)

    def get_contact_history(self, email_contato):
        """
        Return the action from a determinated user
        params:
            email_contato: str - the email from the contact
        """
        return self.client.service\
            .RetornaHistoricoContato(contatoEmail=email_contato)

    def get_datas(self, function="RetornaListas"):
        """
        make an request according to the function name
        and return the data associated, just to get the
        data, because have no extra parameters, just the
        function name, possible function names:
        params values:
            RetornaListas, RetornaMotivosOptOut,
            RetornaQuantidadeListas, RetornaRegrasDicionario


        """
        return self.client.service.__getattr__(function)(self.login,
                                                         self.password)

    def get_contact(self, email):
        """
        Return the data associated with a contact
        params:
            email: str - the email from the contact
        """
        return self.client.service\
            .RetornaDadosContato(self.login, self.password, contatoEmail=email)

    def get_lists(self):
        """call the wsdl method RetornaListas"""
        return self.get_datas()

    def get_lists_qtde(self):
        """call the wsdl method RetornaQuantidadeListas"""
        return self.get_datas("RetornaQuantidadeListas")

    def get_output_reason(self):
        """call the wsdl method RetornaMotivosOptOut"""
        return self.get_datas("RetornaMotivosOptOut")

    def get_dict_rules(self):
        """call the wsdl method RetornaRegrasDicionario"""
        return self.get_datas("RetornaRegrasDicionario")
