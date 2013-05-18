#! /usr/bin/python
# coding: utf-8

import unittest
from connection import Connection


class TestConnection(unittest.TestCase):
    """
        Test class for the Connection class
        provide valid data to test
    """

    def setUp(self):
        self.con = Connection(
            login="login",
            password="password",
            url="https://painel2.virtualtarget.com.br/index.dma/")

    def test_authenticate(self):
        """
            Test if the user authenticated with the virtual target api,
            by simply consulting the webservice
        """
        data = self.con.get_datas()
        self.assertNotEquals(data, None)

    def test_add_contact(self):
        """Try to add a contact to the api"""
        self.con.add_contact(email="thiago.jose@intip.com.br",
                             nome="thiago",
                             lista_id=0)

    def test_add_contacts(self):
        """
            Try to add contacts according with the
            format specified in their api
        """
        self.con.add_contacts(
            dados=[{"listas": [1],
                    "campos": {"email": "thiago.jose@intip.com.br"}}])

    def test_get_contact(self):
        """
            Try to get a contact data,
            provide valid data
        """

        contact = self.con\
            .get_contact(email="thiago.jose@intip.com.br")
        self.assertEquals(contact, None)

    def test_add_list(self):
        """Try to add a list"""
        self.con.add_list(nome="lista de teste",
                          descricao="descricao lista")

    def test_create_campaign(self):
        """Try to create a campaign"""
        self.con.create_campaign(nome="nome campanha",
                                 descricao="descricao campanha")

    def test_create_sendmail(self):
        """Try to send mail to some contacts"""
        self.con\
            .create_sendmail(lista_id=0,
                             remetente_nome="thiago",
                             remetente_email="thiago.jose@intip.com.br",
                             remetente_reply="thiago.jose@intip.com.br",
                             assunto="teste sub", mensagem="teste mens",
                             datahora_programada="16/05/2013 00:24",
                             notificacao_email=False,
                             notificacao_sms=False)


#TODO: Add more tests
unittest.main()
