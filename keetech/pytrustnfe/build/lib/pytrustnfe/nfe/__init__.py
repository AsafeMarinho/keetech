# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
import hashlib
import binascii
from lxml import etree
from .comunicacao import executar_consulta
from .assinatura import Assinatura
from pytrustnfe.xml import render_xml, sanitize_response
from pytrustnfe.utils import CabecalhoSoap
from pytrustnfe.utils import gerar_chave, ChaveNFe
from pytrustnfe.Servidores import localizar_url, localizar_qrcode, localizar_url_nfce
from pytrustnfe.xml.validate import valida_nfe
from pytrustnfe.exceptions import NFeValidationException
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key

# Zeep
from requests import Session
from zeep import Client
from zeep.transports import Transport

def _build_header(method, **kwargs):
    action = {
        'NfeAutorizacao': ('NfeAutorizacao4', '4.00', 'NfeAutorizacaoLote'),
        'NfeRetAutorizacao': ('NfeRetAutorizacao4', '4.00', 'NfeRetAutorizacao/nfeRetAutorizacaoLote'),
        'NfeConsultaCadastro': ('CadConsultaCadastro4', '2.00', 'CadConsultaCadastro2/consultaCadastro2'),
        'NfeInutilizacao': ('NfeInutilizacao4', '4.00', 'NfeInutilizacao2/nfeInutilizacaoNF2'),
        'RecepcaoEventoCancelamento': ('RecepcaoEvento4', '4.00', 'RecepcaoEvento/nfeRecepcaoEvento'),
        'RecepcaoEventoCarta': ('RecepcaoEvento4', '4.00', 'RecepcaoEvento/nfeRecepcaoEvento'),
        'NFeDistribuicaoDFe': ('NFeDistribuicaoDFe/nfeDistDFeInteresse', '1.00', 'NFeDistribuicaoDFe/nfeDistDFeInteresse'),
        'RecepcaoEventoManifesto': ('RecepcaoEvento', '1.00', 'RecepcaoEvento/nfeRecepcaoEvento'),
    }
    vals = {
        'estado': kwargs['estado'],
        'method': action[method][0],
        'soap_action': action[method][2],
        'versao': action[method][1]
    }
    return CabecalhoSoap(**vals)


def _generate_nfe_id(**kwargs):
    for item in kwargs['NFes']:
        vals = {
            'cnpj': item['infNFe']['emit']['cnpj_cpf'],
            'estado': item['infNFe']['ide']['cUF'],
            'emissao': '%s%s' % (item['infNFe']['ide']['dhEmi'][2:4],
                                 item['infNFe']['ide']['dhEmi'][5:7]),
            'modelo': item['infNFe']['ide']['mod'],
            'serie': item['infNFe']['ide']['serie'],
            'numero': item['infNFe']['ide']['nNF'],
            'tipo': item['infNFe']['ide']['tpEmis'],
            'codigo': item['infNFe']['ide']['cNF'],
        }
        chave_nfe = ChaveNFe(**vals)
        chave_nfe = gerar_chave(chave_nfe, 'NFe')
        item['infNFe']['Id'] = chave_nfe
        item['infNFe']['ide']['cDV'] = chave_nfe[len(chave_nfe) - 1:]


def _add_required_node(elemTree):
    ns = elemTree.nsmap
    if None in ns:
        ns['ns'] = ns[None]
        ns.pop(None)

    prods = elemTree.findall('ns:NFe/ns:infNFe/ns:det/ns:prod', namespaces=ns)
    for prod in prods:
        element = prod.find('ns:cEAN', namespaces=ns)
        if element is None:
            cEan = etree.Element('cEAN')
            prod.insert(1, cEan)
        element = prod.find('ns:cEANTrib', namespaces=ns)
        if element is None:
            cEANTrib = etree.Element('cEANTrib')
            vProd = prod.find('ns:vProd', namespaces=ns)
            prod.insert(prod.index(vProd) + 1, cEANTrib)
    return elemTree


