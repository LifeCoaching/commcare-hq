from casexml.apps.case.models import CommCareCase
from casexml.apps.case.sharedmodels import CommCareCaseIndex
from corehq.apps.commtrack.models import Product, CommtrackConfig,\
    CommtrackActionConfig, SupplyPointType
from corehq.apps.commtrack import const
from casexml.apps.case.tests.util import CaseBlock
from casexml.apps.case.xml import V2
import uuid
from corehq.apps.hqcase.utils import submit_case_blocks
from xml.etree import ElementTree

"""
helper code to populate the various commtrack models, for ease of
development/testing, before we have proper UIs and imports
"""

def get_commtrack_user_id(domain):
    # abstracted out in case we one day want to back this
    # by a real user, but for now it's like demo_user
    return const.COMMTRACK_USERNAME

def make_product(domain, name, code):
    p = Product()
    p.domain = domain
    p.name = name
    p.code = code.lower()
    p.save()
    return p

# TODO use case-xml case creation workflow
def make_supply_point(domain, location):
    # a supply point is currently just a case with a special type
    id = uuid.uuid4().hex
    caseblock = CaseBlock(
        case_id=id,
        create=True,
        version=V2,
        user_id=get_commtrack_user_id(domain),
        case_type=const.SUPPLY_POINT_CASE_TYPE,
    )
    casexml = ElementTree.tostring(caseblock.as_xml())
    submit_case_blocks(casexml, domain)
    c = CommCareCase.get(id)
    c.bind_to_location(location)
    c.save()
    return c

# TODO use case-xml case creation workflow
def make_supply_point_product(supply_point_case, product_uuid):
    pc = CommCareCase()
    pc.domain = supply_point_case.domain
    pc.type = const.SUPPLY_POINT_PRODUCT_CASE_TYPE
    pc.product = product_uuid
    ix = CommCareCaseIndex()
    ix.identifier = const.PARENT_CASE_REF
    ix.referenced_type = const.SUPPLY_POINT_CASE_TYPE
    ix.referenced_id = supply_point_case._id
    pc.indices = [ix]
    pc.location_ = supply_point_case.location_
    pc.save()
    return pc

def make_psi_config(domain):
    c = CommtrackConfig(
        domain=domain,
        multiaction_enabled=True,
        multiaction_keyword='s',
        actions=[
            CommtrackActionConfig(
                action_type='stockedoutfor',
                keyword='d',
                caption='Stock-out Days'
            ),
            CommtrackActionConfig(
                action_type='receipts',
                keyword='r',
                caption='Other Receipts'
            ),
            CommtrackActionConfig(
                action_type='stockonhand',
                keyword='b',
                caption='Balance'
            ),
            CommtrackActionConfig(
                action_type='receipts',
                name='sales',
                keyword='p',
                caption='Placements'
            ),
        ],
        supply_point_types=[
            SupplyPointType(name='CHC', categories=['Public']),
            SupplyPointType(name='PHC', categories=['Public']),
            SupplyPointType(name='SC', categories=['Public']),
            SupplyPointType(name='MBBS', categories=['Private']),
            SupplyPointType(name='Pediatrician', categories=['Private']),
            SupplyPointType(name='AYUSH', categories=['Private']),
            SupplyPointType(name='Medical Store / Chemist', categories=['Traditional']),
            SupplyPointType(name='RMP', categories=['Traditional']),
            SupplyPointType(name='Asha', categories=['Frontline Workers']),
            SupplyPointType(name='AWW', categories=['Public', 'Frontline Workers']),
            SupplyPointType(name='NGO', categories=['Non-traditional']),
            SupplyPointType(name='CBO', categories=['Non-traditional']),
            SupplyPointType(name='SHG', categories=['Non-traditional']),
            SupplyPointType(name='Pan Store', categories=['Traditional']),
            SupplyPointType(name='General Store', categories=['Traditional']),
        ]
    )
    c.save()
    return c

    
