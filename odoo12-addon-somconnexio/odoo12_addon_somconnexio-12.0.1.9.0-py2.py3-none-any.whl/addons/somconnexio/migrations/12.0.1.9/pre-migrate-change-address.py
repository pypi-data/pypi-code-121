import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Add temporary credit product column
    cr.execute('ALTER TABLE broadband_isp_info ADD temporary_change_address boolean')
    _logger.info('New column temporary_change_address created.')
    # Copy broadband_isp_info.change_address to
    # broadband_isp_info.temporary_change_address
    cr.execute('SELECT id,change_address from broadband_isp_info')
    _logger.info('broadband_isp_info.change_address copied to broadband_isp_info.temporary_change_address')  # noqa
    broadband_isp_infos = cr.fetchall()
    for broadband_isp_info in broadband_isp_infos:
        id = broadband_isp_info[0]
        change_address = broadband_isp_info[1] or False
        cr.execute(('UPDATE broadband_isp_info SET temporary_change_address={} WHERE id={}').format(change_address, id))  # noqa
