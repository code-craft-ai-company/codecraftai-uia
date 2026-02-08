
from automojo.arcli.model.groupingcommand import GroupingCommand
from automojo.uia.cli.cmdtree.mapping.monitor import MonitorCommand

class MappingCommand(GroupingCommand):
    
    def __init__(self):
        super().__init__("mapping", self.execute)
        self.add_command(MonitorCommand())

    def execute(self, context):
        pass
