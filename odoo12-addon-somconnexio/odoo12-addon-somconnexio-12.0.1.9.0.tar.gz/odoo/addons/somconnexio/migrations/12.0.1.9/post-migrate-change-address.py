import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Update type column when temporary_change_address is true
    cr.execute('UPDATE broadband_isp_info SET type=\'location_change\' where temporary_change_address is true')  # noqa
    _logger.info('Update type column')
    # Drop temporary column
    cr.execute('ALTER TABLE broadband_isp_info DROP COLUMN temporary_change_address')
    _logger.info('Drop column temporary_change_address')