def _add_qrCode(xml, **kwargs):
    xml = etree.fromstring(xml)
    inf_nfe = kwargs['NFes'][0]['infNFe']
    nfe = xml.find(".//{http://www.portalfiscal.inf.br/nfe}NFe")
    infnfesupl = etree.Element('infNFeSupl')
    # Cria o nó qrCode no XML
    qrcode = etree.Element('qrCode')
    url_consulta = etree.Element('urlChave')
    # Busca a chave da NFe
    chave_nfe = inf_nfe['Id'][3:]
    # Versão do QR-Code
    versao = '100'
    # Tipo do Ambiente de Emissão
    ambiente = kwargs['ambiente']
    # Documento de Identificação do Cliente
    dest_cpf = None
    dest = nfe.find(".//{http://www.portalfiscal.inf.br/nfe}dest")

    if dest:
        dest_parent = dest.getparent()
        dest_parent.remove(dest)
    if inf_nfe.get('dest', False):
        if inf_nfe['dest'].get('CPF', False):
            dest_cpf = inf_nfe['dest']['CPF']
            dest = etree.Element('dest')
            cpf = etree.Element('CPF')
            cpf.text = dest_cpf
            dest.append(cpf)
            dest_parent.append(dest)
    # Data e Hora de emissão da NFC-e
    dh_emissao = inf_nfe['ide']['dhEmi'].encode()
    dh_emissao = base64.b16encode(dh_emissao).decode()
    # Valor Total da NFC-e
    valor_total = inf_nfe['total']['vNF']
    # Valor Total do ICMS
    icms_total = inf_nfe['total']['vICMS']
    # Digest Value
    dig_val = xml.find(".//{http://www.w3.org/2000/09/xmldsig#}DigestValue").text.encode()
    dig_val = base64.b16encode(dig_val).decode()
    # CID Token
    cid_token = kwargs['NFes'][0]['infNFe']['codigo_seguranca']['cid_token']
    # Código de Segurança do Contribuinte
    csc = kwargs['NFes'][0]['infNFe']['codigo_seguranca']['csc']

    # Geração do Hash QR-Code
    if dest_cpf == None:
        c_hash_QR_code = "chNFe={}&nVersao={}&tpAmb={}&dhEmi={}&vNF={}&vICMS={}&digVal={}&cIdToken={}{}"\
            .format(chave_nfe, versao, ambiente, dh_emissao.lower(),
               valor_total, icms_total, dig_val.lower(), cid_token, csc)

    else:
        c_hash_QR_code = "chNFe={}&nVersao={}&tpAmb={}&cDest={}&dhEmi={}&vNF={}&vICMS={}&digVal={}&cIdToken={}{}"\
                    .format(chave_nfe, versao, ambiente, dest_cpf, dh_emissao.lower(),\
                            valor_total, icms_total, dig_val.lower(), cid_token, csc)

    c_hash_QR_code = hashlib.sha1(c_hash_QR_code.encode()).digest()
    c_hash_QR_code = base64.b16encode(c_hash_QR_code).decode()

    # URL QR-Code
    if dest_cpf == None:
        QR_code_url = "?chNFe={}&nVersao={}&tpAmb={}&dhEmi={}&vNF={}&vICMS={}&digVal={}&cIdToken={}&cHashQRCode={}"\
            .format(chave_nfe, versao, ambiente, dh_emissao.lower(), valor_total,\
                    icms_total, dig_val.lower(), cid_token, c_hash_QR_code.upper())
    else:
        QR_code_url = "?chNFe={}&nVersao={}&tpAmb={}&cDest={}&dhEmi={}&vNF={}&vICMS={}&digVal={}&cIdToken={}&cHashQRCode={}"\
                  .format(chave_nfe, versao, ambiente, dest_cpf, dh_emissao.lower(),\
                                 valor_total, icms_total, dig_val.lower(), cid_token, c_hash_QR_code.upper())

    qr_code_server = localizar_qrcode(kwargs['estado'], ambiente)
    url_consulta_nfce = localizar_url_nfce(kwargs['estado'], ambiente)
    qrcode_text = qr_code_server + QR_code_url
    qrcode.text = etree.CDATA(qrcode_text)
    url_consulta.text = url_consulta_nfce
    infnfesupl.append(qrcode)
    infnfesupl.append(url_consulta)
    nfe.insert(1, infnfesupl)
    return etree.tostring(xml, encoding=str)

