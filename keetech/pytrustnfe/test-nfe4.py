from pytrustnfe.nfe import xml_autorizar_nfe
from pytrustnfe.certificado import Certificado
from pytrustnfe.nfe import autorizar_nfe
from pytrustnfe.nfe import retorno_autorizar_nfe
from pytrustnfe.utils import ChaveNFe, gerar_chave, gerar_nfeproc
from pytrustnfe.xml.validate import valida_nfe


from datetime import datetime
import base64, os

caminho = os.path.dirname(__file__)
certificado = open(os.path.join(caminho, 'certificado.pfx'), 'rb').read()
certificado = Certificado(certificado, '12035413')

data_emissao = datetime.now()

def _prepare_eletronic_invoice_values():

    ide = {
        'cUF': '13',
        'cNF': '95959595',
        'natOp': 'VENDA',
        'indPag': '1',
        'mod': '55',
        'serie': '100',
        'nNF': '1',
        'dhEmi': data_emissao.strftime('%Y-%m-%dT%H:%M:%S-00:00'),
        'dhSaiEnt': data_emissao.strftime('%Y-%m-%dT%H:%M:%S-00:00'),
        'tpNF': '1',
        'idDest': 1,
        'cMunFG': '1302603',
        # Formato de Impressão do DANFE - 1 - Danfe Retrato, 4 - Danfe NFCe
        'tpImp': '1',
        'tpEmis': 1,
        'tpAmb': 2,
        'finNFe': 1,
        'indFinal': '1',
        'indPres': '1',
        'procEmi': 0,
    }

    emit = {
        'tipo': 'company',
        'cnpj_cpf': '21673208000141',
        'xNome': 'GEORGE VENANCIO MARTINS SOBRINHO - ME',
        'xFant': 'Pool Life Atacado',
        'enderEmit': {
            'xLgr': 'Avenida Coronel Teixeira',
            'nro': '6553',
            'xBairro': 'Ponta Negra',
            'cMun': '1302603',
            'xMun': 'Manaus',
            'UF': 'AM',
            'CEP': '69037000',
            'cPais': '1058',
            'xPais': 'Brasil',
            'fone': '9230268166'
        },
        'IE': '053718283',
        'CRT': '1',
    }
    dest = {
        'tipo': 'company',
        'cnpj_cpf': '04165072000140',
        'xNome': u'NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL',
        'enderDest': {
            'xLgr': 'AV CONSTANTINO NERY',
            'nro': '2237',
            'xBairro': 'CHAPADA',
            'cMun': '1302603',
            'xMun': 'Manaus',
            'UF': 'AM',
            'CEP': '69050001',
            'cPais': '1058',
            'xPais': 'Brasil',
            'fone': ''
        },
        'indIEDest': '9',
        'IE': '',
    }

    eletronic_items = []

    prod = {
        'cProd': '000024',
        'cEAN': '7896544402133',
        'xProd': 'NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO -\
SEM VALOR FISCAL',
        'NCM': '38089419',
        'EXTIPI': '',
        'CFOP': '5102',
        'uCom': 'BD 10K',
        'qCom': 2,
        'vUnCom': '145.00',
        'vProd':  '290.00',
        'cEANTrib': '7896544402133',
        'uTrib': 'BD 10K',
        'qTrib': 2,
        'vUnTrib': '145.00',
        'vFrete': '',
        'vSeg': '',
        'vDesc': '',
        'vOutro': '',
        'indTot': 1,
        'cfop': '5102',
        'CEST': '',
        'nItemPed': '',
    }

    imposto = {
        'vTotTrib': '0.00',
        'ICMS': {
            'orig':  '0',
            'CST': '102',
            'modBC': '3',
            'vBC': '0',
            'pRedBC': '0.00',
            'pICMS': '0.00',
            'vICMS': '0.00',
            'modBCST': '4',
            'pMVAST': '0.00',
            'pRedBCST': '0.00',
            'vBCST': '0.00',
            'pICMSST': '0.00',
            'vICMSST': '0.00',
            'pCredSN': '0.00',
            'vCredICMSSN': '0.00',
        },
        'IPI': {
            'clEnq': '',
            'cEnq': '999',
            'CST': '99',
            'vBC': '0.00',
            'pIPI': '0.00',
            'vIPI': '0.00',
        },
        'PIS': {
            'CST': '49',
            'vBC': '0.00',
            'pPIS': '0.00',
            'vPIS': '0.00',
        },
        'COFINS': {
            'CST': '49',
            'vBC': '0.00',
            'pCOFINS': '0.00',
            'vCOFINS': '0.00',
        },
    }
    
    eletronic_items.append({'prod': prod, 'imposto': imposto, 'infAdProd': ''})
    
    total = {
        'vBC': '0.00',
        'vICMS': '0.00',
        'vICMSDeson': '0.00',
        #novos campos obrigatórios incluir no odoo
        'vFCP': '0.00',
        'vFCPST': '0.00',
        'vFCPSTRet': '0.00',
        'vIPIDevol': '0.00',


        'vBCST': '0.00',
        'vST': '0.00',
        'vProd': '290.00',
        'vFrete': '0.00',
        'vSeg': '0.00',
        'vDesc': '0.00',
        'vII': '0.00',
        'vIPI': '0.00',
        'vPIS': '0.00',
        'vCOFINS': '0.00',
        'vOutro': '0.00',
        'vNF': '290.00',
        'vFCPUFDest': '0.00',
        'vICMSUFDest': '0.00',
        'vICMSUFRemet': '0.00',
        'vTotTrib': '0.00',
        'vServ': '0.00',
    }

    infAdic = {
        'infCpl': '',
        'infAdFisco':'',
    }
    
    transp = {
        'modFrete': '9',
        'transporta': {
            'xNome': '',
            'IE': '',
            'xEnder': '',
            'xMun': '',
            'UF': ''
        },
        'veicTransp': {
            'placa': '',
            'UF': '',
            'RNTC': '',
        }
    }

    duplicatas = []
    duplicatas.append({
        'nDup': '000001',
        'dVenc':  '2018-09-01',
        'vDup': '290.00',
    })
    cobr = {
        'fat': {
            'nFat': '',
            'vOrig': '290.00',
            'vDesc': '',
            'vLiq': '290.00',
        },
        'dup': duplicatas
    }
    # Incluir Dicionário Obrigatório
    pag = {
        'indPag': '1',
        'tPag': '99',
        'vPag': '290.00',
    }

    vals = {
        'Id': '',
        'ide': ide,
        'emit': emit,
        'dest': dest,
        #'autXML': autorizados,
        'detalhes': eletronic_items,
        'total': total,
        'transp': transp,
        'infAdic': infAdic,
        'cobr': cobr,
        #campo obrigatório
        'pag': pag,
    }

    return vals

