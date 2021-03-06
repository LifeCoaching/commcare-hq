from datetime import datetime, timedelta
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumn
from corehq.apps.reports.filters.fixtures import AsyncLocationFilter
from corehq.apps.reports.generic import GenericTabularReport
from corehq.apps.reports.standard import CustomProjectReport, ProjectReportParametersMixin
from couchexport.models import Format
from custom.ilsgateway.filters import ILSDateFilter
from custom.ilsgateway.models import Alert
from custom.ilsgateway.tanzania import MonthQuarterYearMixin


class AlertReport(GenericTabularReport, CustomProjectReport, ProjectReportParametersMixin, MonthQuarterYearMixin):
    slug = 'alerts'
    fields = [AsyncLocationFilter, ILSDateFilter]
    name = 'Alerts'
    default_rows = 25
    exportable = True
    base_template = 'ilsgateway/base_template.html'

    @property
    def headers(self):
        return DataTablesHeader(*[DataTablesColumn('Alerts')])

    @property
    def rows(self):
        end_date = self.datespan.enddate
        alerts = Alert.objects.filter(
            location_id=self.request.GET.get('location_id', ''),
            date__lte=end_date,
            expires__lte=end_date
        ).order_by('-id')
        return alerts.values_list('text')

    @property
    def export_table(self):
        self.export_format_override = self.export_format_override = self.request.GET.get('format', Format.XLS)
        return super(AlertReport, self).export_table
