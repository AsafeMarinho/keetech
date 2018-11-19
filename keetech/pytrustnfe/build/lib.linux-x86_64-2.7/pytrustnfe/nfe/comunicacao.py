# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pytrustnfe.client import HttpClient
from pytrustnfe.certificado import save_cert_key, extract_cert_and_key_from_pfx

from ..xml import sanitize_response

# SOAP Flags
NS_NFE = 'http://www.portalfiscal.inf.br/nfe'
NS_SIG = 'http://www.w3.org/2000/09/xmldsig#'
NS_SOAP = 'http://www.w3.org/2003/05/soap-envelope'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_XSD = 'http://www.w3.org/2001/XMLSchema'
NS_MET = 'http://www.portalfiscal.inf.br/nfe/wsdl/'

NS_SOAP_NFSE = 'http://schemas.xmlsoap.org/soap/envelope/'
NS_BETHA = 'http://www.betha.com.br/e-nota-contribuinte-ws'
VERSAO_PADRAO = '4.00'
VERSAO_QRCODE = '100'

# Metodos
metodos = {
    'NfeAutorizacao': 'NFeAutorizacao4',
    'NfeRetAutorizacao': 'NFeRetAutorizacao4',
    'NfeConsultaCadastro': 'CadConsultaCadastro4',
    'NfeInutilizacao': 'NFeInutilizacao4',
    'RecepcaoEventoCancelamento': 'NFeRecepcaoEvento4',
    'RecepcaoEventoCarta': 'NFeRecepcaoEvento4',
    'NFeDistribuicaoDFe': 'NFeDistribuicaoDFe/nfeDistDFeInteresse',
    'RecepcaoEventoManifesto': 'RecepcaoEvento',
}

def _soap_xml(body, method):
    xml = '<?xml version="1.0" encoding="utf-8"?>'
    xml += '<soap:Envelope xmlns:soap="%s">' % (NS_SOAP)
    xml += '<soap:Body>'
    xml += '<nfeDadosMsg xmlns="%s">' % (NS_MET + metodos[method])
    xml += body
    xml += '</nfeDadosMsg></soap:Body>'
    xml += '</soap:Envelope>'
    return xml.rstrip('\n')

def _post_header(method):
    """Retorna um dicionário com os atributos para o cabeçalho da requisição HTTP"""
    if method != 'NFeDistribuicaoDFe':
        response = {
            'content-type': 'application/soap+xml; charset=utf-8;',
            'Accept': 'application/soap+xml; charset=utf-8;',
            #'SOAPAction': "", # Requisitado em alguns webservices
            }
    else:
        response = {
            'Content-type': 'text/xml; charset=utf-8;',
            'SOAPAction': "http://www.portalfiscal.inf.br/nfe/wsdl/%s" % metodos[method],
            'Accept': 'application/soap+xml; charset=utf-8',
        }

    return response


def executar_consulta(certificado, url, method, xmlEnviar, send_raw=False):
    cert, key = extract_cert_and_key_from_pfx(
        certificado.pfx, certificado.password)
    cert_path, key_path = save_cert_key(cert, key)
    client = HttpClient(url, cert_path, key_path)
    xml_enviar = _soap_xml(xmlEnviar, method)

    if send_raw:
        xml = '<?xml version="1.0" encoding="utf-8"?>' + xmlEnviar.rstrip('\n')
        xml_enviar = xml
    xml_retorno = client.post_soap(xml_enviar, _post_header(method), send_raw)
    return sanitize_response(xml_retorno.encode())