def _prepare_lote():

    return {
        'idLote': 1001,
        'indSinc': 0,
        'estado': 13,
        'ambiente': 2,
        'NFes': [{
            'infNFe': _prepare_eletronic_invoice_values()
        }],
        'modelo': '55',
    }


lote = _prepare_lote()
print(lote)

# Funções Para Gerar e Assinar o XML
xml_enviar = xml_autorizar_nfe(certificado, **lote)
mensagens_erro = valida_nfe(xml_enviar)
if mensagens_erro:
    print(mensagens_erro)
print(xml_enviar)

#xml_to_send = base64.encodestring(xml_enviar.encode('utf-8'))

#Funções para Envio do XML
estado = '15'
resposta_recibo = None
resposta = autorizar_nfe(certificado, xml=xml_enviar, estado='13', ambiente=2, modelo='55')
#import pudb;pu.db

# Elemento Alterado
retorno = resposta['object'].Body.nfeResultMsg
retorno = retorno.getchildren()[0]
if retorno.cStat == 103:
    obj = {
        'estado': estado,
        'ambiente': 2,
        'obj': {
            'ambiente': 2,
            'numero_recibo': retorno.infRec.nRec
        }
    }
    recibo_nfe = obj['obj']['numero_recibo']
    import time
    while True:
        time.sleep(2)
        resposta_recibo = retorno_autorizar_nfe(certificado, modelo='55', **obj)
        import pudb;pu.db
        retorno = resposta_recibo['object'].Body.\
            nfeRetAutorizacaoLoteResult.retConsReciNFe
        if retorno.cStat != 105:
            break

msg_retorno = None

if retorno.cStat != 104:
    codigo_retorno = retorno.cStat
    mensagem_retorno = retorno.xMotivo
else:
    codigo_retorno = retorno.protNFe.infProt.cStat
    mensagem_retorno = retorno.protNFe.infProt.xMotivo
    if codigo_retorno == '100':
        msg_retorno = {
            'state': 'done', 'nfe_exception': False,
            'protocolo_nfe': retorno.protNFe.infProt.nProt,
            'data_autorizacao': retorno.protNFe.infProt.dhRecbto}
    # Duplicidade de NF-e significa que a nota já está emitida
    # TODO Buscar o protocolo de autorização, por hora só finalizar
    if codigo_retorno == '204':
        msg_retorno = {'state': 'done', 'codigo_retorno': '100',
                'nfe_exception': False,
                'mensagem_retorno': 'Autorizado o uso da NF-e'}

    # Denegada e nota já está denegada
    if codigo_retorno in ('302', '205'):
        msg_retorno = {'state': 'denied',
                    'nfe_exception': True}

recibo_xml = resposta['received_xml']

if msg_retorno:
    print(msg_retorno)
print(recibo_xml)
print(retorno.cStat)
print(codigo_retorno)

print(resposta)