def _render(certificado, method, sign, **kwargs):
    path = os.path.join(os.path.dirname(__file__), 'templates')
    xmlElem_send = render_xml(path, '%s.xml' % method, True, **kwargs)

    modelo = xmlElem_send.find(".//{http://www.portalfiscal.inf.br/nfe}mod")
    modelo = modelo.text if modelo is not None else '55'

    if sign:
        # Caso for autorização temos que adicionar algumas tags tipo
        # cEan, cEANTrib porque o governo sempre complica e não segue padrão
        if method == 'NfeAutorizacao':
            xmlElem_send = _add_required_node(xmlElem_send)

        signer = Assinatura(certificado.pfx, certificado.password)
        if method == 'NfeInutilizacao':
            xml_send = signer.assina_xml(xmlElem_send, kwargs['obj']['id'])
        if method == 'NfeAutorizacao':
            xml_send = signer.assina_xml(xmlElem_send, kwargs['NFes'][0]['infNFe']['Id'])
            if modelo == '65':
                xml_send = _add_qrCode(xml_send, **kwargs)
            if 'validate' in kwargs:
                erros = valida_nfe(xml_send)
                if erros:
                    raise NFeValidationException('Erro ao validar NFe', erros=erros, sent_xml=xml_send)
        elif method == 'RecepcaoEventoCancelamento':
            xml_send = signer.assina_xml(xmlElem_send, kwargs['eventos'][0]['Id'])

        if method == 'RecepcaoEvento':
            xml_send = signer.assina_xml(xmlElem_send, kwargs['eventos'][0]['Id'])
        elif method == 'RecepcaoEventoManifesto':
            xml_send = signer.assina_xml(xmlElem_send, kwargs['manifesto']['identificador'])

    else:
        xml_send = etree.tostring(xmlElem_send, encoding=str)

    return xml_send


def _send(certificado, method, **kwargs):
    xml_send = kwargs["xml"]
    url = localizar_url(method,  kwargs['estado'], kwargs['modelo'], kwargs['ambiente'])

    if method == 'RecepcaoEventoManifesto':
        url = 'https://www.nfe.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx'

    # Não há mais necessidade de usar o cabeçalho SOAP
    # cabecalho = _build_header(method, **kwargs)

    send_raw = False
    if method == 'NFeDistribuicaoDFe':
        send_raw = True

    response, obj = executar_consulta(certificado, url, method, xml_send, send_raw=send_raw)

    return {
        'sent_xml': xml_send,
        'received_xml': response.decode(),
        'object': obj
    }

def xml_autorizar_nfe(certificado, **kwargs):
    _generate_nfe_id(**kwargs)
    return _render(certificado, 'NfeAutorizacao', True, **kwargs)

def autorizar_nfe(certificado, **kwargs):  # Assinar
    if "xml" not in kwargs:
        kwargs['xml'] = xml_autorizar_nfe(certificado, **kwargs)
    return _send(certificado, 'NfeAutorizacao', **kwargs)

def xml_retorno_autorizar_nfe(certificado, **kwargs):
    return _render(certificado, 'NfeRetAutorizacao', False, **kwargs)

def retorno_autorizar_nfe(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_retorno_autorizar_nfe(certificado, **kwargs)
    return _send(certificado, 'NfeRetAutorizacao', **kwargs)

def xml_recepcao_evento_cancelamento(certificado, **kwargs):  # Assinar
    return _render(certificado, 'RecepcaoEventoCancelamento', True, **kwargs)

def recepcao_evento_cancelamento(certificado, **kwargs):  # Assinar
    if "xml" not in kwargs:
        kwargs['xml'] = xml_recepcao_evento_cancelamento(certificado, **kwargs)
    return _send(certificado, 'RecepcaoEventoCancelamento', **kwargs)

def xml_inutilizar_nfe(certificado, **kwargs):
    return _render(certificado, 'NfeInutilizacao', True, **kwargs)

def inutilizar_nfe(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_inutilizar_nfe(certificado, **kwargs)
    return _send(certificado, 'NfeInutilizacao', **kwargs)

def xml_consultar_protocolo_nfe(certificado, **kwargs):
    return _render(certificado, 'NfeConsultaProtocolo', True, **kwargs)

def consultar_protocolo_nfe(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_consultar_protocolo_nfe(certificado, **kwargs)
    return _send(certificado, 'NfeConsultaProtocolo', **kwargs)

def xml_nfe_status_servico(certificado, **kwargs):
    return _render(certificado, 'NfeStatusServico', False, **kwargs)


def nfe_status_servico(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_nfe_status_servico(certificado, **kwargs)
    return _send(certificado, 'NfeStatusServico', **kwargs)

def xml_consulta_cadastro(certificado, **kwargs):
    return _render(certificado, 'NfeConsultaCadastro', False, **kwargs)

def consulta_cadastro(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_consulta_cadastro(certificado, **kwargs)
        kwargs['modelo'] = '55'
    return _send(certificado, 'NfeConsultaCadastro', **kwargs)

def xml_recepcao_evento_carta_correcao(certificado, **kwargs):  # Assinar
    return _render(certificado, 'RecepcaoEvento', True, **kwargs)

def recepcao_evento_carta_correcao(certificado, **kwargs):  # Assinar
    if "xml" not in kwargs:
        kwargs['xml'] = xml_recepcao_evento_carta_correcao(certificado, **kwargs)
    return _send(certificado, 'RecepcaoEvento', **kwargs)

def xml_recepcao_evento_manifesto(certificado, **kwargs):  # Assinar
    return _render(certificado, 'RecepcaoEventoManifesto', True, **kwargs)

def recepcao_evento_manifesto(certificado, **kwargs):  # Assinar
    if "xml" not in kwargs:
        kwargs['xml'] = xml_recepcao_evento_manifesto(certificado, **kwargs)

    xml_send = kwargs["xml"]
    base_url = localizar_url('RecepcaoEventoManifesto', kwargs['estado'], kwargs['modelo'], kwargs['ambiente'])
    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)

    session = Session()
    session.cert = (cert, key)
    session.verify = False
    transport = Transport(session=session)

    xml = etree.fromstring(xml_send)
    xml_um = etree.fromstring(
        '<nfeCabecMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/"><cUF>AN</cUF><versaoDados>1.00</versaoDados></nfeCabecMsg>')
    client = Client(base_url, transport=transport)

    port = next(iter(client.wsdl.port_types))
    first_operation = [x for x in iter(
        client.wsdl.port_types[port].operations) if "Zip" not in x][0]

    with client.settings(raw_response=True):
        response = client.service[first_operation](xml).text
        response, obj = sanitize_response(response.encode())
        return {
            'sent_xml': xml_send,
            'received_xml': response.decode(),
            'object': obj
        }

    #return _send(certificado, 'RecepcaoEventoManifesto', **kwargs)

def xml_recepcao_evento_epec(certificado, **kwargs):  # Assinar
    return _render(certificado, 'RecepcaoEventoEPEC', True, **kwargs)

def recepcao_evento_epec(certificado, **kwargs):  # Assinar
    if "xml" not in kwargs:
        kwargs['xml'] = xml_recepcao_evento_epec(certificado, **kwargs)
    return _send(certificado, 'RecepcaoEventoEPEC', **kwargs)

def xml_consulta_distribuicao_nfe(certificado, **kwargs):  # Assinar
    return _render(certificado, 'NFeDistribuicaoDFe', False, **kwargs)

def consulta_distribuicao_nfe(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_consulta_distribuicao_nfe(certificado, **kwargs)
    xml_send = kwargs["xml"]
    base_url = localizar_url('NFeDistribuicaoDFe', kwargs['estado'], kwargs['modelo'], kwargs['ambiente'])
    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)

    session = Session()
    session.cert = (cert, key)
    session.verify = False
    transport = Transport(session=session)

    xml = etree.fromstring(xml_send)
    xml_um = etree.fromstring(
        '<nfeCabecMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe"><cUF>AN</cUF><versaoDados>1.00</versaoDados></nfeCabecMsg>')
    client = Client(base_url, transport=transport)

    port = next(iter(client.wsdl.port_types))
    first_operation = [x for x in iter(client.wsdl.port_types[port].operations) if "Zip" not in x][0]
    with client.settings(raw_response=True):
        response = client.service[first_operation](nfeDadosMsg=xml, _soapheaders=[xml_um]).text
        response, obj = sanitize_response(response.encode())
        return {
            'sent_xml': xml_send,
            'received_xml': response.decode(),
            'object': obj
        }

def xml_download_nfe(certificado, **kwargs):  # Assinar
    return _render(certificado, 'NFeDistribuicaoDFe', False, **kwargs)

def download_nfe(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs['xml'] = xml_download_nfe(certificado, **kwargs)
    return _send(certificado, 'NFeDistribuicaoDFe', **kwargs)